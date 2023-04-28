import logging

log = logging.getLogger(__name__)

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import List, Optional
from reddevil.core import RdException, bearer_schema, validate_token

from kbsb.main import app
from kbsb.oldkbsb import validate_oldtoken
from . import (
    csv_interclubenrollments,
    csv_interclubvenues,
    find_interclubenrollment,
    find_interclubvenues_club,
    set_interclubenrollment,
    set_interclubvenues,
    setup_interclubclub,
    set_interclubclub,
    get_announcements,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubVenuesIn,
    InterclubVenues,
    InterclubClub,
    InterclubClubOptional,
    PageList,
)


@app.get(
    "/api/v1/a/interclub/enrollment/{idclub}",
    response_model=Optional[InterclubEnrollment],
)
async def api_find_interclubenrollment(idclub: int):
    """
    return an enrollment by idclub
    """
    log.debug(f"api_find_interclubenrollment {idclub}")
    try:
        return await find_interclubenrollment(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call find_interclubenrollment")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/interclub/enrollment/{idclub}", response_model=InterclubEnrollment)
async def api_mgmt_set_enrollment(
    idclub: int,
    ie: InterclubEnrollmentIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await set_interclubenrollment(idclub, ie)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/csv/interclubenrollment", response_model=str)
async def api_csv_interclubenrollments(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        return await csv_interclubenrollments()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call csv_interclubenrollments")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/c/interclub/enrollment/{idclub}", response_model=InterclubEnrollment)
async def api_set_enrollment(
    idclub: int,
    ie: InterclubEnrollmentIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_oldtoken(auth)
        # TODO check club autorization
        return await set_interclubenrollment(idclub, ie)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get(
    "/api/v1/a/interclub/venues/{idclub}", response_model=Optional[InterclubVenues]
)
async def api_find_interclubvenues(idclub: int):
    try:
        return await find_interclubvenues_club(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call find_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/interclub/venues/{idclub}", response_model=InterclubVenues)
async def api_mgmt_set_interclubvenues(
    idclub: int,
    ivi: InterclubVenuesIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        # TODO check club autorization
        return await set_interclubvenues(idclub, ivi)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/csv/interclubvenues", response_model=str)
async def api_csv_interclubvenues(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        return await csv_interclubvenues()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call csv_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/c/interclub/venues/{idclub}", response_model=InterclubVenues)
async def api_set_interclubvenues(
    idclub: int,
    ivi: InterclubVenuesIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_oldtoken(auth)
        return await set_interclubvenues(idclub, ivi)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/a/interclub/club/{idclub}", response_model=InterclubClub)
async def api_get_interclubclub(
    idclub: int,
):
    try:
        return await setup_interclubclub(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call get_interclubclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/api/v1/interclub/club/{idclub}", response_model=InterclubClub)
async def api_mgmt_set_interclubclub(
    idclub: int,
    icc: InterclubClubOptional,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await set_interclubclub(idclub, icc)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call mgmt_set_interclubclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/api/v1/c/interclub/club/{idclub}", response_model=InterclubClub)
async def api_clb_set_interclubclub(
    idclub: int,
    icc: InterclubClubOptional,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_oldtoken(auth)
        return await set_interclubclub(idclub, icc)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call clb_set_interclubclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/v1/a/interclub/announcements", response_model=PageList)
async def api_anon_get_announcements(
):
    try:
        return await get_announcements()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call anon_get_announcements")
        raise HTTPException(status_code=500, detail="Internal Server Error")
