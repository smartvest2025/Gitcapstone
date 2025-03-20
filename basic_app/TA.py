import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import talib as ta

plt.style.use('seaborn')

def sma(ticker):
    df = yf.Ticker(ticker).history(period='1y')
    df['SMA'] = ta.SMA(df['Close'], timeperiod=20)
    df[['Close', 'SMA']].plot(figsize=(12,6))
    return plt

def ema(ticker):
    df = yf.Ticker(ticker).history(period='1y')
    df['EMA'] = ta.EMA(df['Close'], timeperiod=20)
    df[['Close', 'EMA']].plot(figsize=(12,6))
    return plt

def macd(ticker):
    df = yf.Ticker(ticker).history(period='1y')
    df['MACD'], df['MACDSIGNAL'], df['MACDHIST'] = ta.MACD(df['Close'])
    df[['MACD', 'MACDSIGNAL']].plot(figsize=(12,6))
    return plt

def rsi(ticker):
    df = yf.Ticker(ticker).history(period='1y')
    df['RSI'] = ta.RSI(df['Close'])
    df[['RSI']].plot(figsize=(12,6))
    return plt

def adx(ticker):
    df = yf.Ticker(ticker).history(period='1y')
    df['ADX'] = ta.ADX(df['High'], df['Low'], df['Close'])
    df[['ADX']].plot(figsize=(12,6))
    return plt

def bband(ticker):
    df = yf.Ticker(ticker).history(period='1y')
    df['UpBand'], df['MidBand'], df['LowBand'] = ta.BBANDS(df['Close'], timeperiod=20)
    df[['Close', 'UpBand', 'MidBand', 'LowBand']].plot(figsize=(12,6))
    return plt

def obv(ticker):
    df = yf.Ticker(ticker).history(period='1y')
    df['OBV'] = ta.OBV(df['Close'], df['Volume'])
    df[['OBV']].plot(figsize=(12,6))
    return plt

def pivots(ticker):
    df = yf.Ticker(ticker).history(period='1d').tail(1)
    
    high = df['High'].iloc[0]
    low = df['Low'].iloc[0]
    close = df['Close'].iloc[0]
    
    pp = (high + low + close) / 3
    r1 = 2 * pp - low
    s1 = 2 * pp - high
    r2 = pp + (high - low)
    s2 = pp - (high - low)
    r3 = pp + 2 * (high - low)
    s3 = pp - 2 * (high - low)

    print(f"Pivot: {pp}, R1: {r1}, R2: {r2}, R3: {r3}, S1: {s1}, S2: {s2}, S3: {s3}")
    return pp, r1, r2, r3, s1, s2, s3

# Example usage
sma('MSFT').show()
ema('MSFT').show()
macd('MSFT').show()
rsi('MSFT').show()
adx('MSFT').show()
bband('MSFT').show()
obv('MSFT').show()
pivots('HDFCBANK.NS')
