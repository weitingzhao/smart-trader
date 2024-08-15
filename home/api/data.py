


class RawStockDataHolder:
    def __init__(self, row):
        self.row = row

    def get_stock_id(self):
        return self.row[0]

    def get_date(self):
        return self.row[1]

    def get_open(self):
        return self.row[2]

    def get_high(self):
        return self.row[3]

    def get_low(self):
        return self.row[4]

    def get_close(self):
        return self.row[5]

    def get_adj_close(self):
        return self.row[6]

    def get_volume(self):
        return self.row[7]

    def get_dividend(self):
        return self.row[8]

    def get_split_coefficient(self):
        return self.row[9]

    def get_row(self):
        return self.row

    def __str__(self):
        return str(self.row)

    def __repr__(self):
        return str(self.row)


def initialize_data_holder(tickers: list, period_years: int, force_update: bool = False):
    pass