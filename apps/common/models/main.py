from django.contrib.auth.models import User
from django.db import models


# class RefundedChoices(models.TextChoices):
#     YES = 'YES', 'Yes'
#     NO = 'NO', 'No'
#
#
# class CurrencyChoices(models.TextChoices):
#     USD = 'USD', 'USD'
#     EUR = 'EUR', 'EUR'

# class Sales(models.Model):
# 	ID = models.AutoField(primary_key=True)
# 	Product = models.TextField(blank=True, null=True)
# 	BuyerEmail = models.EmailField(blank=True, null=True)
# 	PurchaseDate = models.DateField(blank=True, null=True)
# 	Country = models.TextField(blank=True, null=True)
# 	Price = models.FloatField(blank=True, null=True)
# 	Refunded = models.CharField(max_length=20, choices=RefundedChoices.choices, default=RefundedChoices.NO)
# 	Currency = models.CharField(max_length=10, choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
# 	Quantity = models.IntegerField(blank=True, null=True)

class UserStaticSetting(models.Model):
    """
    This model is used to store the static setting for the system
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    capital = models.DecimalField(max_digits=15, decimal_places=2, default=10000)
    risk = models.DecimalField(max_digits=5, decimal_places=2, default=0.5)
    rounding = models.IntegerField(null=True, default=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expect_gain_risk_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=2)
    position_min = models.IntegerField(null=True, default=2)
    position_max = models.IntegerField(null=True, default=2)

    class Meta:
        db_table = 'user_static_setting'

    def __str__(self):
        return f"Position Sizing for {self.user.username}"


class UtilitiesLookup(models.Model):
    category = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    order = models.IntegerField(null=True, blank=True)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'utilities_lookup'
        indexes = [
            models.Index(fields=['category', 'type','key']),
        ]
        # Setting a composite primary key
        constraints = [
            models.UniqueConstraint(fields=['category', 'type', 'key'], name='utilities_lookup_category_type_key_pk'),
        ]

    def __str__(self):
        return f"{self.category} - {self.type} - {self.key} - {self.value}"

class UtilitiesFilter(models.Model):
    name = models.CharField(max_length=255)
    order = models.IntegerField(null=True, blank=True)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'utilities_filter'

    def __str__(self):
        return f"{self.name} - {self.key} - {self.value}"
