import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def fetch_news(symbol):
    server_params = StdioServerParameters(
        command=["python", "servers/mcp_finance_server.py"]
    )
    async with stdio_client(server_params) as (read, write):
        session = ClientSession(read, write)
        await session.initialize()
        result = await session.call_tool("fetch_news_by_symbol", {"symbol": symbol})
        return result[0].text