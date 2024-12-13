import dateutil.parser as dateparser
from io import StringIO
from lxml import etree
import random
import requests
from requests_html import HTMLSession
import re


class Tradingeconomics:

    base_url = "https://tradingeconomics.com/"
    data_chart_url = "https://markets.tradingeconomics.com/chart"

    def __init__(self):
        self.data_calendar_url = self.base_url + "calendar"

        self.headers = {
            "authority": "tradingeconomics.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "origin": self.base_url,
            "cache-control": "no-cache",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": self.base_url,
            "accept-language": "en-US,en;q=0.9",
        }

    def get_auth_code(self, url_auth):
        # code is part of the js declaration
        url = self.base_url + url_auth
        session = HTMLSession()
        r = session.get(url, headers=self.headers)
        # Extract TESecurify value using regular expression
        authMatch = re.search(r"TESecurify\s*=\s*['\"]([^'\"]+)['\"]", r.text)
        if authMatch:
            auth = authMatch.group(1)
        else:
            raise ValueError("TESecurify auth value is empty")
        return auth

    def get_data(self, url_auth, url, s, span):
        # it's required to get auth code for call
        auth = self.get_auth_code(url_auth=url_auth)
        params = {
            "s": s,
            "span": span,
            "securify": "new",
            "url": url,
            "AUTH": auth,
            "ohlc": random.randint(10**14, (10**15) - 1),
        }
        payload_params = "&".join("%s=%s" % (k, v) for k, v in params.items())

        r = requests.get(
            url=self.data_chart_url, headers=self.headers, params=payload_params
        )
        data = r.json()
        if len(data["series"][0]["data"]) <= 0:
            return False
        items = []
        # reformat currency data
        for item in data["series"][0]["data"]:
            # convert to date db format
            date = dateparser.parse(item["date"]).strftime("%Y-%m-%d 00:00:00")
            v = {
                "date": date,
                "open": item["open"],
                "high": item["high"],
                "low": item["low"],
                "close": item["close"],
                "name": data["series"][0]["shortname"],
            }
            items.append(v)

        return items

    def get_currency_data(self, key, span="5y"):

        # get mapping data for api call
        mapping = self.get_currency_data_mapping(key=key)
        s = mapping["s"]
        url = mapping["url_data"]
        url_auth = mapping["url_auth"]

        return self.get_data(url_auth, url=url, s=s, span=span)

    def get_currency_data_mapping(self, key):
        items = {
            "usd-pln": {
                "s": "usdpln:cur",
                "url_auth": "poland/currency",
                "url_data": "polandcurrency",
            },
            "eur-pln": {
                "s": "eurpln:cur",
                "url_auth": "poland/currency",
                "url_data": "polandcurrency",
            },
            "gbp-pln": {
                "s": "gbppln:cur",
                "url_auth": "poland/currency",
                "url_data": "polandcurrency",
            },
        }
        return items[key]

    def get_commodity_data(self, key, span="5y"):

        # get mapping data for api call
        mapping = self.get_commodity_data_mapping(key=key)

        url = mapping["url_data"]
        url_auth = mapping["url_auth"]
        s = mapping["s"]

        return self.get_data(url_auth, url=url, s=s, span=span)

    def get_commodity_data_mapping(self, key):
        items = {
            "copper": {
                "s": "hg1:com",
                "url_auth": "commodity/copper",
                "url_data": "commoditycopper",
            },
            "brentoil": {
                "s": "co1:com",
                "url_auth": "commodity/brent-crude-oil",
                "url_data": "commoditybrentcrudeoil",
            },
            "wtioil": {
                "s": "cl1:com",
                "url_auth": "commodity/crude-oil",
                "url_data": "commoditycrudeoil",
            },
            "gold": {
                "s": "xauusd:cur",
                "url_auth": "commodity/gold",
                "url_data": "commoditygold",
            },
            "silver": {
                "s": "xagusd:cur",
                "url_auth": "commodity/silver",
                "url_data": "commoditysilver",
            },
            "naturalgas": {
                "s": "ng1:com",
                "url_auth": "commodity/natural-gas",
                "url_data": "commoditynaturalgas",
            },
            "platinum": {
                "s": "xptusd:cur",
                "url_auth": "commodity/platinum",
                "url_data": "commodityplatinum",
            },
            "steel": {
                "s": "jbp:com",
                "url_auth": "commodity/steel",
                "url_data": "commoditysteel",
            },
            "coal": {
                "s": "xal1:com",
                "url_auth": "commodity/coal",
                "url_data": "commoditycoal",
            },
            "uranium": {
                "s": "uxa:com",
                "url_auth": "commodity/uranium",
                "url_data": "commodityuranium",
            },
            "molybden": {
                "s": "molybden:com",
                "url_auth": "commodity/molybden",
                "url_data": "commoditymolybden",
            },
        }
        return items[key]

    def get_bond_data(self, key, span="5y"):

        # get mapping data for api call
        mapping = self.get_bond_data_mapping(key=key)

        url = mapping["url_data"]
        url_auth = mapping["url_auth"]
        s = mapping["s"]

        return self.get_data(url_auth, url=url, s=s, span=span)

    def get_bond_data_mapping(self, key):
        items = {
            "pl": {
                "s": "pogb10yr:gov",
                "url_auth": "poland/government-bond-yield",
                "url_data": "polandgovernmentbondyield",
            },
            "de": {
                "s": "gdbr10:ind",
                "url_auth": "germany/government-bond-yield",
                "url_data": "germanygovernmentbondyield",
            },
            "fr": {
                "s": "gfrn10:ind",
                "url_auth": "france/government-bond-yield",
                "url_data": "francegovernmentbondyield",
            },
            "it": {
                "s": "gbtpgr10:ind",
                "url_auth": "italy/government-bond-yield",
                "url_data": "italygovernmentbondyield",
            },
            "uk": {
                "s": "gukg10:ind",
                "url_auth": "united-kingdom/government-bond-yield",
                "url_data": "unitedkingdomgovernmentbondyield",
            },
            "us": {
                "s": "usgg10yr:ind",
                "url_auth": "united-states/government-bond-yield",
                "url_data": "unitedstatesgovernmentbondyield",
            },
        }
        return items[key]

    def get_stock_index_data(self, key, span="5y"):

        # get mapping data for api call
        mapping = self.get_stock_index_data_mapping(key=key)
        s = mapping["s"]
        url = mapping["url_data"]
        url_auth = mapping["url_auth"]

        return self.get_data(url_auth, url=url, s=s, span=span)

    def get_stock_index_data_mapping(self, key):
        items = {
            "wig": {
                "s": "wig:ind",
                "url_auth": "poland/stock-market",
                "url_data": "polandstockmarket",
            },
            "dax": {
                "s": "dax:ind",
                "url_auth": "germany/stock-market",
                "url_data": "germanystockmarket",
            },
            "cac40": {
                "s": "cac:ind",
                "url_auth": "france/stock-market",
                "url_data": "francestockmarket",
            },
            "ftsemib": {
                "s": "ftsemib:ind",
                "url_auth": "italy/stock-market",
                "url_data": "italystockmarket",
            },
            "ftse100": {
                "s": "ukx:ind",
                "url_auth": "united-kingdom/stock-market",
                "url_data": "unitedkingdomstockmarket",
            },
            "dji": {
                "s": "indu:ind",
                "url_auth": "united-states/stock-market",
                "url_data": "unitedstatesstockmarket",
            },
        }
        return items[key]

    def get_economic_indicators_list(self):
        items = {
            "pl": "poland",
            "de": "germany",
            "fr": "france",
            "it": "italy",
            "uk": "united-kingdom",
            "us": "united-states",
            "cn": "china",
            "jp": "japan",
            "cz": "czech-republic",
            "in": "india",
            "ca": "canada",
            "au": "australia",
            "eu": "euro-area",
        }
        return items

    def get_economic_indicators_data(self, start_date="2021-02-23"):

        countries = self.get_economic_indicators_list()
        country_cookie = "emu,pol,deu,fra,ita,gbr,usa,chn,jpn,ind,cze,can,aus"

        cookie_date_range = start_date + "|" + start_date
        cookies = {
            "calendar-importance": "1",
            "calendar-countries": country_cookie,
            "cal-custom-range": cookie_date_range,
        }

        r = requests.post(
            url=self.data_calendar_url, headers=self.headers, cookies=cookies
        )

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
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(r.text), parser)
        output = {}

        for key, country in countries.items():
            output[key] = {}
            for indicator in indicators:
                output[key][indicator] = {}

                indicators_type = ["actual", "previous", "forecast"]
                for indicator_type in indicators_type:
                    output[key][indicator][indicator_type] = tree.xpath(
                        f"//table//tr[@data-url='/{country}/{indicator}']//*[@id='{indicator_type}']/text()"
                    )
                    # in case if there are multiple values try with data-symbol
                    if len(output[key][indicator][indicator_type]) > 1:
                        output[key][indicator][indicator_type] = tree.xpath(
                            f"//table//tr[@data-url='/{country}/{indicator}' and @data-symbol]//*[@id='{indicator_type}']/text()"
                        )

        return output
