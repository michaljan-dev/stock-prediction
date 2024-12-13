from app import db
from app.sinet.market.models import MarketBondDailyTrading
from app.sinet.market.utils import Spider
from app.sinet.market.api.tradingeconomics import Tradingeconomics
from celery.task import task
import time

#
# query{
#   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjU=") {
#     result
#   }
# }
# CrontabSchedule:5 - bond data


# get bond data - only 10 years
class BondSpider(Spider):

    current_item = None

    def run(self):
        # init Tradingeconomics service
        api = Tradingeconomics()

        # bond to extract
        keys = [
            {
                "k": "pl",
            },
            {
                "k": "de",
            },
            {
                "k": "fr",
            },
            {
                "k": "it",
            },
            {
                "k": "uk",
            },
            {
                "k": "us",
            },
        ]
        # define time range for data
        span = "3y"
        for key in keys:
            bond_key = key["k"]
            # get bond data from service
            items = api.get_bond_data(key=bond_key, span=span)
            # save data in db
            self.save(items=items, bond_key=bond_key)
            time.sleep(5)

    def save(self, bond_key, items):
        print(items)
        if items == []:
            return

        # static value only 10years
        market_bond_id = "10Y"

        for item in items:
            exist_record = (
                db.session.query(MarketBondDailyTrading)
                .filter_by(
                    market_country_id=bond_key,
                    date=item["date"],
                    market_bond_id=market_bond_id,
                )
                .first()
            )
            if bool(exist_record):
                print("exist")
                continue
            else:
                self.current_item = item
                db.session.merge(
                    MarketBondDailyTrading(
                        market_country_id=bond_key,
                        market_bond_id=market_bond_id,
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
def bond_daily_trading_spider_process(*args, **kwargs):
    print("run bond_daily_trading_spider_process")
    try:
        spider = BondSpider()
        spider.run()
        return 200
    except Exception as e:
        print(spider.current_item)
        print(e)
        return 400
