from app import db
from app.sinet.market.models import MarketEconomicIndicatorCountryData
from app.sinet.market.utils import Spider
from app.sinet.market.api.tradingeconomics import Tradingeconomics
from celery.task import task
from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
import time

#
# query{
#   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjY=") {
#     result
#   }
# }
# CrontabSchedule:6 - economic indicator country data


class EconomicIndicatorSpider(Spider):
    current_item = None

    def run(self):
        # init Tradingeconomics service
        api = Tradingeconomics()

        # economic country to extract
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
            {
                "k": "cn",
            },
            {
                "k": "jp",
            },
            {
                "k": "cz",
            },
            {
                "k": "in",
            },
            {
                "k": "ca",
            },
            {
                "k": "au",
            },
            {
                "k": "eu",
            },
        ]

        indicators = {
            "unemployment-rate",
            "inflation-cpi",
            "industrial-production",
            "interest-rate",
            "employment-change",
            "retail-sales-annual",
            "manufacturing-pmi",
            "gdp-growth-annual",
            "gdp-growth",
            "nationwide-housing-prices-yoy",
            "average-earnings-excluding-bonus",
            "current-account",
            "manufacturing-production",
            "industrial-production",
        }
        # how many days ago
        num_ago = 200

        date_ago = date.today() + relativedelta(days=-num_ago)

        # define time range for data
        for dt in rrule(DAILY, dtstart=date_ago, until=date.today()):

            start_date = dt.strftime("%Y-%m-%d")

            items = api.get_economic_indicators_data(start_date=start_date)

            for key in keys:
                market_country_id = key["k"]
                for market_economic_indicator_id in indicators:
                    item = items[market_country_id][market_economic_indicator_id]
                    item["date"] = start_date

                    # save data in db
                    if len(item["actual"]) or len(item["previous"]) > 0:
                        self.save(
                            item=item,
                            market_country_id=market_country_id,
                            market_economic_indicator_id=market_economic_indicator_id,
                        )
            time.sleep(5)

    def save(self, item, market_country_id, market_economic_indicator_id):

        if item:
            self.current_item = item
            exist_record = (
                db.session.query(MarketEconomicIndicatorCountryData)
                .filter_by(
                    market_country_id=market_country_id,
                    date=item["date"],
                    market_economic_indicator_id=market_economic_indicator_id,
                )
                .first()
            )
            if bool(exist_record):
                print("exist")
                return
            else:
                db.session.merge(
                    MarketEconomicIndicatorCountryData(
                        market_country_id=market_country_id,
                        market_economic_indicator_id=market_economic_indicator_id,
                        date=item["date"],
                        actual=self.to_float_old(item["actual"]),
                        previous=self.to_float_old(item["previous"]),
                        forecast=self.to_float_old(item["forecast"]),
                    )
                )
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    return


@task
def economic_indicator_daily_spider_process(*args, **kwargs):
    print("run economic_indicator_daily_spider_process")
    try:
        spider = EconomicIndicatorSpider()
        spider.run()
        return 200
    except Exception as e:
        print(spider.current_item)
        return 400
