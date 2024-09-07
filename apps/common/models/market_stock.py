from django.db import models
from .market import MarketSymbol

class MarketStock(models.Model):
    symbol = models.OneToOneField(
        MarketSymbol,
        primary_key=True,
        related_name='stock',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    underlying_symbol = models.CharField(max_length=10, null=True, blank=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    long_name = models.CharField(max_length=200, null=True, blank=True)
    address1 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField()
    industry = models.CharField(max_length=100, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    long_business_summary = models.TextField(null=True, blank=True)
    full_time_employees = models.PositiveIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    financial_currency = models.CharField(max_length=10, null=True, blank=True)
    exchange = models.CharField(max_length=10, null=True, blank=True)
    quote_type = models.CharField(max_length=10, null=True, blank=True)
    time_zone_full_name = models.CharField(max_length=50, null=True, blank=True)
    time_zone_short_name = models.CharField(max_length=10, null=True, blank=True)
    gmt_offset_milliseconds = models.BigIntegerField(null=True, blank=True)
    uuid = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = 'market_stock'

    def __str__(self):
        return f"market.stock: {self.symbol}"

class MarketStockRiskMetrics(models.Model):
    symbol = models.OneToOneField(
        MarketSymbol,
        primary_key=True,
        related_name='stock_risk_metrics',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    audit_risk = models.PositiveIntegerField(null=True, blank=True)
    board_risk = models.PositiveIntegerField(null=True, blank=True)
    compensation_risk = models.PositiveIntegerField(null=True, blank=True)
    share_holder_rights_risk = models.PositiveIntegerField(null=True, blank=True)
    overall_risk = models.PositiveIntegerField(null=True, blank=True)
    governance_epoch_date = models.DateTimeField(null=True, blank=True)
    compensation_as_of_epoch_date = models.DateTimeField(null=True, blank=True)
    first_trade_date_epoch_utc = models.DateTimeField(null=True, blank=True)
    max_age = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'market_stock_risk_metrics'

    def __str__(self):
        return f"market.stock_risk_metrics: {self.symbol}"

class MarketStockDividend(models.Model):
    symbol = models.OneToOneField(
        MarketSymbol,
        primary_key=True,
        related_name='stock_dividend',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    dividend_rate = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    dividend_yield = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    ex_dividend_date = models.DateTimeField(null=True, blank=True)
    payout_ratio = models.DecimalField(max_digits=20, decimal_places=9, null=True, blank=True)
    five_year_avg_dividend_yield = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    trailing_annual_dividend_rate = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    trailing_annual_dividend_yield = models.DecimalField(max_digits=20, decimal_places=9, null=True, blank=True)

    class Meta:
        db_table = 'market_stock_dividend'

    def __str__(self):
        return f"market.stock_dividend: {self.symbol}"

class MarketStockPrice(models.Model):
    symbol = models.OneToOneField(
        MarketSymbol,
        primary_key=True,
        related_name='stock_price',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    price_hint = models.PositiveIntegerField(null=True, blank=True)
    previous_close = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    open_price = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    day_low = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    day_high = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    regular_market_previous_close = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    regular_market_open = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    regular_market_day_low = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    regular_market_day_high = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    current_price = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    bid = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    ask = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    bid_size = models.PositiveIntegerField(null=True, blank=True)
    ask_size = models.PositiveIntegerField(null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    regular_market_volume = models.BigIntegerField(null=True, blank=True)
    average_volume = models.BigIntegerField(null=True, blank=True)
    average_volume_10days = models.BigIntegerField(null=True, blank=True)
    average_daily_volume_10day = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'market_stock_price'

    def __str__(self):
        return f"market.stock_price: {self.symbol}"

class MarketStockValuation(models.Model):
    symbol = models.OneToOneField(
        MarketSymbol,
        primary_key=True,
        related_name='stock_valuation',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    market_cap = models.BigIntegerField(null=True, blank=True)
    beta = models.DecimalField(max_digits=20, decimal_places=7, null=True, blank=True)
    trailing_pe = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    forward_pe = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    price_to_sales_trailing_12_months = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    price_to_book = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    book_value = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    peg_ratio = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    trailing_peg_ratio = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    enterprise_value = models.BigIntegerField(null=True, blank=True)
    enterprise_to_revenue = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    enterprise_to_ebitda = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    trailing_eps = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    forward_eps = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)

    class Meta:
        db_table = 'market_stock_valuation'

    def __str__(self):
        return f"market.stock_valuation: {self.symbol}"

class MarketStockTarget(models.Model):
    symbol = models.OneToOneField(
        MarketSymbol,
        primary_key=True,
        related_name='stock_target',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    target_high_price = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    target_low_price = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    target_mean_price = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    target_median_price = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    recommendation_mean = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    recommendation_key = models.CharField(max_length=10, null=True, blank=True)
    number_of_analyst_opinions = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'market_stock_target'

    def __str__(self):
        return f"market.stock_target: {self.symbol}"

class MarketStockPerformance(models.Model):
    symbol = models.OneToOneField(
        MarketSymbol,
        primary_key=True,
        related_name='stock_performance',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    fifty_two_week_low = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    fifty_two_week_high = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    fifty_day_average = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    two_hundred_day_average = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    earnings_quarterly_growth = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    earnings_growth = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    revenue_growth = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    gross_margins = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    ebitda_margins = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    operating_margins = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    return_on_assets = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    return_on_equity = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    profit_margins = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)

    class Meta:
        db_table = 'market_stock_performance'

    def __str__(self):
        return f"market.stock_performance: {self.symbol}"

class MarketStockShare(models.Model):
    symbol = models.OneToOneField(
        MarketSymbol,
        primary_key=True,
        related_name='stock_share',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    float_shares = models.BigIntegerField(null=True, blank=True)
    shares_outstanding = models.BigIntegerField(null=True, blank=True)
    shares_short = models.BigIntegerField(null=True, blank=True)
    shares_short_prior_month = models.BigIntegerField(null=True, blank=True)
    shares_short_previous_month_date = models.DateTimeField(null=True, blank=True)
    date_short_interest = models.DateTimeField(null=True, blank=True)
    shares_percent_shares_out = models.DecimalField(max_digits=20, decimal_places=9, null=True, blank=True)
    held_percent_insiders = models.DecimalField(max_digits=20, decimal_places=9, null=True, blank=True)
    held_percent_institutions = models.DecimalField(max_digits=20, decimal_places=9, null=True, blank=True)
    short_ratio = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    short_percent_of_float = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)

    class Meta:
        db_table = 'market_stock_share'

    def __str__(self):
        return f"market.stock_share: {self.symbol}"

class MarketStockFinancial(models.Model):
    symbol = models.OneToOneField(
        MarketSymbol,
        primary_key=True,
        related_name='stock_financial',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    total_cash = models.BigIntegerField(null=True, blank=True)
    total_cash_per_share = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    ebitda = models.BigIntegerField(null=True, blank=True)
    total_debt = models.BigIntegerField(null=True, blank=True)
    quick_ratio = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    current_ratio = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    total_revenue = models.BigIntegerField(null=True, blank=True)
    debt_to_equity = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    revenue_per_share = models.DecimalField(max_digits=15, decimal_places=7, null=True, blank=True)
    net_income_to_common = models.BigIntegerField(null=True, blank=True)
    free_cashflow = models.BigIntegerField(null=True, blank=True)
    operating_cashflow = models.BigIntegerField(null=True, blank=True)
    last_fiscal_year_end = models.DateTimeField(null=True, blank=True)
    next_fiscal_year_end = models.DateTimeField(null=True, blank=True)
    most_recent_quarter = models.DateTimeField(null=True, blank=True)
    last_split_factor = models.CharField(max_length=10, null=True, blank=True)
    last_split_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'market_stock_financial'

    def __str__(self):
        return f"market.stock_financial: {self.symbol}"

class MarketCompanyOfficer(models.Model):
    symbol = models.ForeignKey(
        MarketSymbol,
        related_name='stock_company_officer',
        db_column='symbol',
        on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=100, null=False, blank=False)
    max_age = models.PositiveIntegerField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    year_born = models.PositiveIntegerField(null=True, blank=True)
    fiscal_year = models.PositiveIntegerField(null=True, blank=True)
    total_pay = models.BigIntegerField(null=True, blank=True)
    exercised_value = models.BigIntegerField(null=True, blank=True)
    unexercised_value = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'market_company_officer'
        unique_together = ('symbol', 'name')

    def __str__(self):
        return f"market.company_officer: {self.symbol} - {self.name}"