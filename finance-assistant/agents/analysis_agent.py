from pydantic import BaseModel
import logging
from .base_agent import create_base_app

app = create_base_app("Analysis Agent")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisRequest(BaseModel):
    portfolio: dict[str, float]
    market_data: dict[str, dict]

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    try:
        # Calculate total portfolio value
        total_value = sum(shares * request.market_data[symbol]["price"] 
                         for symbol, shares in request.portfolio.items()
                         if symbol in request.market_data)
        
        # Mock sector classification
        tech_stocks = {"AAPL", "MSFT", "NVDA", "TSMC", "ASML"}
        tech_value = sum(shares * request.market_data[symbol]["price"]
                        for symbol, shares in request.portfolio.items()
                        if symbol in request.market_data and symbol in tech_stocks)
        
        # Calculate exposure percentage
        exposure = (tech_value / total_value) * 100 if total_value > 0 else 0
        
        # Mock earnings surprises
        surprises = {}
        for symbol in request.portfolio:
            if symbol in request.market_data:
                surprises[symbol] = {
                    "AAPL": 2.5,
                    "MSFT": 1.8,
                    "NVDA": 4.2,
                    "TSMC": -0.8,
                    "ASML": 3.1
                }.get(symbol, 0.0)
        
        return {
            "exposure": exposure,
            "surprises": surprises,
            "total_value": total_value,
            "tech_value": tech_value
        }
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return {"error": f"Failed to analyze portfolio: {str(e)}"}

@app.post("/run")
async def run(request: AnalysisRequest):
    return await analyze(request)