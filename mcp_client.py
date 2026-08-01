import asyncio
import os

from dotenv import load_dotenv
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(override=True)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

PYTHON_PATH = os.getenv("PYTHON_PATH")
AVIATIONSTACK_MCP_SERVER_PATH = os.getenv("AVIATIONSTACK_MCP_SERVER_PATH")

# error handling for missing env vars
missing_env_vars = []
if not TAVILY_API_KEY:
    missing_env_vars.append("TAVILY_API_KEY")
if not PYTHON_PATH:
    missing_env_vars.append("PYTHON_PATH")
if not AVIATIONSTACK_MCP_SERVER_PATH:
    missing_env_vars.append("AVIATIONSTACK_MCP_SERVER_PATH")

if missing_env_vars:
    raise RuntimeError(
        "Missing required environment variables: " + ", ".join(missing_env_vars)
    )


mcp_client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
        },
        "aviationstack": {
            "transport": "stdio",
            "command": PYTHON_PATH,
            "args": [AVIATIONSTACK_MCP_SERVER_PATH],
        },
    }
)

tools: dict[str, BaseTool] = {}

async def initialize_mcp():
    """initialize the mcp client and discover tools only once"""
    global tools
    
    # if tools is not None, return
    if tools:
        return

    # discovery of tools
    discovered_tools = await mcp_client.get_tools()
    
    # print("\nAvailable MCP Tools:")
    # for tool in _tools:
        # print(tool.name)

    tools = {tool.name: tool for tool in discovered_tools}

async def search_hotels(query: str):
    """search hotels using the tavily mcp tool"""
    await initialize_mcp()

    tool = tools.get("tavily_search")
    if not tool:
        return "Hotel Search tool unavailable"
    
    return await tool.ainvoke({"query": query})

async def search_flights(
    origin_iata: str,
    destination_iata: str,
    limit: int = 5
):
    await initialize_mcp()

    tool = tools.get("search_flights")

    if not tool:
        return "Flight search tool unavailable."

    return await tool.ainvoke(
        {
            "dep_iata": origin_iata,
            "arr_iata": destination_iata,
            "limit": limit,
        }
    )

async def main():
    print("[mcp_client]: Initializing MCP Client and Discovering Tools")
    await initialize_mcp()
    

if __name__ == "__main__":
    asyncio.run(main())
