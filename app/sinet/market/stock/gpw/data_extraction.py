from app import db
from app.sinet.market.utils import Spider
from app.sinet.market.models import (
    MarketStockCompany,
    MarketStockCompanySector,
    MarketStockCompanyDailyTrading,
)
from celery.task import task
from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
import time
from requests_html import HTMLSession

#
# query{
#   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjE=") {
#     result
#   }
# }
# CrontabSchedule:2 - company data
# Q3JvbnRhYlNjaGVkdWxlOjE=
# CrontabSchedule:2 - daily trading
# Q3JvbnRhYlNjaGVkdWxlOjI=
market_stock_id = "gpw"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "SESSIONID=tbq0tn9oitm3nv7i0dchh83376; lang_code=PL; SID=!1UdmeRJDKFBR94xvrsvAraJ4wYgoXpNlc4KmCRhy06B2Mmu8YD/rL7tL4kWng+Hlu1lu3OerN3xlENIOeuNEiWOATrxBbMsFqWrdDemSKoViv7QSGhT8eBunQfxHn/KLufDoCwTPcYiNtyGBPnQ/pxSgDBkC+co=; TS01816045=016c1ed7ffda471e92e5da2c214dee78b898d713d067cece30d9b5ecf2a76a7425d32cbc99f47ee0f1038409f81229df550cf7f1c9; TSdbf1746a027=08abecc6aeab20008b46ada548843a43ef3b19b6b9b81f07a3153f88a61ab375ceee115bff3f3b9f0808fea854113000c5a02d98a8721ce0bc35d99e390b071ee209ba1ee940447afdbc3fd55908a88bf2dc3934e5a5932f39c4ef1810bc79dd",
    "Host": "www.gpw.pl",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


# get company data
class CompanySpider(Spider):
    def run(self):
        self.process()
        self.save()

    def process(self):
        limit = 500
        url = "https://www.gpw.pl/spolki?offset=1&limit={}".format(limit)

        session = HTMLSession()
        r = session.get(url, headers=headers)
        # r.html.render()

        self.parse(r)

    def parse(self, response):
        rows = response.html.xpath('//*[@id="search-result"]/tr')
        if rows == []:
            return

        self.data = []
        record = {}
        for row in rows:
            sector = "".join(row.xpath("//td[1]/small/text()")).strip()
            first, *middle, last = sector.split("|")
            sector = self.sectorMapp(last.strip())
            record = {
                "symbol": "".join(
                    row.xpath(
                        '//*[contains(@class,"name")]/*[contains(@class,"grey")]/text()'
                    )
                )
                .strip()
                .replace("(", "")
                .replace(")", ""),
                "isin": "".join(row.xpath("//td[1]/a/@href")).replace(
                    "spolka?isin=", ""
                ),
                "name": "".join(
                    row.xpath('//*[contains(@class,"name")]/text()')
                ).strip(),
                "sector": sector,
            }
            self.data.append(record)

    def sectorMapp(self, sector_key):
        sectors = {
            "banki komercyjne": "bank",
            "gry": "game",
            "reklama i marketing": "media",
            "radio i telewizja": "media",
            "oprogramowanie": "it",
            "systemy informatyczne": "it",
            "inżynieria lądowa i wodna": "logistic",
            "Telekomunikacja": "telecommunication",
            "energetyka": "energy",
            "górnictwo węgla": "com-coal",
            "górnictwo metali": "com-metal",
            "wydobycie i produkcja": "com-petroleum",
            "budownictwo ogólne": "construction",
            "materiały budowlane": "construction-mat",
            "Biotechnologia": "biotechnology",
        }
        sector = sectors.get(sector_key)

        return sector

    def save(self):
        if self.data == []:
            return

        for row in self.data:
            exist_record = (
                db.session.query(MarketStockCompany).filter_by(id=row["isin"]).first()
            )
            if bool(exist_record):
                continue
            else:
                try:
                    db.session.merge(
                        MarketStockCompany(
                            name=row["name"],
                            symbol=row["symbol"],
                            id=row["isin"],
                            market_stock_id=market_stock_id,
                        )
                    )
                    db.session.merge(
                        MarketStockCompanySector(
                            market_stock_company_id=row["isin"],
                            market_sector_id=row["sector"],
                        )
                    )
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    continue


@task
def company_spider_process(*args, **kwargs):
    try:
        spider = CompanySpider()
        spider.run()
        return 200
    except Exception as e:
        print(e)
        return 400


