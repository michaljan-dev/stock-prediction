DROP TABLE IF EXISTS aggregated_market_stock;
CREATE TABLE aggregated_market_stock AS (
SELECT 
DISTINCT mscdt.date,
  'kgm' AS series_id,
  mscdtc.open AS market_stock_company_daily_open,
mscdtc.low AS market_stock_company_daily_low,
mscdtc.close AS market_stock_company_daily_close,
msidtw.open AS market_stock_index_daily_trading_wig_open, 
mcfedrepln.close AS market_currency_foreign_exchange_daily_rate_eur_pln_close,
mcfrusdpln.close AS market_currency_foreign_exchange_daily_rate_usd_pln_close,
mcdtgold.close AS market_commodity_daily_trading_gold_close,
mcdtcopper.open AS market_commodity_daily_trading_copper_open,
mcdtcopper.close AS market_commodity_daily_trading_copper_close,
mcdtsilver.close AS market_commodity_daily_trading_silver_close,
mcdtbrentoil.close AS market_commodity_daily_trading_brentoil_close
    FROM market_stock_index_daily_trading AS mscdt
INNER JOIN 
    market_stock_index_daily_trading AS msidtw ON msidtw.date = mscdt.date AND msidtw.market_stock_index_id = 'wig'   
LEFT JOIN 
    market_stock_company_daily_trading AS mscdtc ON mscdtc.date = mscdt.date AND mscdtc.market_stock_company_id = 'PLKGHM000017'
LEFT JOIN 
    market_stock_index_daily_trading AS msidtd ON msidtd.date = mscdt.date AND msidtd.market_stock_index_id = 'dax'
LEFT JOIN 
    market_stock_index_daily_trading AS msidtc ON msidtc.date = mscdt.date AND msidtc.market_stock_index_id = 'cac40'
LEFT JOIN 
    market_stock_index_daily_trading AS msidtftsemib ON msidtftsemib.date = mscdt.date AND msidtftsemib.market_stock_index_id = 'ftsemib'
LEFT JOIN 
    market_stock_index_daily_trading AS msidtdji ON msidtdji.date = mscdt.date AND msidtdji.market_stock_index_id = 'dji'
LEFT JOIN 
    market_stock_index_daily_trading AS msidtftse100 ON msidtftse100.date = mscdt.date AND msidtftse100.market_stock_index_id = 'ftse100'
LEFT JOIN 
    market_currency_foreign_exchange_daily_rate AS mcfedrepln ON mcfedrepln.date = mscdt.date AND mcfedrepln.market_currency_foreign_exchange_pair_id = 'eur-pln'
LEFT JOIN
    market_currency_foreign_exchange_daily_rate AS mcfrusdpln ON mcfrusdpln.date = mscdt.date AND mcfrusdpln.market_currency_foreign_exchange_pair_id = 'usd-pln'
LEFT JOIN 
    market_bond_daily_trading AS mbdtpl ON mbdtpl.date = mscdt.date AND mbdtpl.market_country_id = 'pl' AND mbdtpl.market_bond_id = '10Y'
LEFT JOIN
    market_bond_daily_trading AS mbdtde ON mbdtde.date = mscdt.date AND mbdtde.market_country_id = 'de' AND mbdtde.market_bond_id = '10Y'
LEFT JOIN 
    market_bond_daily_trading AS mbdtus ON mbdtus.date = mscdt.date AND mbdtus.market_country_id = 'us' AND mbdtus.market_bond_id = '10Y'
LEFT JOIN
    market_commodity_daily_trading AS mcdtgold ON mcdtgold.date = mscdt.date AND mcdtgold.market_commodity_id = 'gold' 
LEFT JOIN 
    market_commodity_daily_trading AS mcdtcopper ON mcdtcopper.date = mscdt.date AND mcdtcopper.market_commodity_id = 'copper'
LEFT JOIN 
    market_commodity_daily_trading AS mcdtsilver ON mcdtsilver.date = mscdt.date AND mcdtsilver.market_commodity_id = 'silver'
LEFT JOIN 
    market_commodity_daily_trading AS mcdtbrentoil ON mcdtbrentoil.date = mscdt.date AND mcdtbrentoil.market_commodity_id = 'brentoil'
LEFT JOIN 
    market_commodity_daily_trading AS mcdtwtioil ON mcdtwtioil.date = mscdt.date AND mcdtwtioil.market_commodity_id = 'wtioil'
ORDER BY mscdt.date ASC);
DROP TABLE IF EXISTS aggregated_market_economic_indicator;
CREATE TABLE aggregated_market_economic_indicator AS ( 
    SELECT 
    DISTINCT mscdt.date,
    meicdplip_industrial_production.actual AS market_eicountry_data_pl_industrial_production_actual,
    meicdplic_inflation_cpi.actual AS market_eicountry_data_pl_inflation_cpi_actual,
    meicdplie_interest_rate.actual AS market_eicountry_data_pl_interest_rate_actual,
    meicdplmp_manufacturing_pmi.actual AS market_eicountry_data_pl_manufacturing_pmi_actual,
    meicddeic_inflation_cpi.actual AS market_eicountry_data_de_inflation_cpi_actual,
    meicdeuie_interest_rate.actual AS market_eicountry_data_eu_interest_rate_actual,
    meicdusic_inflation_cpi.actual AS market_eicountry_data_us_inflation_cpi_actual,
    meicdusie_interest_rate.actual AS market_eicountry_data_us_interest_rate_actual,
    meicdplgga_gdp_growth_annual.forecast AS market_eicountry_data_pl_gdp_growth_annual_forecast,
    meicddegga_gdp_growth_annual.forecast AS market_eicountry_data_de_gdp_growth_annual_forecast,
    meicdfrgga_gdp_growth_annual.actual AS market_eicountry_data_fr_gdp_growth_annual_forecast,
    meicdcngga_gdp_growth_annual.actual AS market_eicountry_data_cn_gdp_growth_annual_forecast,
    meicdusgga_gdp_growth.forecast AS market_eicountry_data_us_gdp_growth_forecast
    FROM  market_economic_indicator_country_data AS mscdt
    LEFT JOIN 
    market_economic_indicator_country_data AS meicdplca ON meicdplca.date = mscdt.date AND meicdplca.market_country_id = 'pl'  AND meicdplca.market_economic_indicator_id = 'current-account'
LEFT JOIN 
    market_economic_indicator_country_data AS meicdplec_emp_change ON meicdplec_emp_change.date = mscdt.date AND meicdplec_emp_change.market_country_id = 'pl'  AND meicdplec_emp_change.market_economic_indicator_id = 'employment-change' 
LEFT JOIN 
    market_economic_indicator_country_data AS meicdplgga_gdp_growth_annual ON meicdplgga_gdp_growth_annual.date = mscdt.date AND meicdplgga_gdp_growth_annual.market_country_id = 'pl'  AND meicdplgga_gdp_growth_annual.market_economic_indicator_id = 'gdp-growth-annual'
LEFT JOIN 
    market_economic_indicator_country_data AS meicdplip_industrial_production ON meicdplip_industrial_production.date = mscdt.date AND meicdplip_industrial_production.market_country_id = 'pl'  AND meicdplip_industrial_production.market_economic_indicator_id = 'industrial-production' 
LEFT JOIN 
    market_economic_indicator_country_data AS meicdplic_inflation_cpi ON meicdplic_inflation_cpi.date = mscdt.date AND meicdplic_inflation_cpi.market_country_id = 'pl'  AND meicdplic_inflation_cpi.market_economic_indicator_id = 'inflation-cpi'
LEFT JOIN 
    market_economic_indicator_country_data AS meicdplie_interest_rate ON meicdplie_interest_rate.date = mscdt.date AND meicdplie_interest_rate.market_country_id = 'pl'  AND meicdplie_interest_rate.market_economic_indicator_id = 'interest-rate' 
LEFT JOIN 
    market_economic_indicator_country_data AS meicdplmp_manufacturing_pmi ON meicdplmp_manufacturing_pmi.date = mscdt.date AND meicdplmp_manufacturing_pmi.market_country_id = 'pl'  AND meicdplmp_manufacturing_pmi.market_economic_indicator_id = 'manufacturing-pmi' 
LEFT JOIN 
    market_economic_indicator_country_data AS meicdplrsa_retail_sales_annual ON meicdplrsa_retail_sales_annual.date = mscdt.date AND meicdplrsa_retail_sales_annual.market_country_id = 'pl'  AND meicdplrsa_retail_sales_annual.market_economic_indicator_id = 'retail-sales-annual'    
LEFT JOIN 
    market_economic_indicator_country_data AS meicdplur_unemployment_rate ON meicdplur_unemployment_rate.date = mscdt.date AND meicdplur_unemployment_rate.market_country_id = 'pl'  AND meicdplur_unemployment_rate.market_economic_indicator_id = 'unemployment-rate' 
LEFT JOIN 
    market_economic_indicator_country_data AS meicddegga_gdp_growth_annual ON meicddegga_gdp_growth_annual.date = mscdt.date AND meicddegga_gdp_growth_annual.market_country_id = 'de'  AND meicddegga_gdp_growth_annual.market_economic_indicator_id = 'gdp-growth-annual'
LEFT JOIN 
    market_economic_indicator_country_data AS meicddeic_inflation_cpi ON meicddeic_inflation_cpi.date = mscdt.date AND meicddeic_inflation_cpi.market_country_id = 'de'  AND meicddeic_inflation_cpi.market_economic_indicator_id = 'inflation-cpi'
LEFT JOIN 
    market_economic_indicator_country_data AS meicddersa_retail_sales_annual ON meicddersa_retail_sales_annual.date = mscdt.date AND meicddersa_retail_sales_annual.market_country_id = 'de'  AND meicddersa_retail_sales_annual.market_economic_indicator_id = 'retail-sales-annual'  
LEFT JOIN 
    market_economic_indicator_country_data AS meicddeur_unemployment_rate ON meicddeur_unemployment_rate.date = mscdt.date AND meicddeur_unemployment_rate.market_country_id = 'de'  AND meicddeur_unemployment_rate.market_economic_indicator_id = 'unemployment-rate'  
LEFT JOIN
    market_economic_indicator_country_data AS meicddeur_manufacturing_pmi ON meicddeur_manufacturing_pmi.date = mscdt.date AND meicddeur_manufacturing_pmi.market_country_id = 'de'  AND meicddeur_manufacturing_pmi.market_economic_indicator_id = 'manufacturing-pmi'  
LEFT JOIN
    market_economic_indicator_country_data AS meicdeuie_interest_rate ON meicdeuie_interest_rate.date = mscdt.date AND meicdeuie_interest_rate.market_country_id = 'eu'  AND meicdeuie_interest_rate.market_economic_indicator_id = 'interest-rate'     
LEFT JOIN 
    market_economic_indicator_country_data AS meicdusgga_gdp_growth ON meicdusgga_gdp_growth.date = mscdt.date AND meicdusgga_gdp_growth.market_country_id = 'us'  AND meicdusgga_gdp_growth.market_economic_indicator_id = 'gdp-growth'
LEFT JOIN 
    market_economic_indicator_country_data AS meicdusic_inflation_cpi ON meicdusic_inflation_cpi.date = mscdt.date AND meicdusic_inflation_cpi.market_country_id = 'us'  AND meicdusic_inflation_cpi.market_economic_indicator_id = 'inflation-cpi'
LEFT JOIN 
    market_economic_indicator_country_data AS meicdusie_interest_rate ON meicdusie_interest_rate.date = mscdt.date AND meicdusie_interest_rate.market_country_id = 'us'  AND meicdusie_interest_rate.market_economic_indicator_id = 'interest-rate' 
LEFT JOIN 
    market_economic_indicator_country_data AS meicdusrsa_retail_sales_annual ON meicdusrsa_retail_sales_annual.date = mscdt.date AND meicdusrsa_retail_sales_annual.market_country_id = 'us'  AND meicdusrsa_retail_sales_annual.market_economic_indicator_id = 'retail-sales-annual'  
LEFT JOIN 
    market_economic_indicator_country_data AS meicdusur_unemployment_rate ON meicdusur_unemployment_rate.date = mscdt.date AND meicdusur_unemployment_rate.market_country_id = 'us'  AND meicdusur_unemployment_rate.market_economic_indicator_id = 'unemployment-rate'   
LEFT JOIN 
    market_economic_indicator_country_data AS meicdfrgga_gdp_growth_annual ON meicdfrgga_gdp_growth_annual.date = mscdt.date AND meicdfrgga_gdp_growth_annual.market_country_id = 'fr'  AND meicdfrgga_gdp_growth_annual.market_economic_indicator_id = 'gdp-growth-annual'
LEFT JOIN 
    market_economic_indicator_country_data AS meicdcngga_gdp_growth_annual ON meicdcngga_gdp_growth_annual.date = mscdt.date AND meicdcngga_gdp_growth_annual.market_country_id = 'cn'  AND meicdcngga_gdp_growth_annual.market_economic_indicator_id = 'gdp-growth-annual'
WHERE mscdt.market_country_id = 'pl' OR mscdt.market_country_id = 'de' OR mscdt.market_country_id = 'us' OR mscdt.market_country_id = 'fr' OR mscdt.market_country_id = 'cn' OR mscdt.market_country_id = 'eu') ORDER BY mscdt.date ASC