from django.db import connection
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_hypertable(sender, **kwargs):
    if sender.name != 'logic':
        return
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT create_hypertable('market_stock_hist_bars_ts', 'time', if_not_exists => TRUE);
        """)
