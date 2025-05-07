# mcp_google_search_server.py
import os
from typing import List, Dict
from serpapi.google_search import GoogleSearch   # <-- note the submodule path
# from fastmcp import mcp

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Google-search", description="google search server proving looks into internet")


SERPAPI_KEY = "1470c630c504b68afa02aafe583e81b03205313f23af9ec2ac1476780b0fdeca"

@mcp.tool()
def search(query: str, num: int = 5) -> List[Dict]:
    """Search Google using SerpApi and return top organic results."""
    print(SERPAPI_KEY)
    print(query)
    print(num)
    search = GoogleSearch({
        "q": query,
        "num": num,
        "api_key": SERPAPI_KEY
    })
    print(search)
    results = search.get_dict()
    return results.get("organic_results", [])

if __name__ == "__main__":
    # This will start an stdio‐based MCP server
    mcp.run()