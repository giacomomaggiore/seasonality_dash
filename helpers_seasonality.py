import yfinance as yf
import pandas as pd
import numpy 
import datetime as dt




ticker = "AAPL"

start = "2018-01-01"
end = "2023-01-01"


def download_data(start, end, ticker):
  date_range = pd.date_range(start=start, end=end, freq="D")

  data = pd.DataFrame(index=date_range)
  data.index = data.index.strftime("%Y-%m-%d")

  df_stock = pd.DataFrame()
  historical = yf.download(ticker, start, end)
  df_stock["Close"] = historical["Close"]
  df_stock["Volume"] = historical["Volume"]
  df_stock["Year"] = df_stock.index.year
  df_stock.index = df_stock.index.strftime("%Y-%m-%d")



  data["Close"] = df_stock["Close"]
  data["Volume"] = df_stock["Volume"]
  data.bfill(inplace=True)
  data.index = pd.to_datetime(data.index)
  data["Year"] = data.index.year

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
    

    initial_year_price = data_year.at["01-01", "Close"]
    data_year["Close"] = ((data_year["Close"] - initial_year_price)/ initial_year_price) * 100
    df_seasonality[year] = data_year["Close"]

  df_seasonality.bfill(inplace = True)
  df_seasonality.ffill(inplace = True)
  df_seasonality.index = df_seasonality.index + "-2024"
  df_seasonality.index = pd.to_datetime(df_seasonality.index)
  
  df_seasonality.index = df_seasonality.index.strftime("%d-%B")
  return df_seasonality

