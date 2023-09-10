# copyright Ruben Decrop 2012 - 2022

import logging
from typing import cast, List, Dict, Any
from datetime import datetime
import io, csv

from reddevil.core import (
    RdBadRequest,
    RdNotFound,
    encode_model,
    get_settings,
)
from reddevil.mail import sendEmail, MailParams

from kbsb.interclubs.md_interclubs import (
    ICPlayer,
    ICTransfer,
    ICVenue,
    ICClub,
    ICClubIn,
    ICEnrollment,
    ICEnrollmentIn,
    ICTeam,
    ICSeries,
    ICVenues,
    ICVenuesIn,
    DbICClub,
    DbICSeries,
    DbICEnrollment,
    DbICVenue,
)
from kbsb.club import get_club_idclub, club_locale, DbClub
from kbsb.member import anon_getmember

logger = logging.getLogger(__name__)
settings = get_settings()


# Interclub Enrollment


async def create_interclubenrollment(enr: ICEnrollment) -> str:
    """
    create a new InterclubEnrollment returning its id
    """
    enrdict = enr.dict()
    enrdict.pop("id", None)
    return await DbICEnrollment.add(enrdict)


async def get_interclubenrollment(id: str, options: dict = {}) -> ICEnrollment:
    """
    get the interclub enrollment
    """
    _class = options.pop("_class", ICEnrollment)
    filter = dict(id=id, **options)
    fdict = await DbICEnrollment.find_single(filter)
    return encode_model(fdict, _class)


async def get_interclubenrollments(options: dict = {}) -> List[ICEnrollment]:
    """
    get the interclub enrollment
    """
    logger.debug(f"get_interclubenrollments {options}")
    _class = options.pop("_class", ICEnrollment)
    options["_model"] = ICEnrollment
    docs = await DbICEnrollment.find_multiple(options)
    return docs


async def update_interclubenrollment(
    id: str, iu: ICEnrollment, options: dict = {}
) -> ICEnrollment:
    """
    update a interclub enrollment
    """
    validator = options.pop("_class", ICEnrollment)
    iu.id = None  # don't override the id
    cdict = await DbICEnrollment.update(id, iu.dict(exclude_unset=True), options)
    return cast(ICEnrollment, encode_model(cdict, validator))


# InterclubVenues


async def create_interclubvenues(iv: ICVenues) -> str:
    """
    create a new InterclubVenues returning its id
    """
    ivdict = iv.dict()
    ivdict.pop("id", None)
    return await DbICVenue.add(ivdict)


async def get_interclubvenues(id: str, options: dict = {}) -> ICVenues:
    """
    get the interclubvenues
    """
    _class = options.pop("_class", ICVenues)
    filter = dict(id=id, **options)
    fdict = await DbICVenue.find_single(filter)
    return encode_model(fdict, _class)


async def get_interclubvenues_clubs(options: dict = {}) -> List[ICVenues]:
    """
    get the interclubvenues of all clubs
    """
    _class = options.pop("_class", ICVenues)
    options["_model"] = ICVenues
    docs = await DbICVenue.find_multiple(options)
    clubvenues = [encode_model(d, _class) for d in docs]
    return clubvenues


async def update_interclubvenues(id: str, iu: ICVenues, options: dict = {}) -> ICVenues:
    """
    update a interclub venue
    """
    validator = options.pop("_class", ICVenues)
    iu.id = None  # don't override the id
    docdict = await DbICVenue.update(id, iu.dict(exclude_unset=True), options)
    return cast(ICVenues, encode_model(docdict, validator))


# enrollments


async def find_interclubenrollment(idclub: str) -> ICEnrollment | None:
    """
    find an enrollment by idclub
    """
    logger.debug(f"find_interclubenrollment {idclub}")
    enrs = (await get_interclubenrollments({"idclub": idclub})).enrollments
    return enrs[0] if enrs else None


