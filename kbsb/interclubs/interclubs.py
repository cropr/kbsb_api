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
    get_mongodb,
)
from reddevil.mail import sendEmail, MailParams

from kbsb.interclubs.md_interclubs import (
    ICPlayer,
    ICVenue,
    ICClub,
    ICClubIn,
    ICClubOut,
    ICEnrollment,
    ICEnrollmentIn,
    ICPlayerUpdate,
    ICPlayerIn,
    ICPlayerValidationError,
    ICSeries,
    ICTeam,
    ICVenues,
    ICVenuesIn,
    DbICClub,
    DbICSeries,
    DbICEnrollment,
    DbICVenue,
    playersPerDivision,
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
    # TODO solve email
    # receiver = (
    #     [club.email_main, settings.INTERCLUB_CC_EMAIL]
    #     if club.email_main
    #     else [settings.INTERCLUB_CC_EMAIL]
    # )
    # if club.email_interclub:
    #     receiver.append(club.email_interclub)
    # mp = MailParams(
    #     locale=locale,
    #     receiver=",".join(receiver),
    #     sender="noreply@frbe-kbsb-ksb.be",
    #     bcc=settings.EMAIL.get("bcc", ""),
    #     subject="Interclub 2022-23",
    #     template="interclub/venues_{locale}.md",
    # )
    # nivdict = niv.dict()
    # nivdict["locale"] = locale
    # nivdict["name"] = club.name_long
    # sendEmail(mp, nivdict, "interclub venues")
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


# Interclub Clubs, Playerlist and Teams


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


async def anon_getICclub(idclub: int, options: Dict[str, Any] = {}) -> ICClub | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    options["_model"] = ICClub
    options["idclub"] = idclub
    club = await DbICClub.find_single(options)
    club.players = [p for p in club.players if p.nature in ["assigned", "requestedin"]]
    return club


async def anon_getICclubs() -> List[ICClubOut] | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    options = {
        "_model": ICClubOut,
        "enrolled": True,
        "_fieldlist": {i: 1 for i in ICClubOut.model_fields.keys()},
    }
    clubs = await DbICClub.find_multiple(options)
    return clubs


async def clb_getICclub(idclub: int, options: Dict[str, Any] = {}) -> ICClub | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    options["_model"] = ICClub
    options["idclub"] = idclub
    club = await DbICClub.find_single(options)
    return club


async def clb_updateICplayers(idclub: int, pi: ICPlayerIn) -> None:
    """
    update the the player list of a ckub
    """
    icc = await clb_getICclub(idclub)
    players = pi.players
    transfersout = []
    transferdeletes = []
    inserts = []
    oldplsix = {p.idnumber: p for p in icc.players}
    newplsix = {p.idnumber: p for p in players}
    for p in newplsix.values():
        idn = p.idnumber
        if idn not in oldplsix:
            # inserts
            inserts.append(p)
            if p.idclubvisit:
                if p.idcluborig == idclub:
                    transfersout.append(p)
        else:
            # check for modifications in transfer
            oldpl = oldplsix[idn]
            if oldpl.nature != p.nature:
                if p.nature in ["assigned", "unassigned", "locked"]:
                    # the trasfer is removed
                    transferdeletes.append(newpl)
                if p.nature in ["confirmedout"]:
                    transfersout.append(p)
    dictplayers = [p.model_dump() for p in players]
    await DbICClub.update({"idclub": idclub}, {"players": dictplayers})
    logger.info(f"trout {transfersout} trdel {transferdeletes}")
    for t in transfersout:
        receivingclub = await clb_getICclub(t.idclubvisit)
        rcplayers = receivingclub.players
        trplayers = [x for x in rcplayers if x.idnumber == t.idnumber]
        if not trplayers:
            rcplayers.append(
                ICPlayer(
                    assignedrating=t.assignedrating,
                    fiderating=t.fiderating,
                    first_name=t.first_name,
                    idnumber=t.idnumber,
                    idcluborig=t.idcluborig,
                    idclubvisit=t.idclubvisit,
                    last_name=t.last_name,
                    natrating=t.natrating,
                    nature="requestedin",
                    titular=None,
                )
            )
            dictplayers = [p.model_dump() for p in rcplayers]
            await DbICClub.update({"idclub": t.idclubvisit}, {"players": dictplayers})
    for t in transferdeletes:
        # we need to remove the transfer from the receiving club
        receivingclub = await clb_getICclub(t.idclubvisit)
        rcplayers = receivingclub.players
        trplayers = [x for x in rcplayers if x.idnumber != t.idnumber]
        dictplayers = [p.model_dump() for p in trplayers]
        await DbICClub.update({"idclub": t.idclubvisit}, {"players": dictplayers})


async def clb_validateICPlayers(
    idclub: int, pi: ICPlayerIn
) -> List[ICPlayerValidationError]:
    """
    creates a list of validation errors
    """
    errors = []
    players = [p for p in pi.players if p.nature in ["assigned", "requestedin"]]
    # check for valid elo
    elos = set()
    for p in players:
        if p.natrating is None:
            p.natrating = 0
        if p.fiderating is None:
            p.fiderating = 0
        if 1150 > p.natrating > 0:
            p.natrating = 1150
        maxrating = max(p.fiderating or 0, p.natrating) + 100
        minrating = min(p.fiderating or 3000, p.natrating) - 100
        if p.idnumber == 24338:
            logger.info(f"mx mn {maxrating} {minrating} {max(1000, minrating)} ")
        if p.assignedrating < max(1000, minrating):
            errors.append(
                ICPlayerValidationError(
                    errortype="ELO",
                    idclub=idclub,
                    message="Elo too low",
                    detail=p.idnumber,
                )
            )
        if not p.natrating and not p.fiderating:
            if p.assignedrating > 1600:
                errors.append(
                    ICPlayerValidationError(
                        errortype="ELO",
                        idclub=idclub,
                        message="Elo too high",
                        detail=p.idnumber,
                    )
                )
        elif p.assignedrating > maxrating:
            errors.append(
                ICPlayerValidationError(
                    errortype="ELO",
                    idclub=idclub,
                    message="Elo too high",
                    detail=p.idnumber,
                )
            )
        if p.assignedrating in elos:
            errors.append(
                ICPlayerValidationError(
                    errortype="ELO",
                    idclub=idclub,
                    message="Double ELO",
                    detail=p.idnumber,
                )
            )
        else:
            elos.add(p.assignedrating)
    countedTitulars = {}
    teams = await anon_getICteams(idclub)
    totaltitulars = 0
    for t in teams:
        countedTitulars[t.name] = {
            "counter": 0,
            "teamcount": playersPerDivision[t.division],
            "name": t.name,
        }
        totaltitulars += playersPerDivision[t.division]
    sortedplayers = sorted(players, reverse=True, key=lambda x: x.assignedrating)
    for ix, p in enumerate(sortedplayers):
        if ix >= totaltitulars:
            break
        if not p.titular:
            errors.append(
                ICPlayerValidationError(
                    errortype="TitularOrder",
                    idclub=idclub,
                    message="Titulars must be highest rated players",
                    detail=None,
                )
            )
            break
    for p in players:
        if p.titular:
            countedTitulars[p.titular]["counter"] += 1
    for ct in countedTitulars.values():
        if ct["counter"] < ct["teamcount"]:
            errors.append(
                ICPlayerValidationError(
                    errortype="TitularCount",
                    idclub=idclub,
                    message="Not enough titulars",
                    detail=ct["name"],
                )
            )
        if ct["counter"] > ct["teamcount"]:
            errors.append(
                ICPlayerValidationError(
                    errortype="TitularCount",
                    idclub=idclub,
                    message="Too many titulars",
                    detail=ct["name"],
                )
            )
    return errors


# Interclub Series, results and standing


async def anon_getICseries(idclub: int, round: int) -> List[ICSeries] | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    db = await get_mongodb()
    coll = db[DbICSeries.COLLECTION]
    proj = {i: 1 for i in ICSeries.model_fields.keys()}
    if round:
        proj["rounds"] = {"$elemMatch": {"round": round}}
    logger.info(f"proj {proj}")
    filter = {}
    if idclub:
        filter["teams.idclub"] = idclub
    logger.info(f"filter {filter}")
    series = []
    async for doc in coll.find(filter, proj):
        series.append(encode_model(doc, ICSeries))
    return series
