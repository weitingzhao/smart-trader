from django.db import models
from apps.common.models import *
from apps.common.models.screening import Screening

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
    add_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    pick_at = models.DateField(null=True, blank=True)  # Add pick_at field
    ref_strategy = models.ForeignKey(Strategy, on_delete=models.SET_NULL, null=True, blank=True)  # New field
    ref_screening = models.ForeignKey(Screening, on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        db_table = 'wishlist'

    def __str__(self):
        return f"Wishlist: {self.symbol} - {self.quantity} shares"