async def set_interclubenrollment(idclub: str, ie: ICEnrollmentIn) -> ICEnrollment:
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
            ICEnrollment(
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
            ICEnrollment(
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
    sendEmail(mp, nenr.dict(), "interclub enrollment")
    return nenr


async def csv_interclubenrollments() -> str:
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
        id = enr.pop("id", None)
        wishes = enr.pop("wishes", {})
        enr["wishes.grouping"] = wishes.get("grouping", "")
        enr["wishes.split"] = wishes.get("split", "")
        enr["wishes.regional"] = wishes.get("regional", "")
        enr["wishes.remarks"] = wishes.get("remarks", "")
        csvf.writerow(enr)
    return csvstr.getvalue()


async def getICvenues(idclub: int) -> ICVenues:
    try:
        venues = await DbICVenue.find_single({"_model": ICVenues, "idclub": idclub})
    except RdNotFound as e:
        return ICVenues(id="", idclub=idclub, venues=[])
    return venues


async def set_interclubvenues(idclub: str, ivi: ICVenuesIn) -> ICVenues:
    club = await get_club_idclub(idclub)
    logger.debug(f"set_interclubvenues: {idclub} {ivi}")
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    logger.info(f"locale {locale}")
    settings = get_settings()
    ivn = await getICvenues(idclub)
    iv = ICVenues(
        idclub=idclub,
        venues=ivi.venues,
    )
    if ivn:
        logger.info(f"update interclubvenues {ivn.id} {iv}")
        niv = await update_interclubvenues(ivn.id, iv)
    else:
        logger.info(f"insert interclubvenues {iv}")
        id = await create_interclubvenues(iv)
        niv = await get_interclubvenues(id)
    receiver = (
        [club.email_main, settings.INTERCLUB_CC_EMAIL]
        if club.email_main
        else [settings.INTERCLUB_CC_EMAIL]
    )
    if club.email_interclub:
        receiver.append(club.email_interclub)
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL.get("bcc", ""),
        subject="Interclub 2022-23",
        template="interclub/venues_{locale}.md",
    )
    nivdict = niv.dict()
    nivdict["locale"] = locale
    nivdict["name"] = club.name_long
    sendEmail(mp, nivdict, "interclub venues")
    return niv


async def csv_interclubvenues() -> str:
    """
    get all venues in csv format
    """
    fieldnames = [
        "idclub",
        "name_long",
        "name_short",
        "address",
        "email",
        "phone",
        "capacity",
        "notavailable",
    ]
    csvstr = io.StringIO()
    csvf = csv.DictWriter(csvstr, fieldnames)
    csvf.writeheader()
    for vns in await DbICVenue.find_multiple():
        idclub = vns.get("idclub")
        name_long = vns.get("name_long")
        name_short = vns.get("name_short")
        venues = vns.get("venues")
        for v in venues:
            csvf.writerow(
                {
                    "idclub": idclub,
                    "name_long": name_long,
                    "name_short": name_short,
                    "address": v.get("address"),
                    "email": v.get("email"),
                    "phone": v.get("phone"),
                    "capacity": v.get("capacity"),
                    "notavailable": ",".join(v.get("notavailable", [])),
                }
            )
    return csvstr.getvalue()


# Interclub Series and Teams


async def anon_getICteams(idclub: int, options: dict = {}) -> List[ICTeam]:
    """
    get all the interclub temas for a club
    """
    dictseries = await DbICSeries.find_multiple({"teams.idclub": idclub})
    if not dictseries:
        return []
    series = [encode_model(s, ICSeries) for s in dictseries]
    teams = []
    for s in series:
        for t in s.teams:
            if t.idclub == idclub:
                teams.append(t)
    return teams


async def clb_getICclub(idclub: int, options: Dict[str, Any] = {}) -> ICClub | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    options["_model"] = ICClub
    options["idclub"] = idclub
    club = await DbICClub.find_single(options)
    return club


# async def update_clublist(idclub: int, playerlist: List[int]) -> None:
#     """
#     update the clublist with a list of members, belonging to that club
#     """
#     icc = await find_interclubclub(idclub)
#     playerset = {p.idnumber for p in icc.players}
#     for p in playerlist:
#         am = anon_getmember(p)
#         if not am:
#             logger.info("cannot add player {m} to clublist: player is inactive")
#             continue
#         if am.idclub != idclub:
#             logger.info(
#                 "cannot add player {m} to clublist player is not member of {idclub}"
#             )
#             continue
#         if p in playerset:
#             continue
#         playerset.add(p)
#         icc.players.append(
#             ICPlayer(
#                 assignedrating=max(am.fiderating, am.natrating),
#                 fiderating=am.fiderating,
#                 first_name=am.first_name,
#                 idnumber=p,
#                 idclub=icc.idclub,
#                 natrating=am.natrating,
#                 last_name=am.last_name,
#                 transfer=False,
#             )
#         )
#     # DbInterclubClub.p_update(icc.id, InterclubClubOptional(players=icc.players))


# async def update_icclub(idclub: int, icc: ICClubIn) -> ICClub:
#     """
#     updates the interclubclub
#     """
#     club = await get_club_idclub(idclub)
#     if not club:
#         raise RdNotFound(description="ClubNotFound")
#     locale = club_locale(club)
#     ic = await find_interclubclub(idclub)
#     settings = get_settings()
#     icupdated = await DbInterclubClub.p_update(ic.id, icc)
#     receiver = (
#         [club.email_main, settings.INTERCLUB_CC_EMAIL]
#         if club.email_main
#         else [settings.INTERCLUB_CC_EMAIL]
#     )
#     if club.email_interclub:
#         receiver.append(club.email_interclub)
#     mp = MailParams(
#         locale=locale,
#         receiver=",".join(receiver),
#         sender="noreply@frbe-kbsb-ksb.be",
#         bcc=settings.EMAIL.get("bcc", ""),
#         subject="Interclub 2022-23",
#         template="interclub/club_{locale}.md",
#     )
#     icdict = icupdated.dict()
#     icdict["locale"] = locale
#     sendEmail(mp, icdict, "interclub playerlist")
#     return icupdated
