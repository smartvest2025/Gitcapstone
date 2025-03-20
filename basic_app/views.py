from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users

from .models import Portfolio, Client, Stock
from .forms import CreateUserForm
from .sectorPerformance import sectorPerformance
from basic_app.stock_data import candlestick_data, get_data, get_name, get_price
from basic_app.FA import piotroski
from basic_app.get_news import getNews, getNewsWithSentiment
from basic_app.get_stock_info import getStockInfo, search_stocks
from basic_app.ProphetTrend import forecast
from basic_app.get_learning_content import get_learning_content

import yfinance as yf
from json import dumps, loads
import logging

logger = logging.getLogger(__name__)
#Graph
import matplotlib.pyplot as plt
import yfinance as yf
import base64
from io import BytesIO

def get_historical_chart(ticker):
    # Fetch historical data (e.g., 1 year of daily data)
    df = yf.Ticker(ticker).history(period="1y")
    if df.empty:
        return None
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['Close'], label="Close Price", color="blue")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(f"{ticker} Historical Price")
    plt.legend()
    
    # Save plot to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode('utf-8')
    plt.close()  # Close the figure to free memory
    return graph


# Dashboard view (landing page)
def dashboard(request):
    return render(request, "basic_app/dashboard.html")

# Home/Index view with AJAX-based stock search
@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def index(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = request.POST.get('searchData')
        if not data or len(data) < 1:
            return JsonResponse({'data': 'Invalid input. Please enter a valid stock name or symbol.'})
        search_results = search_stocks(data)
        if isinstance(search_results, dict) and 'error' in search_results:
            return JsonResponse({'data': search_results})
        return JsonResponse({'data': search_results}, safe=False)
    
    user = request.user
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    
    # Calculate total portfolio value
    total_value = 0.0
    for s in stocks:
        # Update sector performance if not set
        if not s.stock_sector_performance:
            s.stock_sector_performance = sectorPerformance(s.stock_symbol)
        # Update price if not set
        if not s.stock_price:
            price = get_price(s.stock_symbol)
            s.stock_price = str(round(price[0], 2)) + " " + price[1]
        s.save()
        # Calculate portfolio value: quantity * price
        try:
            price_num = float(s.stock_price.split()[0])
            total_value += price_num * s.quantity
        except Exception as e:
            print(f"Error processing {s.stock_symbol}: {e}")
    
    news = getNews("business")
    context = {
        'stocks': stocks,
        'total_value': total_value,
        'news': news,
        'page_title': "Home"
    }
    return render(request, "basic_app/index.html", context)


# User profile view
@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def profile(request):
    client = request.user
    return render(request, "basic_app/profile.html", {'client': client, 'page_title': "User Profile"})

# Portfolio view (shows stocks added to the portfolio)
@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def portfolio(request):
    user = request.user
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    
    total_value = 0.0
    for s in stocks:
        # Update sector performance if missing
        if not s.stock_sector_performance:
            s.stock_sector_performance = sectorPerformance(s.stock_symbol)
        # Update price if missing
        if not s.stock_price:
            price = get_price(s.stock_symbol)
            s.stock_price = str(round(price[0], 2)) + " " + price[1]
        s.save()
        # Extract numeric part and calculate total value
        try:
            price_num = float(s.stock_price.split()[0])
            total_value += price_num * s.quantity
        except Exception as e:
            print(f"Error processing {s.stock_symbol}: {e}")
    
    context = {
        'stocks': stocks,
        'total_value': total_value,
        'page_title': "Your Portfolio"
    }
    print(f"Stocks retrieved: {[stock.stock_symbol for stock in stocks]}")
    return render(request, "basic_app/portfolio.html", context)

# Stock detail view: fetches stock data and renders stock.html
@login_required(login_url='basic_app:login')
def stock(request, symbol):
    data = candlestick_data(symbol)
    try:
        # Pass symbol as a list to fetch info correctly
        item = getStockInfo([symbol])
    except Exception as e:
        messages.error(request, f"Failed to fetch stock information: {str(e)}")
        return redirect('basic_app:index')
    
    info = get_data(symbol)
    piotroski_score = piotroski(symbol)
    short_name = info.get('shortName', 'Unknown')
    news = getNewsWithSentiment(short_name)
    
    sentiment_news_chart = {'positive': 0, 'negative': 0, 'neutral': 0}
    for i in range(min(12, len(news))):
        if news[i]['sentiment'] == 'positive':
            sentiment_news_chart['positive'] += 1
        elif news[i]['sentiment'] == 'negative':
            sentiment_news_chart['negative'] += 1
        else:
            sentiment_news_chart['neutral'] += 1
    
    recommendation = False
    overall_sentiment = sentiment_news_chart['positive'] - sentiment_news_chart['negative']
    if piotroski_score is not None and piotroski_score > 5 and overall_sentiment > 0:
        recommendation = True

    # Generate the historical chart for the stock
    history_graph = get_historical_chart(symbol)
    
    context = {
        'data': dumps(data),
        'item': dumps(item),
        'info': info,
        'piotroski_score': piotroski_score,
        'sentiment_data': dumps(sentiment_news_chart),
        'page_title': symbol + " Info",
        'recommendation': recommendation,
        'history_graph': history_graph  # pass the graph to the template
    }
    
    # AJAX handling for adding stock from detail page (unchanged)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and item:
        run = False
        data_post = request.POST.get('myData')
        name = request.POST.get('name')
        user = request.user
        client = Client.objects.get(user=user)
        portfolio = Portfolio.objects.get(client=client)
        stocks = portfolio.stocks.all()
        for stock in stocks:
            if data_post == stock.stock_symbol:
                stock.quantity += 1
                stock.save()
                run = True
        if not run:
            new_stock = Stock.objects.create(parent_portfolio=portfolio, stock_symbol=data_post, stock_name=name)
            new_stock.quantity = 1
            new_stock.save()
        return JsonResponse({})
    
    return render(request, "basic_app/stock.html", context)



# Login view
@unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.exists() and user.groups.all()[0].name == 'Admin':
                return redirect("basic_app:stats")
            else:
                return redirect("basic_app:index")
        else:
            messages.info(request, "Incorrect username or password")
            return redirect("basic_app:login")
    return render(request, "basic_app/login.html", {'page_title': "Login"})

# Logout view
@login_required(login_url='basic_app:login')
def logoutUser(request):
    logout(request)
    return redirect("basic_app:login")

# Registration view
@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='Client')
            user.groups.add(group)
            client = Client.objects.create(user=user)
            portfolio = Portfolio.objects.create(client=client)
            return redirect('basic_app:login')
    context = {'form': form, 'page_title': "Register"}
    return render(request, "basic_app/register.html", context)

