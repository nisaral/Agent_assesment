import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pydantic import BaseModel
from dotenv import load_dotenv
import aiohttp
import logging
from cachetools import TTLCache
from transformers import pipeline
from .base_agent import create_base_app

load_dotenv()
app = create_base_app("Scraping Agent")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache = TTLCache(maxsize=100, ttl=3600)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
if not NEWSAPI_KEY:
    logger.warning("NEWSAPI_KEY not found in environment variables")

try:
    sentiment_analyzer = pipeline("sentiment-analysis")
    logger.info("Successfully initialized sentiment analyzer")
except Exception as e:
    logger.error(f"Failed to initialize sentiment analyzer: {e}")
    sentiment_analyzer = None

class CompanyRequest(BaseModel):
    company: str

async def fetch_newsapi(symbol: str):
    if not NEWSAPI_KEY:
        logger.error("NewsAPI key not configured")
        return []
        
    url = f"https://newsapi.org/v2/everything"
    params = {
        "q": symbol,
        "apiKey": NEWSAPI_KEY,
        "pageSize": 5,
        "language": "en",
        "sortBy": "relevancy"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    logger.error(f"NewsAPI error: {resp.status}")
                    return []
                data = await resp.json()
                if data.get("status") != "ok":
                    logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                    return []
                return [article["description"] for article in data.get("articles", []) if article.get("description")]
    except Exception as e:
        logger.error(f"Error fetching news from NewsAPI: {e}")
        return []

@app.post("/run")
async def run(request: CompanyRequest):
    try:
        cache_key = f"news_{request.company}"
        if cache_key in cache:
            logger.info(f"Returning cached news for {request.company}")
            return {"news": cache[cache_key]}

        news_articles = await fetch_newsapi(request.company)
        if not news_articles:
            news_articles = [f"No news available for {request.company}"]
            logger.info("Using fallback empty news")

        articles_with_sentiment = []
        for text in news_articles:
            sentiment = "neutral"
            try:
                if sentiment_analyzer:
                    result = sentiment_analyzer(text)
                    sentiment = result[0]["label"].lower()
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
            articles_with_sentiment.append(f"{text} (Sentiment: {sentiment})")

        cache[cache_key] = articles_with_sentiment
        return {"news": articles_with_sentiment}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"news": [f"Error fetching news for {request.company}"]}