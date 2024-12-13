from app import db
from app.sinet.market.models import MarketCurrencyForeignExchangeDailyRate
from app.sinet.market.utils import Spider
from app.sinet.market.api.tradingeconomics import Tradingeconomics
from celery.task import task
import time

#
# query{
#   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjM=") {
#     result
#   }
# }
# CrontabSchedule:3 - currency data


# get currency data
class CurrencySpider(Spider):
    def run(self):
        # init Tradingeconomics service
        api = Tradingeconomics()

        # currency pairs to extract
        keys = [
            {
                "k": "eur-pln",
            },
            {
                "k": "usd-pln",
            },
            {
                "k": "gbp-pln",
            },
        ]
        # define time range for data
        span = "3y"
        for key in keys:
            pair_key = key["k"]
            # get currency data from service
            items = api.get_currency_data(key=pair_key, span=span)
            # save data in db
            self.save(items=items, pair_key=pair_key)
            time.sleep(5)

    def save(self, pair_key, items):
        if items == []:
            return

        for item in items:
            exist_record = (
                db.session.query(MarketCurrencyForeignExchangeDailyRate)
                .filter_by(
                    market_currency_foreign_exchange_pair_id=pair_key, date=item["date"]
                )
                .first()
            )
            if bool(exist_record):
                print("exist")
                continue
            else:
                db.session.merge(
                    MarketCurrencyForeignExchangeDailyRate(
                        market_currency_foreign_exchange_pair_id=pair_key,
                        date=item["date"],
                        open=self.to_float(item["open"]),
                        high=self.to_float(item["high"]),
                        low=self.to_float(item["low"]),
                        close=self.to_float(item["close"]),
                    )
                )
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    continue


@task
def currency_daily_trading_spider_process(*args, **kwargs):
    print("run currency_daily_trading_spider_process")
    try:
        spider = CurrencySpider()
        spider.run()
        return 200
    except Exception:
        return 400
