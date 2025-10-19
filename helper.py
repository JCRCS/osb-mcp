from typing import Any, Optional
import httpx
import logging

# Define an asynchronous event hook to log request details
async def log_request(request: httpx.Request):
    logging.info(f"Request Method: {request.method}")
    logging.info(f"Request URL: {request.url}")
    logging.info(f"Request Headers: {request.headers}")
    if request.content:
        try:
            logging.info(f"Request Body: {request.content.decode()}")
        except UnicodeDecodeError:
            logging.info(f"Request Body (binary): {request.content}")
    else:
        logging.info("Request Body: None")

# Helper function to perform an HTTP GET request with error handling
async def fetch_json(
    url: str,
    method: str = "GET",
    json_data: dict[str, Any] | list[dict[str, Any]]| None = None,
    timeout: float = 10.0
) -> dict:
    async with httpx.AsyncClient(timeout=timeout, event_hooks={"request": [log_request]}) as client:
        try:
            response = await client.request(method, url, json=json_data)
            logging.error(f"XXXXThe request is{json_data}")
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except httpx.TimeoutException:
            logging.error("The request timed out.")
            return {"error": "Request timed out."}
        except httpx.HTTPStatusError as exc:
            logging.error(f"HTTP error occurred: {exc}")
            return {"error": f"HTTP error: {exc.response.status_code}"}
        except httpx.RequestError as exc:
            logging.error(f"An error occurred while requesting {exc.request.url!r}.")
            return {"error": "An error occurred during the request."}