# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from reddevil.core import RdException, bearer_schema, validate_token

from kbsb.main import app
from kbsb.club import (
    create_club,
    delete_club,
    get_club,
    get_clubs,
    update_club,
    set_club,
    find_club,
    verify_club_access,
    Club,
    ClubIn,
    ClubList,
    ClubRoleNature,
    ClubUpdate,
)
from kbsb.oldkbsb.old import validate_oldtoken

logger = logging.getLogger(__name__)


@app.get("/api/v1/clubs", response_model=ClubList)
async def api_get_clubs(
    reports: int = 0, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    logger.debug("api_get_clubs called")
    try:
        await validate_token(auth)
        return await get_clubs()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_clubs")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/c/clubs", response_model=ClubList)
async def api_clb_get_clubs(
    reports: int = 0, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    logger.debug("api_get_clubs called")
    try:
        validate_oldtoken(auth)
        return await get_clubs()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_clubs")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/a/clubs", response_model=ClubList)
async def api_anon_get_clubs(reports: int = 0):
    try:
        return await get_clubs()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_clubs")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/clubs", response_model=str)
async def api_create_club(
    p: ClubIn, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        validate_token(auth)
        return await create_club(p)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call create_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/club/{id}", response_model=Club)
async def api_get_club(
    id: str, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await get_club(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/c/club/{id}", response_model=Club)
async def api_clb_get_club(
    id: str, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        idnumber = validate_oldtoken(auth)
        verify_club_access(id, idnumber, ClubRoleNature.ClubAdmin)
        return await get_club(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_c_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/api/v1/club/{id}")
async def api_delete_club(
    id: str, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        await delete_club(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call delete_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/api/v1/club/{id}", response_model=Club)
async def api_update_club(
    id: str, p: ClubUpdate, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await set_club(id, p)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call update_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/api/v1/c/club/{id}", response_model=Club)
async def api_clb_update_club(
    id: str, p: ClubUpdate, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        idnumber = validate_oldtoken(auth)
        verify_club_access(id, idnumber, ClubRoleNature.ClubAdmin)
        return await set_club(id, p)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call update_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/c/clubs/{idclub}/access/{role}")
async def api_verify_club_access(
    idclub: int,
    role: ClubRoleNature,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    """
    verifies if a user identified by token has access to a club role
    """
    try:
        idnumber = validate_oldtoken(auth)
        await verify_club_access(id_or_idclub=idclub, idnumber=idnumber, role=role)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call verify_club_access")
        raise HTTPException(status_code=500, detail="Internal Server Error")
