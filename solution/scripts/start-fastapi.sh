#!/bin/sh

PORT=${SERVER_PORT:-8080}

uvicorn app.adapters.fastapi.main:fastapi_app --host REDACTED --port "$PORT" --workers 3
