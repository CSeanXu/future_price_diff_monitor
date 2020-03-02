import aiohttp

from abstraction import BBO
from consts import MarketType


async def get_contract_bbo(currency, contract_type: MarketType):
    symbol = f"{currency}_{contract_type.value}"

    url = f"https://api.hbdm.com/market/detail/merged?symbol={symbol}"
    # trust_env: using system proxy if any
    async with aiohttp.ClientSession(trust_env=True, timeout=aiohttp.ClientTimeout(total=5)) as session:
        async with session.get(url) as resp:
            j = await resp.json(content_type=None)
            tick = j["tick"]
            best_buy_price = tick["bid"][0]
            best_sell_price = tick["ask"][0]
            bbo = BBO(currency, contract_type, best_buy_price, best_sell_price)
            return bbo


async def get_spot_bbo(currency):

    symbol = f"{currency.lower()}usdt"

    url = f"https://api.huobi.io/market/depth?symbol={symbol}&type=step0"  # no aggregation!

    # trust_env: using system proxy if any
    async with aiohttp.ClientSession(trust_env=True, timeout=aiohttp.ClientTimeout(total=5)) as session:
        async with session.get(url) as resp:
            j = await resp.json(content_type=None)
            tick = j["tick"]
            best_buy_price = tick["bids"][0][0]
            best_sell_price = tick["asks"][0][0]
            bbo = BBO(currency, MarketType.SPOT, best_buy_price, best_sell_price)
            return bbo
