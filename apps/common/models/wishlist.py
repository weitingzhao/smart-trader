from django.db import models
from apps.common.models import *

class WishlistPurposeChoices(models.TextChoices):
    NORMAL     = '0', 'Normal'
    SEPA          = '1', 'SEPA'
    EARNING    = '2', 'EARNING'


class Wishlist(models.Model):
    """
    This model is used to store the wishlist of stocks came from the screening strategy result
    """
    wishlist_id = models.AutoField(primary_key=True)
    # Fundamental
    symbol = models.ForeignKey(MarketSymbol, on_delete=models.DO_NOTHING)
    purpose = models.CharField(max_length=8, choices=WishlistPurposeChoices.choices, default=WishlistPurposeChoices.NORMAL, null=True, blank=True)
    add_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    pick_at = models.DateField(null=True, blank=True)  # Add pick_at field

    class Meta:
        db_table = 'wishlist'

    def __str__(self):
        return f"Wishlist: {self.symbol} - {self.quantity} shares"

class Watchlist(models.Model):
    """
    This model is used to store the watchlist of stocks.
    """
    # ID
    watchlist_id = models.AutoField(primary_key=True)
    symbol = models.ForeignKey(MarketSymbol, on_delete=models.DO_NOTHING)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.DO_NOTHING)

    # Action
    target_buy_stop = models.DecimalField(max_digits=10, decimal_places=2)
    target_buy_limit = models.DecimalField(max_digits=10, decimal_places=2)
    target_sell_stop = models.DecimalField(max_digits=10, decimal_places=2)
    target_sell_limit = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    # Indicator
    actual_true_range = models.DecimalField(max_digits=10, decimal_places=2)
    bollinger_upper = models.DecimalField(max_digits=10, decimal_places=2)
    bollinger_lower = models.DecimalField(max_digits=10, decimal_places=2)
    bollinger_upper_lv2 = models.DecimalField(max_digits=10, decimal_places=2)
    bollinger_lower_lv2 = models.DecimalField(max_digits=10, decimal_places=2)
    bollinger_upper_lv3 = models.DecimalField(max_digits=10, decimal_places=2)
    bollinger_lower_lv3 = models.DecimalField(max_digits=10, decimal_places=2)
    rs_upper = models.DecimalField(max_digits=10, decimal_places=2)
    rs_lower = models.DecimalField(max_digits=10, decimal_places=2)
    rs_upper_lv2 = models.DecimalField(max_digits=10, decimal_places=2)
    rs_lower_lv2 = models.DecimalField(max_digits=10, decimal_places=2)

    # Tracking
    refresh_at = models.DateField(null=True, blank=True)
    order_at = models.DateField(null=True, blank=True)
    filled_at = models.DateField(null=True, blank=True)
    is_ordered = models.BooleanField(default=False)
    is_filled = models.BooleanField(default=False)

    class Meta:
        db_table = 'watchlist'

    def __str__(self):
        return f"Watchlist: {self.symbol} - {self.quantity} shares"