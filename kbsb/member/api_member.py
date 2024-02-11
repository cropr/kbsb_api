# copyright Chessdevil Consulting BVBA 2018 - 2020
# copyright Ruben Decrop 2020 - 2022

# this file contains API point that map directly to the old mysql database

import logging

from fastapi import HTTPException, APIRouter, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, APIKeyHeader
from reddevil.core import RdException, bearer_schema, validate_token, get_settings
from typing import List
from kbsb.member import (
    AnonMember,
    LoginValidator,
    Member,
    OldUserPasswordValidator,
    anon_getclubmembers,
    anon_getmember,
    anon_getfidemember,
    anon_belid_from_fideid,
    login,
    mgmt_getmember,
    mgmt_getclubmembers,
    validate_membertoken,
    old_userpassword,
)
from kbsb.core.apikey import header_schema, validate_header

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/member")


@router.post("/login")
async def api_login(ol: LoginValidator) -> str:
    """
    login by using the idnumber, return a JWT token
    """
    try:
        logger.info(f"ol {ol}")
        return await login(ol)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call oldlogin")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/userpassword", include_in_schema=False, status_code=201)
async def api_set_old_userpassword(
    ol: OldUserPasswordValidator,
    apikey: str = Depends(header_schema),
):
    """
    force password on user, creates the user if he does not exist
    """
    try:
        validate_header(apikey)
        await old_userpassword(ol)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call old_userpassword")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/clubmembers/{idclub}", response_model=List[AnonMember])
async def api_get_anonclubmembers(idclub: int, active: bool = True):
    """
    get all members of a club, returns a list of AnonMember (only name, club and rating)
    """
    try:
        return await anon_getclubmembers(idclub, active)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call anon_getclubmembers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/clubmembers/{idclub}", response_model=List[Member])
async def api_mgmt_clubmembers(
    idclub: int,
    active: bool = True,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    """
    get all members of a club, returns a list of AnonMember (only name, club and rating)
    """
    try:
        validate_token(auth)
        return await mgmt_getclubmembers(idclub, active)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call anon_getclubmembers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/member/{idnumber}", response_model=AnonMember)
async def api_anon_getmember(idnumber: int):
    """
    get a member by his idnumber (only name, club and rating)
    """
    try:
        return await anon_getmember(idnumber)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call anon_getmember")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/fidemember/{idnumber}", response_model=AnonMember)
async def api_anon_getfidemember(idnumber: int):
    """
    get a member by his idnumber (only name, club and rating)
    """
    try:
        return await anon_getfidemember(idnumber)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call anon_getmember")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/clb/member/{idnumber}", response_model=Member)
async def api_clb_get_member(
    idnumber: int, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    """
    get full details a member by his idnumber (as in the signaletique)
    """
    try:
        idnumber = validate_membertoken(auth)
        return await mgmt_getmember(idnumber)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_activemember")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/fideid2belid/{idfide}", response_model=int)
async def api_anon_belid_from_fideid(idfide: int):
    """
    return the id_bel for an id_fide, or 0 if not existing
    """
    try:
        return await anon_belid_from_fideid(idfide)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call anon_getmember")
        raise HTTPException(status_code=500, detail="Internal Server Error")
