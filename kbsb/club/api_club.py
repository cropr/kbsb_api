# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging

from fastapi import HTTPException, Depends, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from reddevil.core import RdException, bearer_schema, validate_token

from kbsb.main import app
from kbsb.club import (
    create_club,
    delete_club,
    get_club,
    get_anon_clubs,
    get_csv_clubs,
    get_club_idclub,
    update_club,
    set_club,
    verify_club_access,
    Club,
    ClubIn,
    ClubList,
    ClubRoleNature,
    ClubUpdate,
)
from kbsb.oldkbsb.old import validate_oldtoken

logger = logging.getLogger(__name__)

# mgmt calls


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


@app.get("/api/v1/club/{idclub}", response_model=Club)
async def api_get_club(
    idclub: int, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await get_club_idclub(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/api/v1/club/{idclub}")
async def api_delete_club(
    idclub: int, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        await delete_club(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call delete_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/api/v1/club/{idclub}", response_model=Club)
async def api_update_club(
    idclub: int,
    p: ClubUpdate,
    bt: BackgroundTasks,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    logger.debug(f"api ClubUpdate {p}")
    try:
        user = await validate_token(auth)
        return await set_club(idclub, p, user=user, bt=bt)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call update_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# clb calls


@app.get("/api/v1/c/club/{idclub}", response_model=Club)
async def api_clb_get_club(
    idclub: int, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        idnumber = validate_oldtoken(auth)
        verify_club_access(id, idnumber, ClubRoleNature.ClubAdmin)
        return await get_club({"idclub": idclub})
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_c_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/api/v1/c/club/{idclub}", response_model=Club)
async def api_clb_update_club(
    idclub: int,
    p: ClubUpdate,
    bt: BackgroundTasks,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        idnumber = validate_oldtoken(auth)
        verify_club_access(idclub, idnumber, ClubRoleNature.ClubAdmin)
        return await set_club(idclub, p, user=str(idnumber), bt=bt)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call update_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# anon calls


@app.get("/api/v1/a/clubs", response_model=ClubList)
async def api_anon_get_clubs():
    try:
        return await get_anon_clubs()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_clubs")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/a/csv/clubs", response_class=StreamingResponse)
async def api_anon_csv_clubs():
    try:
        stream = await get_csv_clubs()
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=clubs.csv"
        return response
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_clubs")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# other


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
        await verify_club_access(idclub=idclub, idnumber=idnumber, role=role)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call verify_club_access")
        raise HTTPException(status_code=500, detail="Internal Server Error")
