from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AnalysisRequest(BaseModel):
    portfolio: dict[str, float]
    market_data: dict[str, dict]

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    total_value = sum(shares * request.market_data[symbol]["price"] 
                      for symbol, shares in request.portfolio.items())
    tech_value = sum(shares * request.market_data[symbol]["price"] 
                     for symbol, shares in request.portfolio.items())
    exposure = (tech_value / total_value) * 100 if total_value > 0 else 0
    surprises = {
        symbol: ((data["eps_actual"] - data["eps_estimate"]) / data["eps_estimate"] * 100)
        for symbol, data in request.market_data.items() if data["eps_estimate"] != 0
    }
    return {"exposure": exposure, "surprises": surprises}