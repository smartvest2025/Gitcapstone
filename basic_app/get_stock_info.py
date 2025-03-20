import urllib.request, json
import yfinance as yf
from django.core.cache import cache

def getStockInfo(tickers):
    all_stock_data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        try:
            stock_info = stock.info
        except Exception as e:
            return {'error': 'Failed to fetch stock data', 'details': str(e)}
    
        if 'error' in stock_info:
            return {'error': stock_info['error']}
        
        formatted_data = {
            'symbol': stock_info.get('symbol', ticker),
            'name': stock_info.get('longName', ticker),
            'exchange': stock_info.get('exchange', 'N/A'),
            'sector': stock_info.get('sector', 'N/A'),
            'industry': stock_info.get('industry', 'N/A'),
            'currentPrice': stock_info.get('currentPrice', 'N/A'),
            'marketCap': stock_info.get('marketCap', 'N/A'),
            'dividendYield': stock_info.get('dividendYield', 'N/A'),
        }
        
        all_stock_data.append(formatted_data)
    
    return all_stock_data

def search_stocks(query):
    try:
        query_lower = query.lower().strip()
        search_results = []

        # Try to get the cached ticker info
        cached_ticker_info = cache.get("extended_ticker_info")
        if not cached_ticker_info:
            # Extended list of ticker symbols (more than 50)
            extended_tickers = (
                "AAPL MSFT TSLA AMZN GOOG META NVDA JPM NFLX BABA IBM ORCL INTC CSCO HPQ QCOM VZ T "
                "PG KO PFE MRK WMT DIS HD MA V CVX XOM UNH BA LMT CAT GE MMM HON CRM ABT NKE COST "
                "SBUX MCD LOW T TMO ABNB BIDU BKNG JD SPOT PEP ADOB"
            )
            ticker_data = yf.Tickers(extended_tickers)
            cached_ticker_info = {}
            for ticker in ticker_data.tickers.keys():
                stock = yf.Ticker(ticker)
                stock_info = stock.info
                cached_ticker_info[ticker] = stock_info
            # Cache the data for one hour (3600 seconds)
            cache.set("extended_ticker_info", cached_ticker_info, timeout=3600)

        # Search through the cached ticker info
        for ticker, stock_info in cached_ticker_info.items():
            name = stock_info.get('longName', '').lower()
            symbol = stock_info.get('symbol', '').lower()
            if query_lower in name or query_lower in symbol:
                search_results.append({
                    'symbol': stock_info.get('symbol'),
                    'name': stock_info.get('longName', 'N/A'),
                    'exchange': stock_info.get('exchange', 'N/A'),
                    'sector': stock_info.get('sector', 'N/A'),
                    'industry': stock_info.get('industry', 'N/A'),
                    'currentPrice': stock_info.get('currentPrice', 'N/A'),
                    'marketCap': stock_info.get('marketCap', 'N/A'),
                    'currency': stock_info.get('currency', 'USD')
                })
            if len(search_results) >= 10:  # Limit results to 10
                break

        return search_results if search_results else {'error': 'No matching stocks found'}

    except Exception as e:
        return {'error': 'Failed to fetch stock data', 'details': str(e)}
