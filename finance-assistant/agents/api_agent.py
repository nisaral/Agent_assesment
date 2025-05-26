import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI
from pydantic import BaseModel
from data_ingestion.api import fetch_market_data
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables
load_dotenv()

app = FastAPI()

class SymbolsRequest(BaseModel):
    symbols: List[str]
    indices: Optional[List[str]] = None
    currencies: Optional[List[str]] = None
    commodities: Optional[List[str]] = None

@app.post("/fetch")
async def fetch_data(request: SymbolsRequest):
    return fetch_market_data(
        request.symbols,
        indices=request.indices,
        currencies=request.currencies,
        commodities=request.commodities
    )