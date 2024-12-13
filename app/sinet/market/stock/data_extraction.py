from app import db
from app.sinet.market.models import MarketStockIndexDailyTrading
from app.sinet.market.utils import Spider
from app.sinet.market.api.tradingeconomics import Tradingeconomics
from celery.task import task
import time

#
# query{
#   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjc=") {
#     result
#   }
# }
# CrontabSchedule:7 - stock index data


# get stock index data
class StockIndexSpider(Spider):
    def run(self):
        # init Tradingeconomics service
        api = Tradingeconomics()

        # stock index
        keys = [
            {
                "k": "wig",
            },
            {
                "k": "dax",
            },
            {
                "k": "cac40",
            },
            {
                "k": "ftsemib",
            },
            {
                "k": "ftse100",
            },
            {
                "k": "dji",
            },
        ]
        # define time range for data
        span = "1y"
        for key in keys:
            index_key = key["k"]
            # get stock index data from service
            items = api.get_stock_index_data(key=index_key, span=span)
            # save data in db
            self.save(items=items, index_key=index_key)
            time.sleep(5)

    def save(self, index_key, items):
        if items == []:
            return

        for item in items:
            exist_record = (
                db.session.query(MarketStockIndexDailyTrading)
                .filter_by(market_stock_index_id=index_key, date=item["date"])
                .first()
            )
            if bool(exist_record):
                print("exist")
                continue
            else:
                db.session.merge(
                    MarketStockIndexDailyTrading(
                        market_stock_index_id=index_key,
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
def stock_index_daily_trading_spider_process(*args, **kwargs):
    print("run stock_index_daily_trading_spider_process")
    try:
        spider = StockIndexSpider()
        spider.run()
        return 200
    except Exception as e:
        print(e)
        return 400
