import backtrader as bt
import threading
import datetime

from cerebro.strategy.three_step_strategy import ThreeStepStrategy


class LiveStrategy(ThreeStepStrategy):
    params = (
        ('order_valid', 30),  # 订单有效期（秒）
        ('price_deviation', 0.01),  # 允许的价格偏离
    )

    def __init__(self):
        super().__init__()
        self.live_data = False
        self.orders = dict()

    def notify_data(self, data, status, *args, **kwargs):
        if status == data.LIVE:
            self.live_data = True

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.record_trade(order)

    def record_trade(self, order):
        # 记录交易到数据库或文件
        trade = {
            'datetime': self.datetime.datetime(),
            'symbol': order.data._name,
            'size': order.size,
            'price': order.executed.price,
            'commission': order.executed.comm
        }
        print(f"TRADE RECORDED: {trade}")

    def next(self):
        if not self.live_data:
            return
        super().next()
        # 检查现有订单状态
        self.check_pending_orders()

    def check_pending_orders(self):
        for oid, order in list(self.orders.items()):
            if order.status in [order.Expired, order.Canceled]:
                self.cancel(order)
                del self.orders[oid]

    def execute_entry(self, trend_type):
        size = self.broker.getcash() * 0.98 / self.hourly.close[0]
        price = self.get_entry_price(trend_type)

        order = self.buy_bracket(
            price=price,
            size=size,
            stopprice=self.stop_loss,
            limitprice=self.take_profit,
            exectype=bt.Order.StopLimit,
            valid=datetime.timedelta(seconds=self.p.order_valid))

        self.orders[order[0].ref] = order[0]

    def get_entry_price(self, trend_type):
        # 获取实时报价
        last = self.hourly.close[0]
        bid = self.hourly.bid[0]
        ask = self.hourly.ask[0]

        if trend_type == 'breakout':
            return min(last + 0.01, ask)
        elif trend_type == 'reversal':
            return max(last - 0.01, bid)
        else:
            return (bid + ask) / 2