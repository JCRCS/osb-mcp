import asyncio
import logging

from fastapi.responses import StreamingResponse
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
from fastapi import Request
import httpx
from mcp.server.fastmcp import FastMCP

API_URL = "http://127.0.0.1:9000"
OPEN_STUDY_BUILDER_ULR = "http://127.0.0.1:9001"
mcp = FastMCP("API-Proxy")

@mcp.resource("greeting://")
def get_greeting() -> str:
    resp = httpx.get(f"{API_URL}/greet")
    return resp.json()["message"]

@mcp.tool()
def set_info(name: str, country: str) -> dict:
    resp = httpx.post(f"{API_URL}/info", json={"name": name, "country": country})
    return resp.json()

@mcp.tool()
def get_studies() -> dict:
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_ULR}/studies")
    return resp.json()

@mcp.resource("country://{name}")
def get_country(name: str) -> str:
    resp = httpx.get(f"{API_URL}/country/{name}")
    if resp.status_code == 404:
        return f"No info for {name}"
    return resp.json()["country"]

logging.info("Starting FastMCP Server via STDIO...")

if __name__ == "__main__":
    logging.info("FastMCP Server is now listening for connections over STDIO.")
    # exporta un endpoint SSE en http://127.0.0.1:6274/sse
    mcp.run(transport="stdio")
    # mcp.run()
