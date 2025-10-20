"""
AWS Lambda Handler for TranslateCloud API

This module serves as the entry point for AWS Lambda function execution.
It uses Mangum to adapt the FastAPI application (ASGI) to run within AWS Lambda's
event-driven environment.

Key Components:
- Mangum: ASGI adapter that translates Lambda events to/from ASGI format
- FastAPI app: The main API application defined in src/main.py
- lifespan="off": Disables FastAPI's lifespan events for Lambda cold starts

Architecture:
    API Gateway → Lambda (this handler) → FastAPI app → Routes → Services → Database

Environment:
- Runtime: Python 3.11
- Timeout: 300 seconds (5 minutes)
- Memory: 1024 MB
- Region: eu-west-1

Usage:
    This file is automatically invoked by AWS Lambda when requests arrive
    via API Gateway. The handler function translates Lambda events into
    FastAPI-compatible requests.

Performance Considerations:
- Cold start: ~1-2 seconds (includes imports and FastAPI initialization)
- Warm execution: ~50-200ms (handler overhead)
- lifespan="off" reduces cold start time by skipping FastAPI startup/shutdown events

Author: TranslateCloud Team
Last Updated: October 20, 2025
"""

# Third-party imports
from mangum import Mangum  # ASGI adapter for AWS Lambda

# Local application imports
from src.main import app  # FastAPI application instance

# ============================================================================
# AWS Lambda Handler Configuration
# ============================================================================

# Create Lambda handler using Mangum adapter
# - app: FastAPI application instance with all routes and middleware
# - lifespan="off": Disables FastAPI lifespan events (startup/shutdown hooks)
#   This improves Lambda cold start performance since Lambda manages lifecycle
handler = Mangum(app, lifespan="off")

# Note: AWS Lambda calls handler(event, context) automatically
# - event: Dict containing API Gateway request data (method, path, headers, body)
# - context: LambdaContext object with invocation metadata (request ID, timeout, etc.)
# - Returns: Dict with statusCode, headers, and body for API Gateway response
