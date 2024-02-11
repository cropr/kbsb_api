# copyright Chessdevil Consulting BVBA 2018 - 2024
# copyright Ruben Decrop 2020 - 2024


from fastapi.security import APIKeyHeader
from reddevil.core import get_settings, RdNotAuthorized

header_schema = APIKeyHeader(name="X-API-Key")
settings = get_settings()


def validate_header(apikey: str):
    if settings.API_KEY != apikey:
        raise RdNotAuthorized(description="InvalidKey")
