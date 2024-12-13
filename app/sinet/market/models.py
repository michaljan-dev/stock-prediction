from app import db
from app.sinet.core.models import SchedulerEntry, CrontabSchedule


# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)


class MarketCountry(db.Model):

    __tablename__ = "market_country"

    id = db.Column(db.String(5), primary_key=True)
    name = db.Column(db.String(225), nullable=False, unique=True)

    def __init__(self, id, name):
        self.id = id
        self.name = name


class MarketSector(db.Model):

    __tablename__ = "market_sector"

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(225), nullable=False, unique=True)

    def __init__(self, id, name):
        self.id = id
        self.name = name


class MarketStock(db.Model):

    __tablename__ = "market_stock"

    id = db.Column(db.String(25), primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    market_country_id = db.Column(
        db.String(10), db.ForeignKey("market_country.id"), nullable=False
    )

    def __init__(self, id, name, market_country_id):
        self.id = id
        self.name = name
        self.market_country_id = market_country_id


class MarketStockCompany(db.Model):

    __tablename__ = "market_stock_company"

    # isin number
    id = db.Column(db.String(20), primary_key=True)
    market_stock_id = db.Column(
        db.String(25), db.ForeignKey("market_stock.id"), nullable=True
    )
    name = db.Column(db.String(255), nullable=False, unique=True)
    symbol = db.Column(db.String(128), nullable=False)
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    def __init__(self, id, name, symbol, market_stock_id):
        self.id = id
        self.name = name
        self.symbol = symbol
        self.market_stock_id = market_stock_id


class MarketStockCompanySector(Base):

    __tablename__ = "market_stock_company_sector"

    market_stock_company_id = db.Column(
        db.String(20), db.ForeignKey("market_stock_company.id"), nullable=False
    )
    market_sector_id = db.Column(db.String(20), db.ForeignKey("market_sector.id"))

    def __init__(self, market_stock_company_id, market_sector_id):
        self.market_stock_company_id = market_stock_company_id
        self.market_sector_id = market_sector_id


class MarketStockCompanyDailyTrading(Base):

    __tablename__ = "market_stock_company_daily_trading"

    date = db.Column(db.DateTime, index=True)
    market_stock_company_id = db.Column(
        db.String(20), db.ForeignKey("market_stock_company.id"), nullable=False
    )
    open = db.Column(db.String(60), nullable=True)
    high = db.Column(db.String(60), nullable=True)
    low = db.Column(db.String(60), nullable=True)
    close = db.Column(db.String(60), nullable=True)
    adj_close = db.Column(db.String(60), nullable=True)
    volume = db.Column(db.String(60), nullable=True)
    transactions = db.Column(db.String(60), nullable=True)

    # New instance instantiation procedure
    def __init__(
        self,
        date,
        market_stock_company_id,
        open,
        high,
        low,
        close,
        adj_close,
        volume,
        transactions,
    ):

        self.date = date
        self.market_stock_company_id = market_stock_company_id
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.adj_close = adj_close
        self.volume = volume
        self.transactions = transactions


class MarketStockCompanyPrediction(Base):

    __tablename__ = "market_stock_company_prediction"

    market_stock_company_id = db.Column(
        db.String(20), db.ForeignKey("market_stock_company.id"), nullable=False
    )
    date_created = db.Column(db.DateTime)
    strategy_id = db.Column(
        db.String(25),
        db.ForeignKey("market_stock_company_prediction_strategy.id"),
        nullable=True,
    )

    def __init__(self, date_created, strategy_id, market_stock_company_id):
        self.market_stock_company_id = market_stock_company_id
        self.date_created = date_created
        self.strategy_id = strategy_id


class MarketStockCompanyPredictionStrategy(db.Model):

    __tablename__ = "market_stock_company_prediction_strategy"

    id = db.Column(db.String(25), primary_key=True)
    name = db.Column(db.String(255), nullable=True)

    def __init__(self, id, name):
        self.id = id
        self.name = name


class MarketStockCompanyDailyTradingPrediction(Base):

    __tablename__ = "market_stock_company_daily_trading_prediction"

    prediction_id = db.Column(
        db.Integer(),
        db.ForeignKey("market_stock_company_prediction.id"),
        nullable=False,
    )
    date = db.Column(db.DateTime, index=True)
    close = db.Column(db.String(60), nullable=True)

    def __init__(self, date, prediction_id, close):
        self.date = date
        self.prediction_id = prediction_id
        self.close = close


class MarketStockIndex(db.Model):

    __tablename__ = "market_stock_index"

    id = db.Column(db.String(20), primary_key=True)
    market_stock_id = db.Column(
        db.String(25), db.ForeignKey("market_stock.id"), nullable=True
    )
    name = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, id, name, market_stock_id):
        self.id = id
        self.name = name
        self.market_stock_id = market_stock_id


