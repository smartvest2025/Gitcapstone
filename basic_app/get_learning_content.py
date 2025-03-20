import requests
from bs4 import BeautifulSoup
import random

def get_learning_content(topic):
    url = f"https://www.investopedia.com/search?q={topic}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = soup.find_all('div', class_='search-results__item')
    
    content = {}

    if len(articles) >= 5:  # Limit results to 5 to keep it balanced
        random_articles = random.sample(articles, 5)
    else:
        random_articles = articles

    for i, article in enumerate(random_articles):
        title_tag = article.find('h3')
        link_tag = article.find('a')
        desc_tag = article.find('p')

        if title_tag and link_tag:
            title = title_tag.text.strip()
            link = link_tag['href']
            description = desc_tag.text.strip() if desc_tag else "No description available."

            content[i] = {'title': title, 'link': link, 'description': description}

    return content
