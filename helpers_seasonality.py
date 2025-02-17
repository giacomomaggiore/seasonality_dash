import yfinance as yf
import pandas as pd
import numpy 
import datetime as dt
import pandas_datareader.data as pdr
import seaborn as sns
import matplotlib.pyplot as plt
import json
import requests
import warnings
warnings.filterwarnings('ignore')

import os
from dotenv import load_dotenv
load_dotenv()

MY_API_TOKEN = os.getenv("API_KEY")

print(MY_API_TOKEN)
SYMBOL_NAME = 'AAPL'
EXCHANGE_CODE = 'US'

ticker = "AAPL"

start = "2018-01-01"
end = "2023-01-01"

def fetch_stock_data(ticker, start_date, end_date, skip_years=[], frequency='d', exchange_code='US'):
    
    """
    Fetch stock data for a given symbol and time range, skipping specified years.

    Parameters:
        ticker (str): The stock symbol (e.g., 'AAPL').
        exchange_code (str): The exchange code (e.g., 'US').
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        skip_years (list): List of years to exclude from the result.
        frequency (str): Data frequency ('d' for daily, 'w' for weekly, 'm' for monthly). Default is 'd'.

    Returns:
        pd.DataFrame: Processed DataFrame with selected columns and filtered rows. The index is set to 'Year'.
    """
    # Define API token
    API_TOKEN = MY_API_TOKEN

    # Construct API URL
    url = (f'https://eodhd.com/api/eod/{ticker}.{exchange_code}'
           f'?from={start_date}&to={end_date}&period={frequency}&api_token={API_TOKEN}&fmt=json')

    # Fetch data from the API
    response = requests.get(url)

    # Check for request errors
    if response.status_code != 200:
        raise ValueError(f"Error fetching data: {response.status_code}, {response.text}")

    # Parse JSON response
    useful_data = response.json()

    # Convert to DataFrame
    df = pd.DataFrame(useful_data)

    # Rename columns
    df = df.rename(columns={'adjusted_close': 'Adj Close', 'volume': 'Volume', 'date': 'Year'})


    # Select specific columns
    df = df[['Year', 'Adj Close', 'Volume']]
    print(df.columns)
    #print("sto stampando")
    #print(df.columns)

    # Convert 'Year' column to datetime
    df['Year'] = pd.to_datetime(df['Year'])


    # Set 'Year' as the index
    df = df.set_index('Year')
    df = df.set_index(pd.to_datetime(df.index))

    # Filter out rows with years in the skip_years list
    df = df[~df.index.year.isin(skip_years)]
    
    
    df_stock = pd.DataFrame(index = df.index.strftime("%Y-%m-%d"))
    df_stock["Adj Close"] = df["Adj Close"]
    df_stock["Volume"] = df["Volume"]
    df_stock["Year"] = df.index.year
    
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    data = pd.DataFrame(index=date_range)

    data["Adj Close"] = df["Adj Close"]
    data["Volume"] = df["Volume"]
    data.bfill(inplace=True)
    data.index = pd.to_datetime(data.index)
    data["Year"] = data.index.year

    return data

def download_data(start, end, ticker):
  date_range = pd.date_range(start=start, end=end, freq="D")

  data = pd.DataFrame(index=date_range)
  data.index = data.index.strftime("%Y-%m-%d")

  df_stock = pd.DataFrame()
  historical = yf.download(ticker, start, end)
  df_stock["Adj Close"] = historical["Adj Close"]
  df_stock["Volume"] = historical["Volume"]
  df_stock["Year"] = df_stock.index.year
  df_stock.index = df_stock.index.strftime("%Y-%m-%d")



  data["Adj Close"] = df_stock["Adj Close"]
  data["Volume"] = df_stock["Volume"]
  data.bfill(inplace=True)
  data.index = pd.to_datetime(data.index)
  data["Year"] = data.index.year

  return data

def calculate_seasonality_mean(start, end, ticker):
  data = download_data(ticker, start, end)

  #anno bisestile
  first_day = dt.datetime(2016,1,1)
  last_day = dt.datetime(2016,12,31)

  one_year_series = pd.date_range(start=first_day, end=last_day, freq="D")

  years = data["Year"].unique()
  df_seasonality = pd.DataFrame(index = one_year_series, columns=years)
  df_seasonality.index = df_seasonality.index.strftime("%m-%d")

  for year in years:
    data_year = data[data["Year"] == year]

    data_year.index = data_year.index.strftime("%m-%d")

    initial_year_price = data_year.at["01-01", "Adj Close"]
    data_year["Adj Close"] = ((data_year["Adj Close"] - initial_year_price)/ initial_year_price) * 100
    df_seasonality[year] = data_year["Adj Close"]

  df_seasonality.bfill(inplace = True)
  df_seasonality["mean"] = df_seasonality.mean(axis = 1, numeric_only=True)
  
  df_seasonality_mean = pd.DataFrame(index = df_seasonality.index)
  df_seasonality_mean["mean"] = df_seasonality["mean"]
  
  data = []
  
  for index, row in df_seasonality_mean.iterrows():
    temp_dict = {}
    temp_dict["date"] = "2024-"+index
    temp_dict["x"] = row["mean"]
    data.append(temp_dict)
  
  return data

def calculate_seasonality(start, end, ticker):
  data = download_data(start, end, ticker)

  #anno bisestile
  first_day = dt.datetime(2016,1,1)
  last_day = dt.datetime(2016,12,31)

  one_year_series = pd.date_range(start=first_day, end=last_day, freq="D")

  years = data["Year"].unique()
  df_seasonality = pd.DataFrame(index = one_year_series, columns=years)
  df_seasonality.index = df_seasonality.index.strftime("%m-%d")

  for year in years:
    data_year = data[data["Year"] == year]

    data_year.index = data_year.index.strftime("%m-%d")
    

    initial_year_price = data_year.at["01-01", "Adj Close"]
    data_year["Adj Close"] = ((data_year["Adj Close"] - initial_year_price)/ initial_year_price) * 100
    df_seasonality[year] = data_year["Adj Close"]

  df_seasonality.bfill(inplace = True)
  df_seasonality.ffill(inplace = True)
  df_seasonality.index = df_seasonality.index + "-2024"
  df_seasonality.index = pd.to_datetime(df_seasonality.index)
  
  df_seasonality.index = df_seasonality.index.strftime("%d-%B")
  return df_seasonality



def volume_seasonality(start, end, ticker):
  data = download_data(start, end, ticker)

  years = data["Year"].unique()

  month_range = numpy.arange(1,13,1)

  volume_df = pd.DataFrame(index=month_range, columns=years)

  for year in years:
    data_year = data[data["Year"] == year]
    volume_df[year] = data_year["Volume"].groupby(data_year.index.month).sum()

    initial_volume = volume_df.at[1, year]
    volume_df[year] = ((volume_df[year] / initial_volume))
  
  volume_df["mean"] = volume_df.mean(axis = 1, numeric_only=True)
  
  data = []
  for index, row in volume_df.iterrows():
    temp_dict = {}
    temp_dict["date"] = "2024-"+str(index)
    temp_dict["volume"] = row["mean"]
    
    data.append(temp_dict)
  
  return data
#------------------------------------------------------------

#data = calculate_seasonality("2009-01-01", "2015-01-01", "aapl")
#print(data)
#figure = plt.figure(figsize=(10,6))
