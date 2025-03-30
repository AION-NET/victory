#   SecurityModule.py
#   Security-related functions for the AION RWX API

import logging
from typing import Optional
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from config import API_TOKEN  #   Securely load API_TOKEN (example)
from urllib.parse import unquote
import os
import shlex
import re
import time
from fastapi import FastAPI

#   --- Configuration ---
#   Rate Limiting (Example - Replace with a proper solution for production)
#   This is a placeholder; consider using FastAPI's RateLimit or similar.
RATE_LIMIT_ENABLED = False
REQUEST_HISTORY = {}  #   in-memory rate limiting - NOT production-safe
RATE_WINDOW = 60  #   Seconds
RATE_MAX_REQUESTS = 100

def setup_security(app: FastAPI):
    """
    Sets up security-related middleware and dependencies for the FastAPI app.

    Args:
        app: The FastAPI application instance.
    """
    #   Add middleware here if needed (e.g., for more advanced security)
    #   Example: app.middleware("http")(security_middleware)
    pass

def verify_api_token(request: Request):
    """
    Verifies the API token in the request headers.

    Args:
        request: The incoming request.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid or missing.
    """
    token = request.headers.get("action-api-key")
    if not token or token != API_TOKEN:
        logging.warning("Unauthorized access attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

def safe_path(base_dir: str, sub_path: str) -> str:
    """
    Constructs a safe absolute path, preventing access outside the base directory.
    Decodes URL-encoded paths.  Handles various edge cases.

    Args:
        base_dir: The base directory to restrict access to.
        sub_path
