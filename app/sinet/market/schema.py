from app.sinet.core.utils import (
    ExtendedSQLAlchemyObjectType,
    ExtendedSQLAlchemyConnectionField,
)
import graphene
from graphene import relay
from .models import (
    MarketSector as MarketSectorModel,
    MarketStock as MarketStockModel,
    MarketStockCompany as MarketStockCompanyModel,
    MarketStockCompanyDailyTrading as MarketStockCompanyDailyTradingModel,
    MarketStockCompanyPrediction as MarketStockCompanyPredictionModel,
    MarketStockCompanyDailyTradingPrediction as MarketStockCompanyDailyTradingPredictionModel,
)


class MarketSector(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = MarketSectorModel
        interfaces = (relay.Node,)


class MarketSectorConnection(relay.Connection):
    class Meta:
        node = MarketSector


class MarketStock(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = MarketStockModel
        interfaces = (relay.Node,)


class MarketStockConnection(relay.Connection):
    class Meta:
        node = MarketStock


class MarketStockCompanyDailyTrading(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = MarketStockCompanyDailyTradingModel
        interfaces = (relay.Node,)


class MarketStockCompanyDailyTradingConnection(relay.Connection):
    class Meta:
        node = MarketStockCompanyDailyTrading


class MarketStockCompany(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = MarketStockCompanyModel
        interfaces = (relay.Node,)


class MarketStockCompanyConnection(relay.Connection):
    class Meta:
        node = MarketStockCompany


class MarketStockCompanyPrediction(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = MarketStockCompanyPredictionModel
        interfaces = (relay.Node,)


class MarketStockCompanyPredictionConnection(relay.Connection):
    class Meta:
        node = MarketStockCompanyPrediction


class MarketStockCompanyDailyTradingPrediction(ExtendedSQLAlchemyObjectType):
    class Meta:
        model = MarketStockCompanyDailyTradingPredictionModel
        interfaces = (relay.Node,)


class MarketStockCompanyDailyTradingPredictionConnection(relay.Connection):
    class Meta:
        node = MarketStockCompanyDailyTradingPrediction


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # Allows sorting over multiple columns, by default over the primary key
    market_stock = ExtendedSQLAlchemyConnectionField(MarketStock)
    market_sector = ExtendedSQLAlchemyConnectionField(MarketSector)
    market_stock_company = ExtendedSQLAlchemyConnectionField(MarketStockCompany)
    market_stock_company_daily_trading = ExtendedSQLAlchemyConnectionField(
        MarketStockCompanyDailyTrading
    )
    market_stock_company_prediction = ExtendedSQLAlchemyConnectionField(
        MarketStockCompanyPrediction
    )
    market_stock_company_daily_trading_prediction = ExtendedSQLAlchemyConnectionField(
        MarketStockCompanyDailyTradingPrediction
    )
