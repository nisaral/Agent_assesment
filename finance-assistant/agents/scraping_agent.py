from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
# Add the parent directory to the Python path so it can find the data_ingestion module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_ingestion.mcp_scraper import fetch_news

app = FastAPI()

class SymbolRequest(BaseModel):
    symbol: str

@app.post("/news")
async def get_news(request: SymbolRequest):
    return {"news": await fetch_news(request.symbol)}