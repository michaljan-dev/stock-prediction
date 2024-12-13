# Economic Indicators and Stock Data Scrapers

## Purpose
This project provides tools to scrape economic indicators and stock data for generating datasets to support stock prediction in the PL stock market.


## Setting Up Python Environment

### Prerequisites
1. Use Poetry and pyenv to manage Python versions.
2. Install the following dependencies for Python development: 
    libxml2-dev liblzma-dev libxslt-dev python3-dev libmysqlclient-dev libsqlite3-dev

Configuring Poetry Environment
- Specify the Python version for Poetry to use:
  poetry env use {pythonVersion}

Configuring Automation Services
- Set up cron jobs with Celery to automate scraping tasks and data processing. The services are located in the systemd folder.

Main App Configuration
- Rename the config.dist.py file to config.py.
- Update the variables inside config.py as needed for environment.

Alternative Data Extraction with GraphQL
If cron is not being used, you can leverage GraphQL queries for data extraction.

Use global queries to extract full datasets.
Generate data files from these queries for stock prediction purposes.

## GraphQL Queries for Crontab Schedules

Below are the available **GraphQL queries** for executing crontab schedules. Each query is identified by its respective `CrontabSchedule` ID and task description.

### CrontabSchedule:8 - All stock data
 query{
   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjg=") {
     result
   }
 }

### CrontabSchedule:9 - Generate file for prediction model
 query{
   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjk=") {
     result
   }
 }

### CrontabSchedule:1 - Market stock company data for PL.
 query{
   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjE=") {
     result
   }
 }

### CrontabSchedule:2 - Daily stock trading data for PL
 query{
   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjI=") {
     result
   }
 }

### CrontabSchedule:3 - Currency data
 query{
   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjM=") {
     result
   }
 }

### CrontabSchedule:4 - Commodity data
 query{
   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjQ=") {
     result
   }
 }

### CrontabSchedule:5 - Bond data
 query{
   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjU=") {
         result
   }
 }

### CrontabSchedule:6 - Economic indicator country data
 query{
   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjY=") {
     result
   }
 }

### CrontabSchedule:7 - Stock index data
 query{
   runCronJob(id:"Q3JvbnRhYlNjaGVkdWxlOjc=") {
     result
   }
 }