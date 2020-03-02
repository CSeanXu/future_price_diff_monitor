from enum import Enum


class MarketType(Enum):

    SPOT = "SPOT"

    FUTURE_CURRENT_WEEK = "CW"
    FUTURE_NEXT_WEEK = "NW"
    FUTURE_CURRENT_QUOTER = "CQ"
