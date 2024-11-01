from django.db import models
from . import Wishlist
from .market import MarketSymbol


class ActionChoices(models.TextChoices):
    NONE                                          = '0', 'None'
    Active_BUY_Initial                       = '1', 'Active BUY Initial Position'
    Active_BUY_Additional               = '2', 'Active BUY Additional Position'
    Active_RAISE_Stop_Bar              = '11', 'Active RAISE Stop Bar'
    Active_LOWER_Stop_Bar            = '15', 'Active LOWER Stop Bar'
    Passive_SELL_on_Stop_PROFIT  = '21', 'Passive SELL on Stop PROFIT'
    Passive_SELL_on_Stop_LOST     = '25', 'Passive SELL on Stop LOST'
    Active_SELL_on_STOP_PROFIT  = '31', 'Active SELL on STOP PROFIT'
    Active_SELL_on_STOP_LOST     = '35', 'Active SELL on STOP LOST'


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
    is_applied = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = 'transaction'

    def __str__(self):
        return f"Transaction: {self.transaction_id} for {self.holding}"


class HoldingBuyOrder(models.Model):
    """
    This model is used to store the buy orders for a holding
    """
    holding_buy_order_id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.DO_NOTHING, null=True, blank=True)

    action = models.CharField(max_length=20, choices=ActionChoices.choices, default=ActionChoices.NONE, null=True)
    timing = models.CharField(max_length=20, choices=TimingChoices.choices, default=TimingChoices.NONE, null=True)
    order_place_date = models.DateTimeField(null=True, blank=True)

    quantity_target = models.IntegerField(null=True, blank=True)

    price_market = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    price_stop = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    price_limit = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)

    is_initial = models.BooleanField(default=False,null=True, blank=True)
    is_additional = models.BooleanField(default=False,null=True, blank=True)

    class Meta:
        db_table = 'holding_buy_order'

    def __str__(self):
        return f"Holding Buy Order: {self.holding_buy_order_id} for {self.holding}"


class HoldingSellOrder(models.Model):
    """
    This model is used to store the sell orders for a holding
    """
    holding_sell_order_id = models.AutoField(primary_key=True)
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)

    action = models.CharField(max_length=20, choices=ActionChoices.choices, default=ActionChoices.NONE)
    timing = models.CharField(max_length=20, choices=TimingChoices.choices, default=TimingChoices.NONE)
    order_place_date = models.DateTimeField(null=True, blank=True)

    quantity_target = models.IntegerField(null=True, blank=True)

    price_stop = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    price_limit = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)

    is_initial = models.BooleanField(default=False,null=True, blank=True)
    good_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'holding_sell_order'

    def __str__(self):
        return f"Holding Sell Order: {self.holding_sell_order_id} for {self.holding}"


