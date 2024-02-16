# copyright Ruben Decrop 2012 - 2024

import logging

logger = logging.getLogger(__name__)


from typing import cast, List, Dict, Any
from fastapi.responses import Response


from reddevil.core import (
    RdBadRequest,
    RdNotFound,
    get_settings,
    get_mongodb,
    get_mongodbs,
)
from reddevil.mail import sendEmail, MailParams

from kbsb.interclubs import (
    ICEnrollmentDB,
    ICEnrollmentIn,
    DbICEnrollment,
    ICROUNDS,
    PLAYERSPERDIVISION,
)
from kbsb.club import get_club_idclub, club_locale


# CRUD


async def create_interclubenrollment(enr: ICEnrollmentDB) -> str:
    """
    create a new InterclubEnrollment returning its id
    """
    enrdict = enr.model_dump()
    enrdict.pop("id", None)
    return await DbICEnrollment.add(enrdict)


async def get_interclubenrollment(id: str, options: dict = {}) -> ICEnrollmentDB:
    """
    get the interclub enrollment
    """
    filter = options.copy()
    filter["_model"] = filter.pop("_model", ICEnrollmentDB)
    filter["id"] = id
    return cast(ICEnrollmentDB, await DbICEnrollment.find_single(filter))


async def get_interclubenrollments(options: dict = {}) -> List[ICEnrollmentDB]:
    """
    get the interclub enrollment
    """
    filter = options.copy()
    filter["_model"] = filter.pop("_model", ICEnrollmentDB)
    return [cast(ICEnrollmentDB, x) for x in await DbICEnrollment.find_multiple(filter)]


async def update_interclubenrollment(
    id: str, iu: ICEnrollmentDB, options: dict = {}
) -> ICEnrollmentDB:
    """
    update a interclub enrollment
    """
    options1 = options.copy
    options1["_model"] = options1.pop("_model", ICEnrollmentDB)
    iudict = iu.model_dump(exclude_unset=True)
    iudict.pop("id", None)
    return cast(ICEnrollmentDB, await DbICEnrollment.update(id, iudict, options1))


# business methods


async def find_interclubenrollment(idclub: str) -> ICEnrollmentDB | None:
    """
    find an enrollment by idclub
    """
    logger.debug(f"find_interclubenrollment {idclub}")
    enrs = await get_interclubenrollments({"idclub": idclub})
    return enrs[0] if enrs else None


async def set_interclubenrollment(idclub: str, ie: ICEnrollmentIn) -> ICEnrollmentDB:
    """
    set enrollment (and overwrite it if it already exists)
    """
    club = await get_club_idclub(idclub)
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    settings = get_settings()
    enr = await find_interclubenrollment(idclub)
    if enr:
        nenr = await update_interclubenrollment(
            enr.id,
            ICEnrollmentDB(
                name=ie.name,
                teams1=ie.teams1,
                teams2=ie.teams2,
                teams3=ie.teams3,
                teams4=ie.teams4,
                teams5=ie.teams5,
                wishes=ie.wishes,
            ),
        )
    else:
        id = await create_interclubenrollment(
            ICEnrollmentDB(
                idclub=idclub,
                locale=locale,
                name=ie.name,
                teams1=ie.teams1,
                teams2=ie.teams2,
                teams3=ie.teams3,
                teams4=ie.teams4,
                teams5=ie.teams5,
                wishes=ie.wishes,
            )
        )
        nenr = await get_interclubenrollment(id)
    receiver = (
        [club.email_main, settings.INTERCLUBS_CC_EMAIL]
        if club.email_main
        else [settings.INTERCLUBS_CC_EMAIL]
    )
    if club.email_interclub:
        receiver.append(club.email_interclub)
    logger.debug(f"EMAIL settings {settings.EMAIL}")
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL.get("bcc", ""),
        subject="Interclub 2022-23",
        template="interclub/enrollment_{locale}.md",
    )
    sendEmail(mp, nenr.model_dump(), "interclub enrollment")
    return nenr


async def csv_ICenrollments() -> str:
    """
    get all enrollments in csv format
    """
    wishes_keys = [
        "wishes.grouping",
        "wishes.split",
        "wishes.regional",
        "wishes.remarks",
    ]
    fieldnames = [
        "idclub",
        "locale",
        "name_long",
        "name_short",
        "teams1",
        "teams2",
        "teams3",
        "teams4",
        "teams5",
        "idinvoice",
        "idpaymentrequest",
    ]
    csvstr = io.StringIO()
    csvf = csv.DictWriter(csvstr, fieldnames + wishes_keys)
    csvf.writeheader()
    for enr in await DbICEnrollment.find_multiple(
        {"_fieldlist": fieldnames + ["wishes"]}
    ):
        enrdict = enr.model_dump()
        id = enrdict.pop("id", None)
        wishes = enr.pop("wishes", {})
        enrdict["wishes.grouping"] = wishes.get("grouping", "")
        enrdict["wishes.split"] = wishes.get("split", "")
        enrdict["wishes.regional"] = wishes.get("regional", "")
        enrdict["wishes.remarks"] = wishes.get("remarks", "")
        csvf.writerow(enrdict)
    return csvstr.getvalue()
