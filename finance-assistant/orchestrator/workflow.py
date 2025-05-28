import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langgraph.graph import StateGraph, END
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import aiohttp
from pydantic import BaseModel
from dotenv import load_dotenv
import re
from agents.base_agent import create_base_app

load_dotenv()
app = create_base_app("Orchestrator")

def read_service_ports(log_file="service_ports.log"):
    ports = {
        "api_agent": 8001,
        "scraping_agent": 6002,
        "retriever_agent": 6003,
        "analysis_agent": 6004,
        "language_agent": 6005,
        "voice_agent": 6006
    }
    try:
        with open(log_file, "r") as f:
            log_content = f.read()
            for module, default_port in ports.items():
                match = re.search(rf"{module}: http://localhost:(\d+)", log_content)
                if match:
                    ports[module] = int(match.group(1))
    except FileNotFoundError:
        pass
    return ports

service_ports = read_service_ports()

class State(BaseModel):
    query: str = ""
    portfolio: str = ""
    market_data: dict = {}
    news: list = []
    retrieved: list = []
    analysis_result: dict = {}
    narrative: str = ""
    audio_output: str = ""
    error: str = ""

class QueryRequest(BaseModel):
    query: str
    portfolio: str

async def api_node(state: State):
    stocks = [s.split(":")[0] for s in state.portfolio.split(", ") if s] or ["AAPL", "MSFT", "NVDA", "TSMC", "ASML"]
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://localhost:{service_ports['api_agent']}/run", json={
                "ticker": ",".join(stocks)
            }) as resp:
                if not resp.ok:
                    raise HTTPException(status_code=resp.status, detail="API service error")
                state.market_data = await resp.json()
    except Exception as e:
        state.error = f"API service error: {str(e)}"
    return state

async def scraping_node(state: State):
    if state.error:
        return state
    stocks = [s.split(":")[0] for s in state.portfolio.split(", ") if s] or ["AAPL", "MSFT", "NVDA", "TSMC", "ASML"]
    try:
        async with aiohttp.ClientSession() as session:
            news = []
            for symbol in stocks:
                async with session.post(f"http://localhost:{service_ports['scraping_agent']}/run", json={"company": symbol}) as resp:
                    if not resp.ok:
                        raise HTTPException(status_code=resp.status, detail="Scraping service error")
                    news.extend((await resp.json())["news"])
            state.news = news
    except Exception as e:
        state.error = f"Scraping service error: {str(e)}"
    return state

async def retriever_node(state: State):
    if state.error:
        return state
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://localhost:{service_ports['retriever_agent']}/run", json={
                "documents": state.news,
                "query": state.query
            }) as resp:
                if not resp.ok:
                    raise HTTPException(status_code=resp.status, detail="Retriever service error")
                results = await resp.json()
                state.retrieved = [item["content"] for item in results]
                state.confidence = min([item["score"] for item in results], default=0.5)
    except Exception as e:
        state.error = f"Retriever service error: {str(e)}"
    return state

async def analysis_node(state: State):
    if state.error:
        return state
    portfolio = {s.split(":")[0]: int(s.split(":")[1]) for s in state.portfolio.split(", ") if s and ":" in s}
    if not portfolio:
        portfolio = {"AAPL": 100, "MSFT": 80, "NVDA": 50, "TSMC": 60, "ASML": 40}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://localhost:{service_ports['analysis_agent']}/run", json={
                "portfolio": portfolio,
                "market_data": state.market_data["stocks"]
            }) as resp:
                if not resp.ok:
                    raise HTTPException(status_code=resp.status, detail="Analysis service error")
                state.analysis_result = await resp.json()
    except Exception as e:
        state.error = f"Analysis service error: {str(e)}"
    return state

async def language_node(state: State):
    if state.error:
        return state
    if state.confidence < 0.3:
        state.narrative = "Could you clarify your query? The retrieved information is insufficient."
        return state
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://localhost:{service_ports['language_agent']}/run", json={
                "exposure": state.analysis_result["exposure"],
                "surprises": state.analysis_result["surprises"],
                "regional_performance": {"North America": 1.2, "Europe": -0.8, "Asia Pacific": 2.1},
                "sector_performance": {"Technology": 2.3, "Semiconductors": 4.1, "Software": 1.8},
                "documents": state.retrieved,
                "previous_exposure": state.analysis_result["exposure"] - 2.7,
                "key_holdings": [s.split(":")[0] for s in state.portfolio.split(", ") if s] or ["AAPL", "MSFT", "NVDA", "TSMC", "ASML"],
                "sector_breakdown": {"Semiconductors": 35.2, "Software": 28.8, "Hardware": 22.1, "Services": 13.9},
                "regional_breakdown": {"North America": 52.3, "Asia Pacific": 31.2, "Europe": 16.5},
                "major_indices": state.market_data["indices"],
                "currency_moves": state.market_data["currencies"],
                "commodity_prices": state.market_data["commodities"]
            }) as resp:
                if not resp.ok:
                    raise HTTPException(status_code=resp.status, detail="Language service error")
                response = await resp.json()
                state.narrative = response["narrative"]
    except Exception as e:
        state.error = f"Language service error: {str(e)}"
    return state

async def voice_node(state: State):
    if state.error:
        return state
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://localhost:{service_ports['voice_agent']}/run", json={"text": state.narrative}) as resp:
                if not resp.ok:
                    raise HTTPException(status_code=resp.status, detail="Voice service error")
                state.audio_output = (await resp.json())["audio_file"]
    except Exception as e:
        state.error = f"Voice service error: {str(e)}"
    return state

workflow = StateGraph(State)
workflow.add_node("api", api_node)
workflow.add_node("scraping", scraping_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("analysis_processor", analysis_node)
workflow.add_node("language", language_node)
workflow.add_node("voice", voice_node)
workflow.add_edge("api", "analysis_processor")
workflow.add_edge("scraping", "retriever")
workflow.add_edge("retriever", "analysis_processor")
workflow.add_edge("analysis_processor", "language")
workflow.add_edge("language", "voice")
workflow.add_edge("voice", END)
workflow.set_entry_point("api")
graph = workflow.compile()

@app.post("/process_query")
async def process_query(request: QueryRequest):
    state = State(query=request.query, portfolio=request.portfolio)
    result = await graph.ainvoke(state)
    if result.error:
        raise HTTPException(status_code=500, detail=result.error)
    return result

@app.post("/run")
async def run(request: QueryRequest):
    state = State(query=request.query, portfolio=request.portfolio)
    result = await graph.ainvoke(state)
    if result.error:
        return JSONResponse(
            status_code=500,
            content={"error": result.error, "narrative": "Sorry, there was an error processing your request."}
        )
    return {"narrative": result.narrative, "audio_file": result.audio_output}