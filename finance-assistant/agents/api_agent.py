import aiohttp
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging
from cachetools import TTLCache
from .base_agent import create_base_app

load_dotenv()
app = create_base_app("API Agent")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache = TTLCache(maxsize=100, ttl=300)

class TickerRequest(BaseModel):
    ticker: str

async def fetch_alpha_vantage_data(symbols: list):
    cache_key = ",".join(sorted(symbols))
    if cache_key in cache:
        logger.info(f"Returning cached data for {cache_key}")
        return cache[cache_key]
    
    # Use mock data for now
    data = {
        "stocks": {
            "AAPL": {"price": 150.0, "volume": 1000000},
            "MSFT": {"price": 280.0, "volume": 900000},
            "NVDA": {"price": 400.0, "volume": 800000},
            "TSMC": {"price": 90.0, "volume": 700000},
            "ASML": {"price": 600.0, "volume": 600000}
        },
        "indices": {"^GSPC": {"value": 5500.0}},
        "currencies": {"EURUSD": {"rate": 1.1}},
        "commodities": {"GC=F": {"price": 2500.0}}
    }
    
    cache[cache_key] = data
    return data

@app.post("/run")
async def run(request: TickerRequest):
    try:
        symbols = request.ticker.split(",")
        return await fetch_alpha_vantage_data(symbols)
    except Exception as e:
        logger.error(f"API run error: {e}")
        return {"error": str(e)}