# copyright Chessdevil Consulting BVBA 2018 - 2020
# copyright Ruben Decrop 2020 - 2022

# this file contains API point that map directly to the old mysql database

import logging

from fastapi import HTTPException, APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from reddevil.core import RdException, bearer_schema, validate_token
from typing import List
from kbsb.member import (
    AnonMember,
    LoginValidator,
    Member,
    anon_getclubmembers,
    anon_getmember,
    login,
    mgmt_getmember,
    validate_membertoken,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/member")


@router.post("/login")
async def api_login(ol: LoginValidator) -> str:
    """
    login by using the idnumber, return a JWT token
    """
    try:
        return await login(ol)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call oldlogin")
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


@router.get("/anon/member/{idnumber}", response_model=AnonMember)
async def api_get_anonmember(idnumber: int):
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
