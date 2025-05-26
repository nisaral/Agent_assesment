import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

# Load environment variables
load_dotenv()

app = FastAPI()
llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))

class MarketRegion(str, Enum):
    GLOBAL = "global"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    EMERGING_MARKETS = "emerging_markets"
    LATIN_AMERICA = "latin_america"

class MarketSector(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIALS = "financials"
    ENERGY = "energy"
    CONSUMER = "consumer"
    INDUSTRIALS = "industrials"
    REAL_ESTATE = "real_estate"
    UTILITIES = "utilities"
    MATERIALS = "materials"
    TELECOMMUNICATIONS = "telecommunications"

class LanguageRequest(BaseModel):
    # Core allocation data
    exposure: float
    focus_region: str = "global"
    focus_sector: Optional[str] = None
    
    # Performance data
    surprises: dict  # Company/Symbol: surprise %
    regional_performance: Optional[Dict[str, float]] = None
    sector_performance: Optional[Dict[str, float]] = None
    
    # News and context
    documents: list[str]
    
    # Portfolio context
    previous_exposure: Optional[float] = None
    market_sentiment: Optional[str] = None
    #key holdings
    sector_breakdown: Optional[dict] = None
    #regional breakdown
    # Market conditions
    major_indices: Optional[Dict[str, float]] = None
    currency_moves: Optional[Dict[str, float]] = None
    commodity_prices: Optional[Dict[str, float]] = None

@app.post("/generate")
async def generate_narrative(request: LanguageRequest):
    
    # Dynamic prompt template for global market briefs
    prompt = ChatPromptTemplate.from_template(
        """
You are a senior portfolio analyst providing a comprehensive market brief to institutional investors. 
Analyze the provided data and deliver a professional, actionable market commentary.

**PORTFOLIO CONTEXT:**
- Current {focus_area} Allocation: {exposure:.2f}% of AUM
- Previous Day Allocation: {previous_exposure}% 
- Change: {exposure_change}
- Focus Region: {focus_region}
- Focus Sector: {focus_sector}

**HOLDINGS & ALLOCATION:**
- Key Holdings: {key_holdings}
- Sector Breakdown: {sector_breakdown}
- Regional Breakdown: {regional_breakdown}

**MARKET PERFORMANCE:**
{performance_summary}

**EARNINGS & CORPORATE DEVELOPMENSTS:**
{earnings_analysis}

**GLOBAL MARKET SNAPSHOT:**
{market_indices}

**CURRENCY & COMMODITIES:**
{fx_commodities}

**NEWS & DEVELOPMENTS:**
{news_summary}

**ANALYSIS FRAMEWORK:**
Structure your response professionally as follows:

1. **POSITION OVERVIEW** (2-3 sentences)
   - Current allocation level and directional change
   - Overall portfolio risk profile for {focus_area}

2. **PERFORMANCE DRIVERS** (3-4 sentences)
   - Key regional/sector performance trends
   - Major earnings impacts and corporate developments
   - Cross-asset correlations and themes

3. **GLOBAL CONTEXT** (2-3 sentences)
   - Broader market environment and key indices
   - Currency/commodity impacts on positioning
   - Geopolitical or macroeconomic factors

4. **RISK FACTORS** (2-3 sentences)
   - Current risk level assessment (Low/Moderate/High/Elevated)
   - Key vulnerabilities and stress scenarios
   - Correlation risks and concentration concerns

5. **TACTICAL OUTLOOK** (2-3 sentences)
   - Near-term positioning recommendations
   - Key events, data releases, or catalysts to monitor
   - Potential rebalancing considerations

**DELIVERY GUIDELINES:**
- Professional, institutional-grade language
- Quantitative where possible with specific figures
- Actionable insights for portfolio management
- Risk-aware perspective
- Maximum 250 words total
- Include confidence levels for key assessments

**SESSION CONTEXT:**
Date: {current_date}
Market Focus: {focus_area} Markets
Trading Environment: {trading_session}
Analysis Timeframe: Intraday to 1-week outlook
""")
    
    # Process and format the data
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Determine focus area description
    focus_area = f"{request.focus_region.replace('_', ' ').title()}"
    if request.focus_sector:
        focus_area += f" {request.focus_sector.replace('_', ' ').title()}"
    
    # Calculate exposure change
    exposure_change = ""
    if request.previous_exposure:
        change = request.exposure - request.previous_exposure
        direction = "increased" if change > 0 else "decreased"
        exposure_change = f"{direction} {abs(change):.1f}% from yesterday"
    else:
        exposure_change = "baseline measurement"
    
    # Format performance data
    performance_items = []
    if request.regional_performance:
        regional_items = [f"{region}: {perf:+.1f}%" for region, perf in request.regional_performance.items()]
        performance_items.append(f"Regional: {', '.join(regional_items)}")
    
    if request.sector_performance:
        sector_items = [f"{sector}: {perf:+.1f}%" for sector, perf in request.sector_performance.items()]
        performance_items.append(f"Sectoral: {', '.join(sector_items)}")
    
    performance_summary = "; ".join(performance_items) if performance_items else "Performance data pending"
    
    # Format earnings surprises
    if request.surprises:
        earnings_items = []
        for company, surprise in request.surprises.items():
            direction = "beat" if surprise > 0 else "missed"
            magnitude = "significantly" if abs(surprise) > 5 else "modestly" if abs(surprise) > 2 else "slightly"
            earnings_items.append(f"{company} {magnitude} {direction} by {abs(surprise):.1f}%")
        earnings_analysis = "; ".join(earnings_items)
    else:
        earnings_analysis = "No major earnings surprises reported"
    
    # Format market indices
    if request.major_indices:
        index_items = [f"{index}: {change:+.1f}%" for index, change in request.major_indices.items()]
        market_indices = ", ".join(index_items)
    else:
        market_indices = "Major indices data unavailable"
    
    # Format FX and commodities
    fx_comm_items = []
    if request.currency_moves:
        fx_items = [f"{curr}: {move:+.1f}%" for curr, move in request.currency_moves.items()]
        fx_comm_items.append(f"FX: {', '.join(fx_items)}")
    
    if request.commodity_prices:
        comm_items = [f"{comm}: {price:+.1f}%" for comm, price in request.commodity_prices.items()]
        fx_comm_items.append(f"Commodities: {', '.join(comm_items)}")
    
    fx_commodities = "; ".join(fx_comm_items) if fx_comm_items else "Limited cross-asset data"
    
    # Process news documents
    news_summary = " | ".join(request.documents[:5]) if request.documents else "No significant news developments"
    
    # Format optional fields with better defaults
    key_holdings = ", ".join(request.key_holdings[:8]) if request.key_holdings else "Portfolio holdings not specified"
    
    sector_breakdown = ""
    if request.sector_breakdown:
        sector_items = [f"{sector}: {weight:.1f}%" for sector, weight in sorted(request.sector_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]]
        sector_breakdown = "; ".join(sector_items)
    else:
        sector_breakdown = "Sector allocation not provided"
    
    regional_breakdown = ""
    if request.regional_breakdown:
        regional_items = [f"{region}: {weight:.1f}%" for region, weight in sorted(request.regional_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]]
        regional_breakdown = "; ".join(regional_items)
    else:
        regional_breakdown = "Regional allocation not provided"
    
    # Determine trading session
    hour = datetime.now().hour
    if 6 <= hour < 12:
        trading_session = "Pre-market / Asian Session"
    elif 12 <= hour < 18:
        trading_session = "European / US Pre-market"
    elif 18 <= hour < 24:
        trading_session = "US Market Hours"
    else:
        trading_session = "After Hours / Asian Pre-market"
    
    # Generate the response
    formatted_prompt = prompt.format(
        focus_area=focus_area,
        exposure=request.exposure,
        previous_exposure=request.previous_exposure or "N/A",
        exposure_change=exposure_change,
        focus_region=request.focus_region.replace('_', ' ').title(),
        focus_sector=request.focus_sector.replace('_', ' ').title() if request.focus_sector else "Broad Market",
        performance_summary=performance_summary,
        earnings_analysis=earnings_analysis,
        market_indices=market_indices,
        fx_commodities=fx_commodities,
        news_summary=news_summary,
        current_date=current_date,
        key_holdings=key_holdings,
        sector_breakdown=sector_breakdown,
        regional_breakdown=regional_breakdown,
        trading_session=trading_session
    )
    
    response = llm.invoke(formatted_prompt)
    
    return {
        "narrative": response.content,
        "metadata": {
            "timestamp": current_date,
            "focus_area": focus_area,
            "exposure": request.exposure,
            "exposure_change": exposure_change,
            "earnings_count": len(request.surprises) if request.surprises else 0,
            "trading_session": trading_session,
            "region": request.focus_region,
            "sector": request.focus_sector
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "global_market_brief_generator"}

# Sample endpoints for different market focuses
@app.get("/sample/global-tech")
async def sample_global_tech():
    sample_request = LanguageRequest(
        exposure=28.5,
        focus_region=MarketRegion.GLOBAL,
        focus_sector=MarketSector.TECHNOLOGY,
        surprises={"AAPL": 3.2, "MSFT": 1.8, "NVDA": 8.5, "TSMC": 4.2, "ASML": -1.3},
        regional_performance={"North America": 1.2, "Europe": -0.8, "Asia Pacific": 2.1},
        sector_performance={"Technology": 2.3, "Semiconductors": 4.1, "Software": 1.8},
        documents=[
            "AI chip demand driving semiconductor outperformance globally",
            "Fed officials signal cautious approach to rate cuts",
            "European tech regulation creating headwinds for US platforms",
            "Chinese tech earnings showing resilience amid economic slowdown"
        ],
        previous_exposure=25.8,
        key_holdings=["AAPL", "MSFT", "NVDA", "GOOGL", "TSMC", "ASML", "SAP"],
        sector_breakdown={"Semiconductors": 35.2, "Software": 28.8, "Hardware": 22.1, "Services": 13.9},
        regional_breakdown={"North America": 52.3, "Asia Pacific": 31.2, "Europe": 16.5},
        major_indices={"S&P 500": 0.8, "NASDAQ": 1.4, "Nikkei": 2.1, "STOXX 600": -0.3},
        currency_moves={"USD/EUR": 0.2, "USD/JPY": -0.8, "USD/CNY": 0.1},
        commodity_prices={"Gold": -0.5, "Oil": 1.2, "Copper": 0.8}
    )
    return await generate_narrative(sample_request)

@app.get("/sample/emerging-markets")
async def sample_emerging_markets():
    sample_request = LanguageRequest(
        exposure=15.7,
        focus_region=MarketRegion.EMERGING_MARKETS,
        surprises={"Taiwan Semi": 4.2, "Tencent": -1.8, "Vale": 2.3, "Infosys": 1.9},
        regional_performance={"China": -1.2, "India": 2.8, "Brazil": 0.5, "Mexico": 1.1},
        documents=[
            "China PMI data shows mixed signals for manufacturing recovery",
            "Indian central bank maintains hawkish stance on inflation",
            "Brazil commodity exports surge on Chinese demand",
            "EM currencies under pressure from strong dollar"
        ],
        previous_exposure=14.2,
        key_holdings=["Taiwan Semi", "Tencent", "Infosys", "Vale", "Itau", "Naspers"],
        major_indices={"MSCI EM": -0.6, "CSI 300": -1.8, "Sensex": 1.9, "Bovespa": 0.3},
        currency_moves={"CNY": -0.3, "INR": -0.2, "BRL": 0.8, "MXN": 0.4}
    )
    return await generate_narrative(sample_request)

@app.get("/sample/us-financials")
async def sample_us_financials():
    sample_request = LanguageRequest(
        exposure=12.4,
        focus_region=MarketRegion.NORTH_AMERICA,
        focus_sector=MarketSector.FINANCIALS,
        surprises={"JPM": 2.1, "BAC": 1.8, "WFC": -0.9, "GS": 3.4},
        documents=[
            "Bank earnings reflect improving net interest margins",
            "Credit loss provisions remain benign across major banks",
            "Fed stress test results support dividend increases",
            "Regional bank consolidation accelerating"
        ],
        previous_exposure=11.8,
        key_holdings=["JPM", "BAC", "WFC", "C", "GS", "MS"],
        major_indices={"S&P 500": 0.5, "Financial Select Sector": 1.2},
        commodity_prices={"10Y Treasury": 4.25}
    )
    return await generate_narrative(sample_request)