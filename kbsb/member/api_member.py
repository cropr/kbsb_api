# copyright Chessdevil Consulting BVBA 2018 - 2020
# copyright Ruben Decrop 2020 - 2022

# this file contains API point that map directly to the old mysql database

import logging

from fastapi import HTTPException, APIRouter
from reddevil.core import RdException
from typing import List
from kbsb.member import (
    LoginValidator,
    login,
    get_clubmembers,
    get_member,
    ActiveMember,
    ActiveMemberList,
)
from .md_member import MemberList

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/members")


@router.post("/login")
def api_login(ol: LoginValidator) -> str:
    """
    login by using the idnumber
    """
    try:
        return login(ol)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call oldlogin")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/clubmembers/{idclub}", response_model=List[ActiveMember])
def api_get_clubmembers(idclub: int):
    """
    get all members of a club
    """
    try:
        return get_clubmembers(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_clubmembers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon//activemember/{idnumber}", response_model=ActiveMember)
def api_get_activemember(idnumber: int):
    """
    get a member by his idnumber
    """
    try:
        return get_member(idnumber)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_activemember")
        raise HTTPException(status_code=500, detail="Internal Server Error")
