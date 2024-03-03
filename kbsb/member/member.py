# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
from jose import JWTError, ExpiredSignatureError
from fastapi.security import HTTPAuthorizationCredentials
from typing import List

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
    AnonMember,
    SALT,
    OldUserPasswordValidator,
)
from kbsb.member.mysql_member import (
    mysql_login,
    mysql_anon_getmember,
    mysql_mgmt_getmember,
    mysql_anon_getclubmembers,
    mysql_mgmt_getclubmembers,
    mysql_anon_belid_from_fideid,
    mysql_anon_getfidemember,
    mysql_old_userpassword,
)
from kbsb.member.mongo_member import (
    mongodb_login,
    mongodb_anon_getmember,
    mongodb_mgmt_getmember,
    mongodb_anon_getclubmembers,
    mongodb_mgmt_getclubmembers,
    mongodb_anon_belid_from_fideid,
    mongodb_anon_getfidemember,
    mongodb_old_userpassword,
)


logger = logging.getLogger(__name__)


async def login(ol: LoginValidator) -> str:
    """
    use the mysql database to mimic the old php login procedure
    return a JWT token
    """
    settings = get_settings()
    if settings.MEMBERDB == "oldmysql":
        return await mysql_login(ol.idnumber, ol.password)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_login(ol.idnumber, ol.password)
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


async def mgmt_getmember(idbel: str | int) -> Member:
    settings = get_settings()
    try:
        nidbel = int(idbel)
    except Exception:
        raise RdBadRequest(description="idbelNotInteger")
    if settings.MEMBERDB == "oldmysql":
        return await mysql_mgmt_getmember(nidbel)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_mgmt_getmember(nidbel)
    raise NotImplemented


async def mgmt_getclubmembers(idclub: int, active: bool) -> List[Member]:
    """
    find all members of a club
    """
    settings = get_settings()
    if settings.MEMBERDB == "oldmysql":
        mm = await mysql_mgmt_getclubmembers(idclub, active)
        logger.debug(f"3 mm {mm[0:3]}")
        return mm
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_mgmt_getclubmembers(idclub, active)
    raise NotImplemented


async def anon_getclubmembers(idclub: int, active: bool) -> List[AnonMember]:
    """
    find all members of a club
    """
    settings = get_settings()
    if settings.MEMBERDB == "oldmysql":
        return await mysql_anon_getclubmembers(idclub, active)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_anon_getclubmembers(idclub, active)
    raise NotImplemented


async def anon_getmember(idbel: int) -> AnonMember:
    settings = get_settings()
    if settings.MEMBERDB == "oldmysql":
        return await mysql_anon_getmember(idbel)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_anon_getmember(idbel)
    raise NotImplemented


async def anon_getfidemember(idfide: int) -> AnonMember:
    settings = get_settings()
    if settings.MEMBERDB == "oldmysql":
        return await mysql_anon_getfidemember(idfide)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_anon_getfidemember(idfide)
    raise NotImplemented


async def anon_belid_from_fideid(idfide: int) -> int:
    settings = get_settings()
    if settings.MEMBERDB == "oldmysql":
        return await mysql_anon_belid_from_fideid(idfide)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_anon_belid_from_fideid(idfide)
    raise NotImplemented


async def old_userpassword(oupw: OldUserPasswordValidator) -> None:
    settings = get_settings()
    if settings.MEMBERDB == "oldmysql":
        return await mysql_old_userpassword(oupw)
    elif settings.MEMBERDB == "mongodb":
        return await mongodb_mgmt_getmember(oupw)
    raise NotImplemented
