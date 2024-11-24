from django.db import models
from . import Wishlist
from .market import MarketSymbol


class ActionChoices(models.TextChoices):
    NONE                                          = '0', 'None'
    Active_BUY_Initial                       = '1', 'Active BUY Initial Size'
    Active_BUY_Additional               = '2', 'Active BUY More Size'
    Active_RAISE_Stop_Bar              = '11', 'Active RAISE Stop Bar'
    Active_LOWER_Stop_Bar            = '15', 'Active LOWER Stop Bar'
    Passive_SELL_on_Stop_PROFIT  = '21', 'Passive STOP on Profit'
    Passive_SELL_on_Stop_LOST     = '25', 'Passive STOP get Lost'
    Active_SELL_on_STOP_PROFIT  = '31', 'Active STOP lock Profit'
    Active_SELL_on_STOP_LOST     = '35', 'Active STOP take Lost'


class TimingChoices(models.TextChoices):
    NONE                            = '0', 'None'
    DAY                              = '1', 'Day'
    Good_Till_Cancelled     = '2', 'Good Till Cancel'
    GTC_Extended_Hours  = '3', 'GTC Extended Hours'

class TransactionTypeChoices(models.TextChoices):
    NONE                            = '0', 'None'
    BUY                                 = '1', 'Buy'
    SELL                                = '2', 'Sell'
    DEPOSIT                         = '11', 'Deposit'
    WITHDRAW                     = '12', 'Withdraw'

class OrderTypeChoices(models.TextChoices):
    NONE =  '0', 'None'
    MARKET = '1', 'Market'
    LIMIT = '2', 'Limit'
    STOP = '3', 'Stop'
    STOP_LIMIT = '4', 'Stop Limit'

class FundingTypeChoices(models.TextChoices):
    NONE =  '0', 'None'
    WITHDRAW = '1', 'Withdraw'
    DEPOSIT = '2', 'Deposit'

class  TradePhaseChoices(models.TextChoices):
    NONE            =  '0', 'None' # None
    BEFORE_BO  = '1', 'Before Breakout' # Before Breakout
    BREAKING    = '2', 'Breaking Out' # Breaking Out
    AFTER_BO    = '3', 'After Breakout' # After Breakout

class Portfolio(models.Model):
    """
    This model is used to store the portfolio of stocks
    """
    portfolio_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    money_market = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    cash = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolio'

    def __str__(self):
        return f"[{self.user.username}] Portfolio:{self.name}"

class Funding(models.Model):
    """
    This model is used to store the funding of a portfolio
    """
    funding_id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    completion_date = models.DateTimeField(null=True, blank=True)
    funding_type = models.CharField(max_length=20, choices=FundingTypeChoices.choices, default=FundingTypeChoices.NONE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        db_table = 'funding'

    def __str__(self):
        return f"Funding: {self.funding_id} for {self.portfolio}"

class Holding(models.Model):
    """
    This model is used to store the holding of stocks in a portfolio
    """
    holding_id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    symbol = models.ForeignKey(MarketSymbol, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'holding'
        unique_together = (('portfolio', 'symbol'),)

    def __str__(self):
        return f"Holding: {self.portfolio} - {self.symbol}"

class Trade(models.Model):
    """
    This model is used to store trade information
    """
    trade_id = models.AutoField(primary_key=True)
    profit_actual = models.DecimalField(max_digits=15, decimal_places=2)
    profit_actual_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    is_finished = models.BooleanField(null=True, blank=True)
    trade_phase = models.CharField(max_length=20, choices=TradePhaseChoices.choices, default=TradePhaseChoices.NONE)

    class Meta:
        db_table = 'trade'

    def __str__(self):
        return f"Trade: {self.trade_id} - Profit: {self.profit_actual} - Ratio: {self.profit_actual_ratio}"

class CashBalance(models.Model):
    """
    This model is used to store the cash balance information
    """
    cash_balance_id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.DO_NOTHING, null=True, blank=True)
    money_market = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True)
    cash = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, null=True)
    as_of_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'cash_balance'

    def __str__(self):
        return f"CashBalance: {self.cash_balance_id} as of {self.as_of_date}"

class Transaction(models.Model):
    """
    This model is used to store the buy action of a holding
    """
    transaction_id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TransactionTypeChoices.choices, default=TransactionTypeChoices.NONE)
    date = models.DateTimeField(null=True, blank=True)
    quantity_final = models.IntegerField(null=True, blank=True)
    price_final = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    commission = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)

    buy_order = models.ForeignKey('HoldingBuyOrder', on_delete=models.SET_NULL, null=True, blank=True)
    sell_order = models.ForeignKey('HoldingSellOrder', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'transaction'

    def __str__(self):
        return f"Transaction: {self.transaction_id} for {self.holding}"

class HoldingOrder(models.Model):
    # id
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, null=True, blank=True)  # Add trade_id field

    # quantities & prices
    order_type = models.CharField(max_length=20, choices=OrderTypeChoices.choices, default=OrderTypeChoices.NONE, null=True, blank=True)  # Add order_type field

    quantity_target = models.IntegerField(null=True, blank=True)
    price_market = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    price_stop = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    price_limit = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)

    # category
    action = models.CharField(max_length=20, choices=ActionChoices.choices, default=ActionChoices.NONE)
    timing = models.CharField(max_length=20, choices=TimingChoices.choices, default=TimingChoices.NONE)

    class Meta:
        abstract = True

class HoldingBuyOrder(HoldingOrder):
    """
    This model is used to store the buy orders for a holding
    """
    holding_buy_order_id = models.AutoField(primary_key=True)
    ref_buy_order = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True)

    wishlist = models.ForeignKey(Wishlist, on_delete=models.DO_NOTHING, null=True, blank=True)

    class Meta:
        db_table = 'holding_buy_order'

    def __str__(self):
        return f"Holding Buy Order: {self.holding_buy_order_id} for {self.holding}"

class HoldingSellOrder(HoldingOrder):
    """
    This model is used to store the sell orders for a holding
    """
    holding_sell_order_id = models.AutoField(primary_key=True)
    ref_sell_order = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True)

    is_obsolete = models.BooleanField(default=False, null=True, blank=True)
    order_place_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'holding_sell_order'

    def __str__(self):
        return f"Holding Sell Order: {self.holding_sell_order_id} for {self.holding}"


