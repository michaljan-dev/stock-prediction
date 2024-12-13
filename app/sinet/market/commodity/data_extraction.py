from app import db
from app.sinet.market.models import MarketCommodityDailyTrading
from app.sinet.market.utils import Spider
from app.sinet.market.api.tradingeconomics import Tradingeconomics
from celery.task import task
import time

#
# query{
#   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjQ=") {
#     result
#   }
# }
# CrontabSchedule:4 - commodity data


# get commodity data
class CommoditySpider(Spider):
    def run(self):
        # init Tradingeconomics service
        api = Tradingeconomics()

        # commodity to extract
        keys = [
            {
                "k": "brentoil",
            },
            {
                "k": "wtioil",
            },
            {
                "k": "copper",
            },
            {
                "k": "gold",
            },
            {
                "k": "naturalgas",
            },
            {
                "k": "silver",
            },
            {
                "k": "steel",
            },
            {
                "k": "coal",
            },
        ]
        # define time range for data
        span = "3y"
        for key in keys:
            commodity_key = key["k"]
            # get currency data from service
            items = api.get_commodity_data(key=commodity_key, span=span)
            # save data in db
            self.save(items=items, commodity_key=commodity_key)
            time.sleep(5)

    def save(self, commodity_key, items):
        if items == []:
            return

        for item in items:
            exist_record = (
                db.session.query(MarketCommodityDailyTrading)
                .filter_by(market_commodity_id=commodity_key, date=item["date"])
                .first()
            )
            if bool(exist_record):
                print("exist")
                continue
            else:
                db.session.merge(
                    MarketCommodityDailyTrading(
                        market_commodity_id=commodity_key,
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
def commodity_daily_trading_spider_process(*args, **kwargs):
    print("run commodity_daily_trading_spider_process")
    try:
        spider = CommoditySpider()
        spider.run()
        return 200
    except Exception as e:
        return 400
