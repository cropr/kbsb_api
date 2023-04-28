# copyright Chessdevil Consulting BVBA 2018 - 2020
# copyright Ruben Decrop 2020 - 2022

# this file contains API point that map directly to the old mysql database

import logging

from fastapi import HTTPException
from reddevil.core import RdException
from kbsb.main import app
from typing import Dict
from kbsb.oldkbsb import (
    OldLoginValidator,
    OldMemberList,
    old_login,
    get_clubmembers,
    get_member,
    ActiveMember,
    ActiveMemberList,
)
from .md_old import OldMemberList

logger = logging.getLogger(__name__)


@app.post("/api/v1/old/login")
def api_old_login(ol: OldLoginValidator) -> str:
    try:
        return old_login(ol)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call oldlogin")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/old/clubmembers/{idclub}", response_model=ActiveMemberList)
def api_get_clubmembers(idclub: int):
    try:
        return get_clubmembers(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_clubmembers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/old/activemember/{idnumber}", response_model=ActiveMember)
def api_get_activemember(idnumber: int):
    try:
        return get_member(idnumber)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_activemember")
        raise HTTPException(status_code=500, detail="Internal Server Error")