# Admin statistics view
@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Admin'])
def statisticsAdmin(request):
    return render(request, "basic_app/statisticsAdmin.html")

# Price prediction view using Prophet
def price_prediction(request, symbol):
    if not symbol or len(symbol.strip()) == 0:
        messages.error(request, "Invalid stock symbol provided")
        return redirect('basic_app:index')
    try:
        price_prediction = forecast(symbol)
        return render(request, "basic_app/price_prediction.html", {
            'price_prediction': price_prediction,
            'page_title': "Price Prediction"
        })
    except Exception as e:
        print(f"Error in price prediction: {e}")
        messages.error(request, f"Failed to generate price prediction: {str(e)}")
        return redirect('basic_app:index')

# Add a stock to the user's portfolio
def addToPortfolio(request, symbol):
    user = request.user
    run = False
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    for stock in stocks:
        if symbol == stock.stock_symbol:
            stock.quantity += 1
            stock.save()
            run = True
    name = get_name(symbol)
    if not run:
        new_stock = Stock.objects.create(parent_portfolio=portfolio, stock_symbol=symbol, stock_name=name)
        new_stock.quantity = 1
        new_stock.save()
    return redirect('basic_app:portfolio')

# Remove a stock from the portfolio
def removeFromPortfolio(request, symbol):
    user = request.user
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    for stock in stocks:
        if symbol == stock.stock_symbol:
            stock.delete()
    return redirect("basic_app:portfolio")

# Increase quantity of a stock in the portfolio
def quantityAdd(request, symbol):
    user = request.user
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    for stock in stocks:
        if symbol == stock.stock_symbol:
            stock.quantity += 1
            stock.save()
    return redirect("basic_app:portfolio")

# Decrease quantity (or remove if zero) of a stock in the portfolio
def quantitySub(request, symbol):
    user = request.user
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    for stock in stocks:
        if symbol == stock.stock_symbol:
            stock.quantity -= 1
            if stock.quantity == 0:
                stock.delete()
            else:
                stock.save()
    return redirect('basic_app:portfolio')

# Learning view: returns educational content for stocks, ETFs, trading, etc.
@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def learning_view(request):
    # Base learning articles for each category
    categories = {
        "Stocks": [
            {
                "title": "Stock Market Basics",
                "description": "Learn the basics of the stock market and how it works.",
                "link": "https://www.investopedia.com/stock-market-basics-4689741"
            },
            {
                "title": "How to Invest in Stocks",
                "description": "A step-by-step guide on how to start investing in stocks.",
                "link": "https://www.investopedia.com/how-to-invest-in-stocks-4689742"
            }
        ],
        "ETFs": [
            {
                "title": "Exchange-Traded Funds (ETFs) Explained",
                "description": "Understand how ETFs work and why investors use them.",
                "link": "https://www.investopedia.com/etf-guide-4689743"
            }
        ],
        "Trading": [
            {
                "title": "Day Trading Strategies",
                "description": "Learn common day trading strategies and tips.",
                "link": "https://www.investopedia.com/day-trading-strategies-4689744"
            }
        ]
    }
    
    # For each category, try to fetch dynamic articles using get_learning_content
    for category in categories.keys():
        try:
            dynamic_articles = get_learning_content(category)
            if isinstance(dynamic_articles, dict):
                # Extend the list with dynamic articles if any are returned
                categories[category].extend(dynamic_articles.values())
        except Exception as e:
            # Log the error and continue with the base articles
            print(f"Error fetching dynamic articles for {category}: {e}")
    
    context = {'categories': categories}
    return render(request, 'basic_app/learning.html', context)

