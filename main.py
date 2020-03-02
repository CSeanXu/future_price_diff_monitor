import argparse
import asyncio
import logging
import sys
import time
from threading import Lock

from prometheus_client import start_http_server, Metric, REGISTRY

# lock of the collect method
from consts import MarketType
from crawler import get_contract_bbo, get_spot_bbo

lock = Lock()

loop = asyncio.get_event_loop()

# logging setup
log = logging.getLogger('coinmarketcap-exporter')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


class CoinClient(object):
    def __init__(self):
        self.currency = "BTC"

    async def crawl(self):
        currency = self.currency

        tasks = [
            get_contract_bbo(currency, MarketType.FUTURE_CURRENT_WEEK),
            get_contract_bbo(currency, MarketType.FUTURE_NEXT_WEEK),
            get_contract_bbo(currency, MarketType.FUTURE_CURRENT_QUOTER),
            get_spot_bbo(currency)
        ]

        result = await asyncio.gather(*tasks)

        _result = {}

        spot_price_key = f"{currency}_{MarketType.SPOT.value}_Price"

        for r in result:
            price_key = f"{r.currency}_{r.contract_type.value}_Price"
            val = r.avg_bbo_price
            _result[price_key] = val

        spot_price = _result[spot_price_key]

        tmp_dict = {}

        for k, v in _result.items():
            price_diff_key = f"{k}_DF"
            val = (v - spot_price) / spot_price * 100
            tmp_dict[price_diff_key] = val

        _result.update(tmp_dict)

        return _result

    def tickers(self):
        holder = {"result": None}  # mutable

        async def _hack():
            _result = await self.crawl()
            holder["result"] = _result

        loop.run_until_complete(_hack())

        log.info(holder["result"])

        return holder["result"]


class CoinCollector(object):
    def __init__(self):
        self.client = CoinClient()

    def collect(self):
        with lock:
            log.info('collecting...')

            response = self.client.tickers()

            metric = Metric('market', 'crypto currency market metric values', 'gauge')

            print(response)

            # tick = response["tick"]
            #
            # best_buy_price = tick["bids"][0][0]
            # best_sell_price = tick["asks"][0][0]
            #

            for k, v in response.items():
                metric.add_sample(k, value=v, labels={
                    "currency": "bitcoin",
                })

            # metric.add_sample(
            #     "bitcoin_market",
            #     value=sum([best_buy_price, best_sell_price]) / 2.0,
            #     labels={
            #         "currency": "bitcoin",
            #         "type": "spot",
            #         "id": "bitcoin",
            #     })

            yield metric


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--port', nargs='?', const=9101, help='The TCP port to listen on', default=9101)
        parser.add_argument('--addr', nargs='?', const='0.0.0.0', help='The interface to bind to', default='0.0.0.0')
        args = parser.parse_args()
        log.info('listening on http://%s:%d/metrics' % (args.addr, args.port))

        REGISTRY.register(CoinCollector())
        start_http_server(int(args.port), addr=args.addr)

        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(" Interrupted")
        exit(0)
