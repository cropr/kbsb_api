# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
import hashlib
import asyncio
from jose import JWTError, ExpiredSignatureError
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timedelta, date
from sqlalchemy.orm import sessionmaker
from typing import cast, Any, IO, Union

from reddevil.core import (
    RdNotAuthorized,
    RdBadRequest,
    get_settings,
    jwt_getunverifiedpayload,
    jwt_verify,
)
from kbsb.member import (
    LoginValidator,
    Member,
    ActiveMember,
    ActiveMemberList,
)
from kbsb.member.mysql_member import (
    mysql_query_password,
    mysql_getmember,
    mysql_getactivemember,
    mysql_getclubmembers,
)
from kbsb.member.mongo_member import (
    mongodb_query_password,
    mongodb_getmember,
    mongodb_getactivemember,
    mongodb_getclubmembers,
)

from kbsb.core.db import mysql_engine

logger = logging.getLogger(__name__)


def login(ol: LoginValidator) -> str:
    """
    use the mysql database to mimic the old php login procedure
    return a JWT token
    """
    settings = get_settings()
    if settings.MEMBERDB == "oldmysql":
        return mysql_query_password(ol.idnumber, ol.password)
    elif settings.MEMBERDB == "mongodb":
        return mongodb_query_password(ol.idnumber, ol.password)
    raise NotImplemented


def validate_membertoken(auth: HTTPAuthorizationCredentials) -> int:
    """
    checks a JWT token for validity
    return an idnumber if the token is correctly validated
    if token is not valid the function :
        - either returns None
        - either raise RdNotAuthorized if raising is set
    """
    settings = get_settings()
    token = auth.credentials if auth else None
    if not token:
        raise RdNotAuthorized(description="MissingToken")
    if settings.TOKEN.get("nocheck"):
        logger.debug("nocheck return token 0")
        return 0
    try:
        payload = jwt_getunverifiedpayload(token)
    except JWTError:
        raise RdNotAuthorized(description="BadToken")
    username = payload.get("sub")
    try:
        jwt_verify(token, settings.JWT_SECRET + SALT)
    except ExpiredSignatureError as e:
        logger.debug(f"expired {e}")
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError as e:
        logger.debug(f"jwt error {e}")
        raise RdNotAuthorized(description="BadToken")
    return username


async def get_member(idbel: Union[str, int]) -> Member:
    settings = get_settings()
    try:
        nidbel = int(idbel)
    except Exception:
        raise RdBadRequest(description="idbelNotInteger")
    if settings.MEMBERDB == "oldmysql":
        return await mysql_getmember(nidbel)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_getmember(nidbel)
    raise NotImplemented


async def get_clubmembers(idclub: int, active: bool = True) -> ActiveMemberList:
    """
    find all members of a club
    """
    settings = get_settings()
    if settings.MEMBERDB == "oldmysql":
        return await mysql_getclubmembers(idclub, active)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_getclubmembers(idclub, active)
    raise NotImplemented


async def get_activemember(idbel: int) -> ActiveMember:
    settings = get_settings()
    try:
        nidbel = int(idbel)
    except Exception:
        raise RdBadRequest(description="idbelNotInteger")
    if settings.MEMBERDB == "oldmysql":
        return await mysql_getactivemember(nidbel)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_getactivemember(nidbel)
    raise NotImplemented
