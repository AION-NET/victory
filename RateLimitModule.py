#   RateLimitModule.py
#   Provides rate limiting functionality for the AION RWX API (Basic In-Memory Implementation - NOT Production Ready)

import time
from typing import Dict, List
from fastapi import FastAPI, HTTPException, status, Request

#   --- Configuration ---
RATE_LIMIT_ENABLED = True  #   Enable/Disable rate limiting
RATE_WINDOW = 60  #   Seconds - Time window for checking requests
RATE_MAX_REQUESTS = 100  #   Maximum allowed requests within the window

#   --- In-Memory Request History (Replace with persistent storage for production) ---
REQUEST_HISTORY: Dict[str, List[float]] = {}  #   {client_ip: [timestamps]}

def setup_rate_limiting(app: FastAPI):
    """
    Sets up basic in-memory rate limiting middleware for the FastAPI app.
    (Replace with a proper solution like Redis for production).

    Args:
        app: The FastAPI application instance.
    """

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        client_ip = request.client.host  #   Get client IP (for basic identification)
        if RATE_LIMIT_ENABLED:
            check_rate_limit(client_ip)
        response = await call_next(request)
        return response

def check_rate_limit(client_ip: str):
    """
    Basic in-memory rate limiting (Replace with a proper solution like Redis for production).

    Args:
        client_ip: The IP address of the client.

    Raises:
        HTTPException: 429 Too Many Requests if the limit is exceeded.
    """

    now = time.time()
    if client_ip not in REQUEST_HISTORY:
        REQUEST_HISTORY[client_ip] = []

    #   Keep only requests within the time window
    REQUEST_HISTORY[client_ip] = [
        ts for ts in REQUEST_HISTORY[client_ip] if ts > now - RATE_WINDOW
    ]

    if len(REQUEST_HISTORY[client_ip]) >= RATE_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )

    REQUEST_HISTORY[client_ip].append(now)
