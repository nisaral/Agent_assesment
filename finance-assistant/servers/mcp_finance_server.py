import asyncio
import aiohttp
import json
from typing import Any, Dict, List
import mcp.server.stdio
from mcp import types
from mcp.server import Server
from bs4 import BeautifulSoup

server = Server("finance-news")

class FinanceNewsManager:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        if self.session:
            await self.session.close()

news_manager = FinanceNewsManager()

@server.list_resources()
async def list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            uri="finance://news_feed",
            name="Financial News Feed",
            description="Latest news articles for Asia tech stocks",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "finance://news_feed":
        session = await news_manager.get_session()
        url = "https://finance.yahoo.com/news"
        async with session.get(url) as response:
            data = await response.text()
            soup = BeautifulSoup(data, "html.parser")
            articles = [item.text for item in soup.find_all("h3")[:3]]
            return json.dumps({"news": articles})
    raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="fetch_news_by_symbol",
            description="Fetch news articles for a specific stock symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"}
                },
                "required": ["symbol"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    session = await news_manager.get_session()
    if name == "fetch_news_by_symbol":
        symbol = arguments["symbol"]
        url = f"https://finance.yahoo.com/quote/{symbol}/news"
        try:
            async with session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                articles = [item.text for item in soup.find_all("h3")[:3]]
                return [types.TextContent(
                    type="text",
                    text="\n".join(articles) if articles else "No news found"
                )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error fetching news: {str(e)}"
            )]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    finally:
        await news_manager.close_session()

if __name__ == "__main__":
    asyncio.run(main())