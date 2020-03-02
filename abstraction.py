from typing import Optional

from consts import MarketType


class BBO(object):

    def __init__(self, currency, contract_type: Optional[MarketType], best_buy_price, best_sell_price):
        self.currency = currency
        self.contract_type = contract_type
        self.best_buy_price = best_buy_price
        self.best_sell_price = best_sell_price

    @property
    def avg_bbo_price(self):
        return (self.best_buy_price + self.best_sell_price) / 2

    def __str__(self):
        return f"<BBO of {self.currency}({self.contract_type.value})>: {self.best_buy_price} VS {self.best_sell_price}"
