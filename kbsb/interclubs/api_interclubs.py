import logging

log = logging.getLogger(__name__)

from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import HTTPAuthorizationCredentials
from reddevil.core import RdException, bearer_schema, validate_token
from typing import List

from kbsb.member import validate_membertoken
from .md_interclubs import (
    ICEnrollment,
    ICEnrollmentIn,
    ICVenuesIn,
    ICVenues,
    ICClub,
    ICClubIn,
    ICTeam,
)
from .interclubs import (
    anon_getICteams,
    clb_getICclub,
    csv_interclubenrollments,
    csv_interclubvenues,
    find_interclubenrollment,
    getICvenues,
    set_interclubenrollment,
    set_interclubvenues,
)

router = APIRouter(prefix="/api/v1/interclubs")


# emrollments


@router.get(
    "/anon/enrollment/{idclub}",
    response_model=ICEnrollment | None,
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


@router.post("/mgmt/enrollment/{idclub}", response_model=ICEnrollment)
async def api_mgmt_set_enrollment(
    idclub: int,
    ie: ICEnrollmentIn,
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


@router.get("/mgmt/command/exportenrollments", response_model=str)
async def api_csv_interclubenrollments(
    format: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        if format == "csv":
            return await csv_interclubenrollments()
        elif format == "excel":
            return ""
        else:
            raise RdException(status_code=400, description="Unsupported export format")
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call csv_interclubenrollments")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/clb/enrollment/{idclub}", response_model=ICEnrollment)
async def api_set_enrollment(
    idclub: int,
    ie: ICEnrollmentIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_membertoken(auth)
        # TODO check club autorization
        return await set_interclubenrollment(idclub, ie)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# venues


@router.get("/anon/venue/{idclub}", response_model=ICVenues | None)
async def api_find_interclubvenues(idclub: int):
    try:
        return await getICvenues(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call find_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mgmt/venue/{idclub}", response_model=ICVenues)
async def api_mgmt_set_interclubvenues(
    idclub: int,
    ivi: ICVenuesIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await set_interclubvenues(idclub, ivi)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/exportvenues", response_model=str)
async def api_csv_interclubvenues(
    format: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        if format == "csv":
            return await csv_interclubvenues()
        elif format == "excel":
            return
        else:
            raise RdException(status_code=400, description="Unsupported export format")
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call csv_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/clb/venue/{idclub}", response_model=ICVenues)
async def api_set_interclubvenues(
    idclub: int,
    ivi: ICVenuesIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_membertoken(auth)
        return await set_interclubvenues(idclub, ivi)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# icteams and icclub


@router.get("/anon/icteams/{idclub}", response_model=List[ICTeam])
async def api_anon_getICteams(idclub: int):
    try:
        return await anon_getICteams(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call anon_getICteams")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/clb/icclub/{idclub}", response_model=ICClub)
async def api_clb_getICclub(
    idclub: int,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_membertoken(auth)
        return await clb_getICclub(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")
