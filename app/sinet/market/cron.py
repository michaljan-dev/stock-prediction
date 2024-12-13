from app import db
from app.sinet.market.currency.data_extraction import (
    currency_daily_trading_spider_process,
)
from app.sinet.market.commodity.data_extraction import (
    commodity_daily_trading_spider_process,
)
from app.sinet.market.bond.data_extraction import bond_daily_trading_spider_process
from app.sinet.market.economic_indicator.data_extraction import (
    economic_indicator_daily_spider_process,
)
from app.sinet.market.stock.data_extraction import (
    stock_index_daily_trading_spider_process,
)

# gpw
from app.sinet.market.stock.gpw.data_extraction import company_spider_process
from app.sinet.market.stock.gpw.data_extraction import (
    company_daily_trading_spider_process,
)

from celery.task import task
from datetime import datetime
import pandas as pd
import os


#
# query{
#   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjg=") {
#     result
#   }
# }
# CrontabSchedule:8 - all stock data
@task
def market_combined_spider_process(*args, **kwargs):
    currency_daily_trading_spider_process()
    commodity_daily_trading_spider_process()
    bond_daily_trading_spider_process()
    economic_indicator_daily_spider_process()
    stock_index_daily_trading_spider_process()

    company_spider_process()
    company_daily_trading_spider_process()
    print("run market_combined_spider_process")
    return 200


#
# query{
#   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjk=") {
#     result
#   }
# }
# CrontabSchedule:9 - Generate file for prediction model
@task
def market_generate_csv_file_for_prediction_model(*args, **kwargs):
    files = [
        # {"f": "aggregated_data-wig.sql", "p": "wig"},
        {"f": "aggregated_data-kghm.sql", "p": "kghm"},
    ]
    for file in files:
        _market_generate_aggregated_data(sql_file=file["f"])
        _market_generate_csv_file(prefix=file["p"])
    print("run market_generate_csv_file_for_prediction_model")
    return 200


def _market_generate_csv_file(prefix):
    # Fetch data from the query in batches
    query = "SELECT * FROM  aggregated_market_economic_indicator LEFT JOIN aggregated_market_stock ON  aggregated_market_economic_indicator.date = aggregated_market_stock.date ORDER BY aggregated_market_economic_indicator.date ASC;"
    df = pd.read_sql_query(query, con=db.session.bind)

    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d")
    csv_filename = f"{current_date}-{prefix}-aggregated-original.csv"
    csv_filename = os.path.join("_data", csv_filename)

    # Save the DataFrame to a CSV file
    df.to_csv(csv_filename, index=False)

    # Fill null values using forward filling (ffill)
    df.fillna(method="ffill", inplace=True)
    # Drop columns where all values are NaN
    df_cleaned = df.dropna(axis=1, how="all")
    # Remove rows with any empty (NaN) values in any column
    df_drop = df_cleaned.dropna()
    # Drop columns with duplicate names
    df_drop = df_drop.loc[:, ~df_drop.columns.duplicated()]
    csv_filename = f"{current_date}-{prefix}-aggregated-fillna.csv"
    csv_filename = os.path.join("_data", csv_filename)
    df_drop.to_csv(csv_filename, index=False)

    print(f"Data has been saved to {csv_filename}")


def _market_generate_aggregated_data(sql_file):

    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(current_directory, "_sql", sql_file)

    with open(sql_file_path) as sql_file:
        statements = sql_file.read().split(";")
        for statement in statements:
            if len(statement.strip()) > 0:
                db.session.execute(statement + ";")
        db.session.commit()
    print("run market_generate_aggregated_data")
