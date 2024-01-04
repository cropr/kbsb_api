# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging

from fastapi import HTTPException, Depends, BackgroundTasks, APIRouter
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from typing import List
from reddevil.core import (
    RdException,
    bearer_schema,
    validate_token,
    jwt_getunverifiedpayload,
)

from kbsb.club import (
    create_club,
    delete_club,
    get_club,
    get_anon_clubs,
    get_csv_clubs,
    get_club_idclub,
    mgmt_mailinglist,
    update_club,
    set_club,
    verify_club_access,
    Club,
    ClubItem,
    ClubIn,
    ClubRoleNature,
    ClubUpdate,
)
from kbsb.member import validate_membertoken

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/clubs")

# mgmt calls


@router.post("/mgmt/club", response_model=str)
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


@router.get("/mgmt/club/{idclub}", response_model=Club)
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


@router.delete("/mgmt/club/{idclub}")
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


@router.put("/mgmt/club/{idclub}", response_model=Club)
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


@router.get("/clb/club/{idclub}", response_model=Club)
async def api_clb_get_club(
    idclub: int, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        idnumber = validate_membertoken(auth)
        await verify_club_access(idclub, idnumber, ClubRoleNature.ClubAdmin)
        return await get_club({"idclub": idclub})
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_c_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clb/club/{idclub}", response_model=Club)
async def api_clb_update_club(
    idclub: int,
    p: ClubUpdate,
    bt: BackgroundTasks,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        idnumber = validate_membertoken(auth)
        await verify_club_access(idclub, idnumber, ClubRoleNature.ClubAdmin)
        return await set_club(idclub, p, user=str(idnumber), bt=bt)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call update_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# anon calls


@router.get("/anon/club", response_model=List[ClubItem])
async def api_anon_get_clubs():
    try:
        return await get_anon_clubs()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_clubs")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/csvclubs", response_class=StreamingResponse)
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


@router.get("/anon/club/{idclub}", response_model=Club)
async def api_anon_get_club(
    idclub: int, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        return await get_club({"idclub": idclub})
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_c_club")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# other


@router.get("/clb/club/{idclub}/access/{role}")
async def api_verify_club_access(
    idclub: int,
    role: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    """
    verifies if a user identified by token has access to a club role
    """
    try:
        idnumber = validate_membertoken(auth)
        await verify_club_access(idclub=idclub, idnumber=idnumber, role=role)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call verify_club_access")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/mailinglist", response_model=str)
async def api_mgmt_getXlsAllplayerlist(token: str):
    try:
        payload = jwt_getunverifiedpayload(token)
        assert payload["sub"].split("@")[1] == "frbe-kbsb-ksb.be"
        return await mgmt_mailinglist()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call mgmt_getXlsAllplayerlist")
        raise HTTPException(status_code=500, detail="Internal Server Error")
