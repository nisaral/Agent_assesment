import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import aiohttp
import asyncio
from cachetools import TTLCache
try:
    from clients.mcp3_client import Mcp3ClientSession
except ImportError:
    from data_ingestion.mcp_scraper import fetch_news
    from transformers import pipeline

load_dotenv()
app = FastAPI()
cache = TTLCache(maxsize=100, ttl=3600)  # Cache for 1 hour
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")  # Add to .env

class SymbolRequest(BaseModel):
    symbol: str

async def fetch_newsapi(symbol: str):
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={NEWSAPI_KEY}&pageSize=5"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return [article["description"] for article in data.get("articles", []) if article.get("description")]
    except Exception as e:
        return []

@app.post("/news")
async def get_news(request: SymbolRequest):
    cache_key = f"news_{request.symbol}"
    if cache_key in cache:
        return {"news": cache[cache_key]}

    articles = []
    try:
        async with Mcp3ClientSession() as session:
            news_data = await session.fetch_news(
                symbol=request.symbol,
                sources=["yahoo_finance", "bloomberg", "reuters"],
                max_items=5
            )
            articles = [
                {
                    "text": item["content"],
                    "sentiment": item.get("sentiment", "neutral")
                }
                for item in news_data
            ]
    except Exception:
        sentiment_analyzer = pipeline("sentiment-analysis")
        news = await fetch_news(request.symbol)
        newsapi_articles = await fetch_newsapi(request.symbol)
        news = (news.split("\n") if news else []) + newsapi_articles
        articles = [
            {
                "text": text,
                "sentiment": sentiment_analyzer(text)[0]["label"].lower()
            }
            for text in news if text
        ]

    formatted_news = [f"{article['text']} (Sentiment: {article['sentiment']})" for article in articles]
    cache[cache_key] = formatted_news
    return {"news": formatted_news}