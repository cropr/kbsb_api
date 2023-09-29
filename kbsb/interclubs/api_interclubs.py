import logging

logger = logging.getLogger(__name__)

from fastapi import HTTPException, Depends, APIRouter

from fastapi.security import HTTPAuthorizationCredentials
from reddevil.core import (
    RdException,
    bearer_schema,
    validate_token,
    jwt_getunverifiedpayload,
)
from typing import List, Any
from io import BytesIO

from kbsb.member import validate_membertoken
from .md_interclubs import (
    ICEnrollment,
    ICEnrollmentIn,
    ICVenuesIn,
    ICVenues,
    ICClub,
    ICClubIn,
    ICClubOut,
    ICGameDetails,
    ICPlanningIn,
    ICPlayerIn,
    ICPlayerValidationError,
    ICResultIn,
    ICSeries,
    ICTeam,
)
from .interclubs import (
    anon_getICteams,
    anon_getICclub,
    anon_getICclubs,
    anon_getICseries,
    anon_getICencounterdetails,
    clb_getICclub,
    clb_getICseries,
    clb_saveICplanning,
    clb_saveICresults,
    clb_updateICplayers,
    clb_validateICPlayers,
    csv_ICenrollments,
    csv_ICvenues,
    find_interclubenrollment,
    getICvenues,
    mgmt_getXlsAllplayerlist,
    mgmt_saveICresults,
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
    logger.debug(f"api_find_interclubenrollment {idclub}")
    try:
        return await find_interclubenrollment(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call find_interclubenrollment")
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
        logger.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/exportenrollments", response_model=str)
async def api_csv_interclubenrollments(
    format: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        if format == "csv":
            return await csv_ICenrollments()
        elif format == "excel":
            return ""
        else:
            raise RdException(status_code=400, description="Unsupported export format")
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call csv_interclubenrollments")
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
        logger.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# venues


@router.get("/anon/venue/{idclub}", response_model=ICVenues | None)
async def api_find_interclubvenues(idclub: int):
    try:
        logger.info(f"get venues {idclub}")
        a = await getICvenues(idclub)
        logger.info(f"got venues {a}")
        return a
    except RdException as e:
        logger.info(f"get venues failed {e}")
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call find_interclubvenues")
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
        logger.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/exportvenues", response_model=str)
async def api_csv_interclubvenues(
    format: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        if format == "csv":
            return await csv_ICvenues()
        elif format == "excel":
            return
        else:
            raise RdException(status_code=400, description="Unsupported export format")
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call csv_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/clb/venue/{idclub}", response_model=ICVenues)
async def api_clb_set_icvenues(
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
        logger.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# icteams and icclub


@router.get("/anon/icteams/{idclub}", response_model=List[ICTeam])
async def api_anon_getICteams(idclub: int):
    try:
        return await anon_getICteams(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call anon_getICteams")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/icclub/{idclub}", response_model=ICClub)
async def api_anon_getICclub(idclub: int):
    try:
        return await anon_getICclub(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/icclub", response_model=List[ICClubOut])
async def api_anon_getICclubs():
    try:
        return await anon_getICclubs()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_getICclub")
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
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/icclub/{idclub}", response_model=ICClub)
async def api_mgmt_getICclub(
    idclub: int,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await clb_getICclub(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call mgmt_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post(
    "/clb/icclub/{idclub}/validate", response_model=List[ICPlayerValidationError]
)
async def api_clb_validateICplayers(
    idclub: int,
    players: ICPlayerIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_membertoken(auth)
        return await clb_validateICPlayers(idclub, players)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_validateICPlayers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post(
    "/mgmt/icclub/{idclub}/validate", response_model=List[ICPlayerValidationError]
)
async def api_mgmt_validateICplayers(
    idclub: int,
    players: ICPlayerIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_token(auth)
        return await clb_validateICPlayers(idclub, players)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_validateICPlayers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clb/icclub/{idclub}", status_code=204)
async def api_clb_updateICPlayers(
    idclub: int,
    players: ICPlayerIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_membertoken(auth)
        await clb_updateICplayers(idclub, players)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_updateICplayers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/mgmt/icclub/{idclub}", status_code=204)
async def api_mgmt_updateICPlayers(
    idclub: int,
    players: ICPlayerIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_token(auth)
        await clb_updateICplayers(idclub, players)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_updateICplayers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/xls/allplayerlist", response_model=str)
async def api_mgmt_getXlsAllplayerlist(token: str):
    try:
        payload = jwt_getunverifiedpayload(token)
        logger.info(f"payload {payload}")
        assert payload["sub"].split("@")[1] == "frbe-kbsb-ksb.be"
        return await mgmt_getXlsAllplayerlist()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call mgmt_getXlsAllplayerlist")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# pairings end results


@router.get("/anon/icseries", response_model=List[ICSeries])
async def api_anon_getICseries(idclub: int | None = 0, round: int | None = 0):
    try:
        return await anon_getICseries(idclub, round)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call anon_getICclubs")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/clb/icseries", response_model=List[ICSeries])
async def api_clb_getICseries(
    idclub: int | None = 0,
    round: int | None = 0,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_membertoken(auth)
        return await clb_getICseries(idclub, round)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/icseries", response_model=List[ICSeries])
async def api_mgmt_getICseries(
    idclub: int | None = 0,
    round: int | None = 0,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await clb_getICseries(idclub, round)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clb/icplanning", status_code=201)
async def api_clb_saveICplanning(
    icpi: ICPlanningIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        validate_membertoken(auth)
        await clb_saveICplanning(icpi.plannings)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/mgmt/icresults", status_code=201)
async def api_mgmt_saveICresults(
    icri: ICResultIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        await mgmt_saveICresults(icri.results)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clb/icresults", status_code=201)
async def api_mgmt_saveICresults(
    icri: ICResultIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        logger.info("hi")
        validate_membertoken(auth)
        await clb_saveICresults(icri.results)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/icresultdetails", response_model=List[ICGameDetails])
async def api_anon_getICencounterdetails(
    division: int, index: str, round: int, icclub_home: int, icclub_visit: int
):
    try:
        return await anon_getICencounterdetails(
            division=division,
            index=index or "",
            round=round,
            icclub_home=icclub_home,
            icclub_visit=icclub_visit,
        )
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call anon_getICdetails")
        raise HTTPException(status_code=500, detail="Internal Server Error")