class MarketStockIndexDailyTrading(Base):

    __tablename__ = "market_stock_index_daily_trading"

    date = db.Column(db.DateTime, index=True)
    market_stock_index_id = db.Column(
        db.String(10), db.ForeignKey("market_stock_index.id"), nullable=False
    )
    open = db.Column(db.String(60), nullable=True)
    high = db.Column(db.String(60), nullable=True)
    low = db.Column(db.String(60), nullable=True)
    close = db.Column(db.String(60), nullable=True)

    def __init__(self, date, market_stock_index_id, open, high, low, close):

        self.date = date
        self.market_stock_index_id = market_stock_index_id
        self.open = open
        self.high = high
        self.low = low
        self.close = close


class MarketCurrencyForeignExchangePair(db.Model):

    __tablename__ = "market_currency_foreign_exchange_pair"

    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(255), nullable=True)

    def __init__(self, id, name):
        self.id = id
        self.name = name


class MarketCurrencyForeignExchangeDailyRate(Base):

    __tablename__ = "market_currency_foreign_exchange_daily_rate"

    date = db.Column(db.DateTime, index=True)
    market_currency_foreign_exchange_pair_id = db.Column(
        db.String(10),
        db.ForeignKey("market_currency_foreign_exchange_pair.id"),
        nullable=False,
    )
    open = db.Column(db.String(60), nullable=True)
    high = db.Column(db.String(60), nullable=True)
    low = db.Column(db.String(60), nullable=True)
    close = db.Column(db.String(60), nullable=True)

    def __init__(
        self, date, market_currency_foreign_exchange_pair_id, open, high, low, close
    ):

        self.date = date
        self.market_currency_foreign_exchange_pair_id = (
            market_currency_foreign_exchange_pair_id
        )
        self.open = open
        self.high = high
        self.low = low
        self.close = close


