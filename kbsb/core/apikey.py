# copyright Chessdevil Consulting BVBA 2018 - 2024
# copyright Ruben Decrop 2020 - 2024

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from reddevil.core import get_settings, RdNotAuthorized

settings = get_settings()
api_key_header = APIKeyHeader(name="X-API-Key")


def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header == settings.API_KEY:
        return api_key_header


raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or missing API Key",
)
