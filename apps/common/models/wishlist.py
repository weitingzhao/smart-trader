from django.db import models
from apps.common.models import *

class Wishlist(models.Model):
    """
    This model is used to store the wishlist of stocks came from the screening strategy result
    """
    wishlist_id = models.AutoField(primary_key=True)
    symbol = models.ForeignKey(MarketSymbol, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    target_buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    target_sell_stop = models.DecimalField(max_digits=10, decimal_places=2)
    target_sell_limit = models.DecimalField(max_digits=10, decimal_places=2)
    list_on = models.DateTimeField(null=True, blank=True)
    is_filled = models.BooleanField(default=False)
    action_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'wishlist'

    def __str__(self):
        return f"Wishlist: {self.symbol} - {self.quantity} shares"