class MarketCommodity(db.Model):

    __tablename__ = "market_commodity"

    id = db.Column(db.String(25), primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class MarketBondDailyTrading(Base):

    __tablename__ = "market_bond_daily_trading"

    date = db.Column(db.DateTime, index=True)
    market_country_id = db.Column(
        db.String(10), db.ForeignKey("market_country.id"), nullable=False
    )
    market_bond_id = db.Column(db.String(10), nullable=False)
    open = db.Column(db.String(60), nullable=True)
    high = db.Column(db.String(60), nullable=True)
    low = db.Column(db.String(60), nullable=True)
    close = db.Column(db.String(60), nullable=True)

    # only 10years bond
    def __init__(self, date, market_country_id, market_bond_id, open, high, low, close):

        self.date = date
        self.market_country_id = market_country_id
        self.market_bond_id = market_bond_id
        self.open = open
        self.high = high
        self.low = low
        self.close = close


class MarketCommodityDailyTrading(Base):

    __tablename__ = "market_commodity_daily_trading"

    date = db.Column(db.DateTime, index=True)
    market_commodity_id = db.Column(
        db.String(10), db.ForeignKey("market_commodity.id"), nullable=False
    )
    open = db.Column(db.String(60), nullable=True)
    high = db.Column(db.String(60), nullable=True)
    low = db.Column(db.String(60), nullable=True)
    close = db.Column(db.String(60), nullable=True)

    # prices for comodity are in USD

    def __init__(self, date, market_commodity_id, open, high, low, close):

        self.date = date
        self.market_commodity_id = market_commodity_id
        self.open = open
        self.high = high
        self.low = low
        self.close = close


class MarketEconomicIndicator(db.Model):

    __tablename__ = "market_economic_indicator"

    id = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class MarketEconomicIndicatorCountryData(Base):

    __tablename__ = "market_economic_indicator_country_data"

    date = db.Column(db.DateTime, index=True)
    market_country_id = db.Column(
        db.String(10), db.ForeignKey("market_country.id"), nullable=False
    )
    market_economic_indicator_id = db.Column(
        db.String(40), db.ForeignKey("market_economic_indicator.id"), nullable=False
    )
    actual = db.Column(db.String(25), nullable=True)
    previous = db.Column(db.String(25), nullable=True)
    forecast = db.Column(db.String(25), nullable=True)

    def __init__(
        self,
        date,
        market_country_id,
        market_economic_indicator_id,
        actual,
        previous,
        forecast,
    ):

        self.date = date
        self.market_country_id = market_country_id
        self.market_economic_indicator_id = market_economic_indicator_id
        self.actual = actual
        self.previous = previous
        self.forecast = forecast


@db.event.listens_for(MarketCountry.__table__, "after_create")
def MarketCountry_after_create(*args, **kwargs):
    db.session.add(MarketCountry(id="au", name="Australia"))
    db.session.add(MarketCountry(id="at", name="Austria"))
    db.session.add(MarketCountry(id="ca", name="Canada"))
    db.session.add(MarketCountry(id="cn", name="China"))
    db.session.add(MarketCountry(id="cz", name="Czech Republic"))
    db.session.add(MarketCountry(id="fr", name="France"))
    db.session.add(MarketCountry(id="de", name="Germany"))
    db.session.add(MarketCountry(id="nl", name="Holland"))
    db.session.add(MarketCountry(id="hu", name="Hungary"))
    db.session.add(MarketCountry(id="it", name="Italy"))
    db.session.add(MarketCountry(id="jp", name="Japan"))
    db.session.add(MarketCountry(id="pl", name="Poland"))
    db.session.add(MarketCountry(id="ru", name="Russia"))
    db.session.add(MarketCountry(id="es", name="Spain"))
    db.session.add(MarketCountry(id="uk", name="United Kingdom"))
    db.session.add(MarketCountry(id="us", name="USA"))
    db.session.add(MarketCountry(id="in", name="India"))
    db.session.add(MarketCountry(id="eu", name="European Union"))
    db.session.commit()


@db.event.listens_for(MarketCurrencyForeignExchangePair.__table__, "after_create")
def MarketCurrencyForeignExchangePair_after_create(*args, **kwargs):
    db.session.add(MarketCurrencyForeignExchangePair(id="usd-pln", name="USD to PLN"))
    db.session.add(MarketCurrencyForeignExchangePair(id="eur-pln", name="EUR to PLN"))
    db.session.add(MarketCurrencyForeignExchangePair(id="gbp-pln", name="GBP to PLN"))
    db.session.commit()


@db.event.listens_for(MarketCommodity.__table__, "after_create")
def MarketCommodity_after_create(*args, **kwargs):
    db.session.add(
        MarketCommodity(id="gold", name="Gold", description="Precious metal")
    )
    db.session.add(
        MarketCommodity(id="molybden", name="Molybdenum", description="Precious metal")
    )
    db.session.add(
        MarketCommodity(id="platinum", name="Platinum", description="Precious metal")
    )
    db.session.add(
        MarketCommodity(id="silver", name="Silver", description="Precious metal")
    )
    db.session.add(
        MarketCommodity(id="brentoil", name="Brent oil", description="Energy")
    )
    db.session.add(MarketCommodity(id="wtioil", name="Wti oil", description="Energy"))
    db.session.add(MarketCommodity(id="coal", name="Coal", description="Energy"))
    db.session.add(
        MarketCommodity(id="naturalgas", name="Natural Gas", description="Energy")
    )
    db.session.add(MarketCommodity(id="steel", name="Steel", description="Industrial"))

    db.session.add(
        MarketCommodity(id="copper", name="Copper", description="Industrial metal")
    )

    db.session.commit()


@db.event.listens_for(MarketStock.__table__, "after_create")
def MarketStock_after_create(*args, **kwargs):
    db.session.add(
        MarketStock(id="gpw", market_country_id="pl", name="Warsaw Stock Exchange")
    )
    db.session.add(
        MarketStock(id="fsx", market_country_id="de", name="Frankfurt Stock Exchange")
    )
    db.session.add(
        MarketStock(id="xpar", market_country_id="fr", name="Euronext Paris Exchange")
    )
    db.session.add(
        MarketStock(id="mta", market_country_id="it", name="Italian Stock Exchange")
    )
    db.session.add(
        MarketStock(id="xams", market_country_id="nl", name="Amsterdam Stock Exchange")
    )
    db.session.add(
        MarketStock(id="vse", market_country_id="at", name="Vienna Stock Exchange")
    )
    db.session.add(
        MarketStock(id="lse", market_country_id="uk", name="London Stock Exchange")
    )
    db.session.add(
        MarketStock(id="nyse", market_country_id="us", name="New York Stock Exchange")
    )

    db.session.add(
        MarketStock(id="jpx", market_country_id="jp", name="Tokyo Stock Exchange")
    )
    db.session.commit()


@db.event.listens_for(MarketStockCompanyPredictionStrategy.__table__, "after_create")
def MarketStockCompanyPredictionStrategy_after_create(*args, **kwargs):
    db.session.add(MarketStockCompanyPredictionStrategy(id="lstm1", name="Lstm1"))
    db.session.commit()


@db.event.listens_for(MarketSector.__table__, "after_create")
def MarketSector_after_create(*args, **kwargs):
    db.session.add(MarketSector(id="bank", name="Banks"))
    db.session.add(MarketSector(id="logistic", name="Logistic"))
    db.session.add(MarketSector(id="game", name="Games"))
    db.session.add(MarketSector(id="it", name="It"))
    db.session.add(MarketSector(id="media", name="Media"))
    db.session.add(MarketSector(id="telecommunication", name="Telecommunication"))
    db.session.add(MarketSector(id="energy", name="Energy"))
    db.session.add(MarketSector(id="construction", name="Construction"))
    db.session.add(MarketSector(id="construction-mat", name="Building Materials"))
    db.session.add(MarketSector(id="com-coal", name="Commodities coal"))
    db.session.add(MarketSector(id="com-metal", name="Commodities metals"))
    db.session.add(MarketSector(id="com-petroleum", name="Commodities petroleum"))
    db.session.add(MarketSector(id="biotechnology", name="Biotechnology"))

    db.session.commit()


@db.event.listens_for(MarketEconomicIndicator.__table__, "after_create")
def MarketEconomicIndicator_after_create(*args, **kwargs):
    db.session.add(
        MarketEconomicIndicator(
            id="inflation-cpi", name="Inflation Rate YoY", description=""
        )
    )
    db.session.add(
        MarketEconomicIndicator(
            id="industrial-production", name="Industrial Production YoY", description=""
        )
    )
    db.session.add(
        MarketEconomicIndicator(
            id="interest-rate", name="Interest Rate Decision", description=""
        )
    )
    db.session.add(
        MarketEconomicIndicator(
            id="unemployment-rate", name="Unemployment Rate", description=""
        )
    )
    db.session.add(
        MarketEconomicIndicator(
            id="employment-change", name="Employment Growth YoY", description=""
        )
    )
    db.session.add(
        MarketEconomicIndicator(
            id="retail-sales-annual", name="Retail Sales YoY", description=""
        )
    )
    db.session.add(
        MarketEconomicIndicator(
            id="manufacturing-pmi", name="	Markit Manufacturing PMI", description=""
        )
    )
    db.session.add(
        MarketEconomicIndicator(
            id="gdp-growth-annual", name="GDP Growth Rate YoY Final", description=""
        )
    )
    db.session.add(
        MarketEconomicIndicator(
            id="gdp-growth", name="GDP Growth Rate QoQ Adv", description=""
        )
    )
    db.session.add(
        MarketEconomicIndicator(
            id="average-earnings-excluding-bonus",
            name="Average Earnings excl. Bonus",
            description="",
        )
    )
    db.session.commit()


@db.event.listens_for(MarketStockIndex.__table__, "after_create")
def MarketStockIndex_after_create(*args, **kwargs):
    db.session.add(MarketStockIndex(id="wig", market_stock_id="gpw", name="WIG"))
    db.session.add(MarketStockIndex(id="dax", market_stock_id="fsx", name="DAX"))
    db.session.add(MarketStockIndex(id="cac40", market_stock_id="xpar", name="CAC 40"))
    db.session.add(
        MarketStockIndex(id="ftsemib", market_stock_id="mta", name="FTSE MIB")
    )
    db.session.add(
        MarketStockIndex(id="ftse100", market_stock_id="lse", name="FTSE 100")
    )
    db.session.add(
        MarketStockIndex(id="nikkei225", market_stock_id="jpx", name="Nikkei 225")
    )
    db.session.add(MarketStockIndex(id="nasdaq", market_stock_id="nyse", name="Nasdaq"))
    db.session.add(
        MarketStockIndex(id="dji", market_stock_id="nyse", name="Dow Jones Industrial")
    )
    db.session.commit()


@db.event.listens_for(SchedulerEntry.__table__, "after_create")
def SchedulerEntry_after_create(*args, **kwargs):

    crontab_company_spider = CrontabSchedule(
        minute="0", hour="0", day_of_week="1", day_of_month="1", month_of_year="*"
    )
    db.session.add(crontab_company_spider)
    db.session.add(
        SchedulerEntry(
            crontab=crontab_company_spider,
            name="GPW Market Company Spider",
            task="app.sinet.market.stock.gpw.data_extraction.company_spider_process",
            enabled=False,
        )
    )

    crontab_daily_spider = CrontabSchedule(
        minute="0", hour="20", day_of_week="*", day_of_month="*", month_of_year="*"
    )
    db.session.add(crontab_daily_spider)
    db.session.add(
        SchedulerEntry(
            crontab=crontab_daily_spider,
            name="GPW Market Company Daily Trading Spider",
            task="app.sinet.market.stock.gpw.data_extraction.company_daily_trading_spider_process",
            enabled=False,
        )
    )

    db.session.add(
        SchedulerEntry(
            crontab=crontab_daily_spider,
            name="Currency Daily Trading Spider",
            task="app.sinet.market.currency.data_extraction.currency_daily_trading_spider_process",
            enabled=False,
        )
    )
    db.session.add(
        SchedulerEntry(
            crontab=crontab_daily_spider,
            name="Commodity Daily Trading Spider",
            task="app.sinet.market.commodity.data_extraction.commodity_daily_trading_spider_process",
            enabled=False,
        )
    )
    db.session.add(
        SchedulerEntry(
            crontab=crontab_daily_spider,
            name="Bond Daily Trading Spider",
            task="app.sinet.market.bond.data_extraction.bond_daily_trading_spider_process",
            enabled=False,
        )
    )
    db.session.add(
        SchedulerEntry(
            crontab=crontab_daily_spider,
            name="Economic Indicator Daily Spider",
            task="app.sinet.market.economic_indicator.data_extraction.economic_indicator_daily_spider_process",
            enabled=False,
        )
    )

    db.session.add(
        SchedulerEntry(
            crontab=crontab_daily_spider,
            name="Stock Index Daily Trading Spider",
            task="app.sinet.market.stock.data_extraction.stock_index_daily_trading_spider_process",
            enabled=False,
        )
    )
    db.session.commit()


class AggregatedMarketStock(db.Model):

    __tablename__ = "aggregated_market_stock"
    date = db.Column(db.Date, primary_key=True)
