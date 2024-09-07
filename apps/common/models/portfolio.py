from email.policy import default

from celery.app import default_app
from django.contrib.auth.models import User
from django.db import models

from .market import MarketSymbol


class Portfolio(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolio'

    def __str__(self):
        return f"[{self.user.username}] Portfolio:{self.name}"


class PortfolioItem(models.Model):
    portfolio_item_id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    symbol = models.ForeignKey(MarketSymbol, on_delete=models.DO_NOTHING)
    quantity = models.FloatField(null=True)
    average_price = models.FloatField(null=True)

    class Meta:
        db_table = 'portfolio_item'
        unique_together = (('portfolio', 'symbol'),)

    def __str__(self):
        return f"{self.symbol} - {self.quantity} shares"


class Transaction(models.Model):
    portfolio_transaction_id = models.AutoField(primary_key=True)
    portfolio_item = models.ForeignKey(PortfolioItem, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('sell', 'Sell'),('sell Short', 'Buy'),('buy', 'Buy')])
    quantity = models.FloatField()
    price = models.FloatField()
    date = models.DateTimeField(null=True)
    commission = models.FloatField(null=True)
    notes = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'portfolio_transaction'

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} shares of {self.portfolio_item.symbol} at {self.price}"


class PortfolioPerformance(models.Model):
    portfolio_performance_id = models.AutoField(primary_key=True)
    portfolio_item = models.OneToOneField(PortfolioItem, on_delete=models.CASCADE)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    total_gain_loss = models.DecimalField(max_digits=15, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolio_performance'

    def __str__(self):
        return f"Performance for {self.portfolio.name}"



class PositionSizing(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    capital = models.DecimalField(max_digits=15, decimal_places=2, default=10000)
    risk = models.DecimalField(max_digits=5, decimal_places=2, default=0.5)
    rounding = models.IntegerField(null=True, default=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'position_sizing'

    def __str__(self):
        return f"Position Sizing for {self.user.username}"