# get company daily trading data
class CompanyDailyTradingSpider(Spider):
    def __init__(self, *args, **kwargs):
        self.start_extraction_data_date = "2023-12-05"

    def run(self):
        # num_ago =  33
        num_ago = 5
        date_ago = date.today() + relativedelta(months=-num_ago)

        for dt in rrule(DAILY, dtstart=date_ago, until=date.today()):
            week_no = dt.weekday()
            if week_no < 5:
                self.extraction_data_date = dt.strftime("%Y-%m-%d")
                self.process()
                self.save()
                time.sleep(5)

    def process(self):

        url = "https://www.gpw.pl/archiwum-notowan-full?type=10&instrument=&date={}".format(
            self.extraction_data_date
        )
        # print(url)
        session = HTMLSession()
        r = session.get(url, headers=headers)

        self.parse(r)

    def parse(self, response):
        rows = response.html.xpath('//table[contains(@class,"footable")]/tr')

        self.data = []

        if rows == []:
            return

        record = {}
        for row in rows:
            record = {
                "isin": "".join(row.xpath("//td[2]//text()")).strip(),
                "date": self.extraction_data_date,
                "open": "".join(row.xpath("//td[4]//text()")).strip(),
                "high": "".join(row.xpath("//td[5]//text()")).strip(),
                "low": "".join(row.xpath("//td[6]//text()")).strip(),
                "close": "".join(row.xpath("//td[7]//text()")).strip(),
                "adj_close": "",
                "volume": "".join(row.xpath("//td[9]//text()")).strip(),
                "transactions": "".join(row.xpath("//td[10]//text()")).strip(),
            }
            self.data.append(record)

    def save(self):
        if self.data == []:
            return

        for row in self.data:
            exist_record = (
                db.session.query(MarketStockCompanyDailyTrading)
                .filter_by(market_stock_company_id=row["isin"], date=row["date"])
                .first()
            )

            if bool(exist_record):
                print("exist")
                continue
            else:

                db.session.merge(
                    MarketStockCompanyDailyTrading(
                        date=row["date"],
                        market_stock_company_id=row["isin"],
                        open=self.to_float(row["open"]),
                        high=self.to_float(row["high"]),
                        low=self.to_float(row["low"]),
                        close=self.to_float(row["close"]),
                        adj_close=row["adj_close"],
                        transactions=self.to_float(row["transactions"]),
                        volume=self.to_float(row["volume"]),
                    )
                )
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    continue


@task
def company_daily_trading_spider_process(*args, **kwargs):
    try:
        spider = CompanyDailyTradingSpider()
        spider.run()
        return 200
    except Exception as e:
        print(e)
        return 400


# old to write
# get company news
class CompanyNewsSpider:
    def run(self):
        self.process()
        self.save()

    def process(self):
        limit = 500
        url = "https://www.bankier.pl/gielda/notowania/akcje/kania/wiadomosci/2={}".format(
            limit
        )

        session = HTMLSession()
        r = session.get(url)
        #         r.html.render()

        self.parse(r)

    def parse(self, response):
        rows = response.html.xpath('//*[@id="search-result"]/tr')
        if rows == []:
            return

        self.data = []
        record = {}
        for row in rows:
            sector = "".join(row.xpath("//td[1]/small/text()")).strip()
            first, *middle, last = sector.split("|")
            sector = self.sectorMapp(last.strip())
            record = {
                "symbol": "".join(
                    row.xpath(
                        '//*[contains(@class,"name")]/*[contains(@class,"grey")]/text()'
                    )
                )
                .strip()
                .replace("(", "")
                .replace(")", ""),
                "isin": "".join(row.xpath("//td[1]/a/@href")).replace(
                    "spolka?isin=", ""
                ),
                "name": "".join(
                    row.xpath('//*[contains(@class,"name")]/text()')
                ).strip(),
                "sector": sector,
            }
            self.data.append(record)

    def sectorMapp(self, sector_key):
        sectors = {
            "banki komercyjne": "bank",
            "gry": "game",
            "reklama i marketing": "media",
            "radio i telewizja": "media",
            "oprogramowanie": "it",
            "systemy informatyczne": "it",
            "inżynieria lądowa i wodna": "logistic",
        }
        sector = sectors.get(sector_key)

        return sector

    def save(self):
        if self.data == []:
            return

        for row in self.data:
            exist_record = (
                db.session.query(MarketStockCompany).filter_by(id=row["isin"]).first()
            )
            if bool(exist_record):
                continue
            else:
                try:
                    db.session.merge(
                        MarketStockCompany(
                            name=row["name"],
                            symbol=row["symbol"],
                            id=row["isin"],
                            market_stock_id=market_stock_id,
                        )
                    )
                    db.session.merge(
                        MarketStockCompanySector(
                            market_stock_company_id=row["isin"],
                            market_sector_id=row["sector"],
                        )
                    )
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    continue
