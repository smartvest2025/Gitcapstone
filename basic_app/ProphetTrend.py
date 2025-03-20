from prophet import Prophet
#import pystan
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer,format = "png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def forecast(ticker):
    try:
        # Get historical data
        df = yf.Ticker(ticker).history(period='5y', interval='1d')
        if df.empty:
            raise ValueError(f"No data found for ticker: {ticker}")
            
        # Prepare data for Prophet
        df = df[['Close']]
        if df.isnull().values.any():
            raise ValueError("Missing data in historical prices")
            
        dfx = pd.DataFrame()

        # Prepare time series data
        dfx['ds'] = pd.to_datetime(df.index)
        dfx['y'] = df.Close.values
        
        # Create and fit Prophet model
        fbp = Prophet(daily_seasonality=True)
        fbp.fit(dfx)
        
        # Make predictions
        fut = fbp.make_future_dataframe(periods=365)
        forecast = fbp.predict(fut)
        
        # Generate plot
        plot = fbp.plot(forecast)
        plt.xlabel("Date")
        plt.ylabel("Price")
        graph = get_graph()
        plt.close()  # Close plot to free memory
        return graph
        
    except Exception as e:
        print(f"Error in forecast for {ticker}: {str(e)}")
        raise  # Re-raise the exception for the view to handle

    # plt.show()
    # pchange = ((forecast.trend.values[-1] - dfx.y.values[-1])*100)/dfx.y.values[-1]
    # if pchange > 0:
    #     rating = 1
    # elif pchange == 0:
    #     rating = 0
    # else:
    #     rating = -1
    # return plot, rating
# plot, rating = forecast('googl')
