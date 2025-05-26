import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langgraph.graph import StateGraph, END
import aiohttp
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

class State(BaseModel):
    query: str = ""
    market_data: dict = {}
    news: list = []
    retrieved: list = []
    analysis: dict = {}
    narrative: str = ""
    audio_output: str = ""
    focus_region: str = "global"
    focus_sector: str = None

async def api_node(state: State):
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8001/fetch", json={
            "symbols": ["AAPL", "MSFT", "NVDA", "TSMC", "ASML"],
            "indices": ["^GSPC", "^IXIC", "^N225", "^STOXX"],
            "currencies": ["EURUSD", "JPYUSD", "CNYUSD"],
            "commodities": ["GC=F", "CL=F", "HG=F"]
        }) as resp:
            state.market_data = await resp.json()
    return state

async def scraping_node(state: State):
    async with aiohttp.ClientSession() as session:
        news = []
        for symbol in ["AAPL", "MSFT", "NVDA", "TSMC", "ASML"]:
            async with session.post("http://localhost:8002/news", json={"symbol": symbol}) as resp:
                news.extend((await resp.json())["news"].split("\n"))
        state.news = news
    return state

async def retriever_node(state: State):
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8003/retrieve", json={"documents": state.news, "query": state.query}) as resp:
            state.retrieved = [item["content"] for item in await resp.json()]
    return state

async def analysis_node(state: State):
    portfolio = {"AAPL": 100, "MSFT": 80, "NVDA": 50, "TSMC": 60, "ASML": 40}
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8004/analyze", json={"portfolio": portfolio, "market_data": state.market_data["stocks"]}) as resp:
            state.analysis = await resp.json()
    return state

async def language_node(state: State):
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8005/generate", json={
            "exposure": state.analysis["exposure"],
            "focus_region": state.focus_region,
            "focus_sector": state.focus_sector,
            "surprises": state.analysis["surprises"],
            "regional_performance": {"North America": 1.2, "Europe": -0.8, "Asia Pacific": 2.1},  # Placeholder
            "sector_performance": {"Technology": 2.3, "Semiconductors": 4.1, "Software": 1.8},  # Placeholder
            "documents": state.retrieved,
            "previous_exposure": state.analysis["exposure"] - 2.7,  # Simulated change
            "key_holdings": ["AAPL", "MSFT", "NVDA", "TSMC", "ASML"],
            "sector_breakdown": {"Semiconductors": 35.2, "Software": 28.8, "Hardware": 22.1, "Services": 13.9},  # Placeholder
            "regional_breakdown": {"North America": 52.3, "Asia Pacific": 31.2, "Europe": 16.5},  # Placeholder
            "major_indices": state.market_data["indices"],
            "currency_moves": state.market_data["currencies"],
            "commodity_prices": state.market_data["commodities"]
        }) as resp:
            response = await resp.json()
            state.narrative = response["narrative"]
    return state

async def voice_node(state: State):
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8006/tts", json={"text": state.narrative}) as resp:
            state.audio_output = (await resp.json())["audio_file"]
    return state

workflow = StateGraph(State)
workflow.add_node("api", api_node)
workflow.add_node("scraping", scraping_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("language", language_node)
workflow.add_node("voice", voice_node)
workflow.add_edge("api", "analysis")
workflow.add_edge("scraping", "retriever")
workflow.add_edge("retriever", "analysis")
workflow.add_edge("analysis", "language")
workflow.add_edge("language", "voice")
workflow.add_edge("voice", END)
workflow.set_entry_point("api")
graph = workflow.compile()

@app.post("/process_query")
async def process_query(query: str, focus_region: str = "global", focus_sector: str = None):
    state = State(query=query, focus_region=focus_region, focus_sector=focus_sector)
    return await graph.ainvoke(state)