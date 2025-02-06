import backtrader as bt


class ThreeStepStrategy(bt.Strategy):
    params = (
        ('trend_period', 20),  # 趋势判定周期
        ('entry_period', 10),  # 入场均线周期
        ('atr_period', 14),  # ATR周期
        ('risk_ratio', 3),  # 风险回报比
    )

    def __init__(self):
        # 多时间框架数据准备
        self.daily = self.datas[0]
        self.hourly = self.datas[1]

        # 第一步：有序行为指标（日线级别）
        self.daily_sma = bt.indicators.SMA(self.daily.close, period=self.p.trend_period)
        self.daily_boll = bt.indicators.BollingerBands(self.daily.close, period=self.p.trend_period)
        self.daily_rsi = bt.indicators.RSI(self.daily.close, period=14)

        # 第二步：关键动作指标（小时线级别）
        self.hourly_ema = bt.indicators.EMA(self.hourly.close, period=self.p.entry_period)
        self.hourly_atr = bt.indicators.ATR(self.hourly, period=self.p.atr_period)

        # 第三步：入场信号指标
        self.crossover = bt.indicators.CrossOver(self.hourly.close, self.hourly_ema)

        self.trend_type = None  # 存储当前趋势类型
        self.entry_price = 0  # 入场价格
        self.stop_loss = 0  # 止损价格
        self.take_profit = 0  # 止盈价格

    def next(self):
        if not self.position:  # 未持仓时执行策略
            # 第一步：判断有序行为
            daily_condition = self.check_daily_trend()
            if daily_condition:
                # 第二步：验证关键动作
                hourly_condition = self.check_hourly_signal(daily_condition)
                if hourly_condition:
                    # 第三步：执行低成本入场
                    self.execute_entry(daily_condition)
        else:  # 持仓时监控退出条件
            self.monitor_exit()

    def check_daily_trend(self):
        # 判断日线级别趋势类型
        price_above_sma = self.daily.close[0] > self.daily_sma[0]
        price_in_upper = self.daily.close[0] > self.daily_boll.top[0]
        price_in_lower = self.daily.close[0] < self.daily_boll.bot[0]
        rsi_overbought = self.daily_rsi[0] > 70
        rsi_oversold = self.daily_rsi[0] < 30

        # 判断突破
        if price_above_sma and price_in_upper:
            return 'breakout'
        # 判断整理
        elif self.daily_boll.lines.top[0] - self.daily_boll.lines.bot[0] < \
                self.daily_boll.lines.top[-1] - self.daily_boll.lines.bot[-1]:
            return 'consolidation'
        # 判断反转
        elif (price_in_lower and rsi_oversold) or (price_in_upper and rsi_overbought):
            return 'reversal'
        return None

    def check_hourly_signal(self, trend_type):
        # 验证小时线级别信号
        if trend_type == 'breakout':
            return self.hourly.close[0] > self.hourly_ema[0] and \
                self.hourly.volume[0] > self.hourly.volume[-1] * 1.2
        elif trend_type == 'consolidation':
            return abs(self.hourly.close[0] - self.hourly.open[0]) < \
                self.hourly_atr[0] * 0.3  # 窄幅波动
        elif trend_type == 'reversal':
            return self.crossover[0] != 0  # 出现交叉信号
        return False

    def execute_entry(self, trend_type):
        # 执行入场逻辑
        size = self.broker.getcash() * 0.98 / self.hourly.close[0]

        # 根据趋势类型设置订单
        if trend_type == 'breakout':
            price = self.hourly.low[0] + self.hourly_atr[0] * 0.2
            self.stop_loss = self.hourly.low[0] - self.hourly_atr[0] * 0.5
            self.take_profit = price + (price - self.stop_loss) * self.p.risk_ratio
            self.buy_bracket(price=price, size=size,
                             stopprice=self.stop_loss,
                             limitprice=self.take_profit)

        elif trend_type == 'reversal':
            price = self.hourly.close[0]
            self.stop_loss = price - self.hourly_atr[0] * 1.5
            self.take_profit = price + (price - self.stop_loss) * self.p.risk_ratio
            self.buy_bracket(price=price, size=size,
                             stopprice=self.stop_loss,
                             limitprice=self.take_profit)

        elif trend_type == 'consolidation':
            price = (self.hourly.high[0] + self.hourly.low[0]) / 2
            self.stop_loss = self.hourly.low[0] - self.hourly_atr[0] * 0.3
            self.take_profit = self.hourly_boll.top[0]
            self.buy_bracket(price=price, size=size,
                             stopprice=self.stop_loss,
                             limitprice=self.take_profit)

    def monitor_exit(self):
        # 动态跟踪止损（示例）
        if self.position.size > 0:
            trail_price = self.hourly.close[0] - self.hourly_atr[0] * 0.5
            self.stop_loss = max(self.stop_loss, trail_price)

