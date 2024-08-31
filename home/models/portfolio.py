from django.db import models

from home.models import MarketSymbol


class Portfolio(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolio'

    def __str__(self):
        return f"[{self.user.username}] Portfolio:{self.name}"


class PortfolioItem(models.Model):
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE)
    symbol = models.OneToOneField(MarketSymbol, on_delete=models.DO_NOTHING)
    quantity = models.FloatField()
    average_price = models.FloatField()

    class Meta:
        db_table = 'portfolio_item'

    def __str__(self):
        return f"{self.symbol} - {self.quantity} shares"


class Transaction(models.Model):
    portfolio_item = models.OneToOneField(PortfolioItem, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    quantity = models.FloatField()
    price = models.FloatField()
    date = models.DateTimeField()

    class Meta:
        db_table = 'portfolio_transaction'

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} shares of {self.portfolio_item.symbol} at {self.price}"


class PortfolioPerformance(models.Model):
    portfolio = models.OneToOneField(Portfolio, on_delete=models.CASCADE)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    total_gain_loss = models.DecimalField(max_digits=15, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolio_performance'

    def __str__(self):
        return f"Performance for {self.portfolio.name}"

