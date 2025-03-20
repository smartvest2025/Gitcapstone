import requests

API_KEY = "9b23adeb6a634a0ba1f62e76dcbc54de"

def getNews(topic):
    """
    Fetches general news articles for the given topic (e.g., "business").
    Returns a list of articles or an empty list if there is an error.
    """
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&category={topic}&apiKey={API_KEY}"
        response = requests.get(url)
        print("getNews response status:", response.status_code)
        if response.status_code != 200:
            print(f"Error in getNews: Status code {response.status_code}, response: {response.text}")
            return []
        data = response.json()
        articles = data.get("articles") or []
        print("getNews - Articles found:", len(articles))
        return articles
    except Exception as e:
        print(f"Error in getNews for topic '{topic}': {e}")
        return []

def getNewsWithSentiment(stock_name):
    """
    Fetches news articles for the given stock name and attaches a default sentiment ("neutral").
    Returns up to 12 articles or an empty list if there is an error.
    """
    try:
        url = f"https://newsapi.org/v2/everything?q={stock_name}&pageSize=12&apiKey={API_KEY}"
        response = requests.get(url)
        print("getNewsWithSentiment response status:", response.status_code)
        if response.status_code != 200:
            print(f"Error in getNewsWithSentiment: Status code {response.status_code}, response: {response.text}")
            return []
        data = response.json()
        if not isinstance(data, dict):
            print("Error: Returned data is not a dictionary.")
            return []
        articles = data.get("articles") or []
        print("getNewsWithSentiment - Articles found:", len(articles))
        results = []
        for article in articles:
            if not isinstance(article, dict):
                continue
            # Default sentiment is set to "neutral" if no further analysis is done
            sentiment = "neutral"
            article["sentiment"] = sentiment
            results.append(article)
        return results
    except Exception as e:
        print(f"Error in getNewsWithSentiment for '{stock_name}': {e}")
        return []
