from langchain_protocol import Annotated
from mcp.server.fastmcp import FastMCP
import requests
import os

from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Custom Aviation Stack Server")

AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# error handling for missing env vars
if not AVIATIONSTACK_API_KEY:
    raise RuntimeError("Missing required environment variable: AVIATIONSTACK_API_KEY")

@mcp.tool(description="Get flight information from source to destination.")
def search_flights(
    dep_iata: Annotated[str, "Departure IATA code"], 
    arr_iata: Annotated[str, "Arrival IATA code"], 
    limit: Annotated[int, "Number of flights to return"]
) -> dict:
    """
    Returns flight information for a route.

    Example:
        search_flights("AMD", "DXB", 5)
    """
    response = requests.get(
        "https://api.aviationstack.com/v1/flights",
        params={
            "dep_iata": dep_iata,
            "arr_iata": arr_iata,
            "limit": limit,
            "access_key": AVIATIONSTACK_API_KEY
        }
    )

    data = response.json()

    if response.status_code != 200:
        return data

    return {
        "flights": data["data"]
    }


if __name__ == "__main__":
    # needed when running mcp server in a separate process
    mcp.run() 
