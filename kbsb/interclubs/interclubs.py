# copyright Ruben Decrop 2012 - 2022

import logging
from typing import cast, List, Dict, Any
from datetime import datetime, timezone, timedelta
import io, csv
import asyncio
import copy
import openpyxl
from tempfile import NamedTemporaryFile
from fastapi.responses import Response

from reddevil.core import (
    RdBadRequest,
    RdNotFound,
    encode_model,
    get_settings,
    get_mongodb,
    get_mongodbs,
)
from reddevil.mail import sendEmail, MailParams

from kbsb.interclubs.md_interclubs import (
    ICPlayer,
    ICVenue,
    ICClub,
    ICClubIn,
    ICClubOut,
    ICEncounter,
    ICEnrollment,
    ICEnrollmentIn,
    ICGame,
    ICGameDetails,
    ICPlanning,
    ICPlayerUpdate,
    ICPlayerIn,
    ICPlayerValidationError,
    ICResult,
    ICResultIn,
    ICSeries,
    ICStandings,
    ICTeam,
    ICTeamGame,
    ICTeamStanding,
    ICVenues,
    ICVenuesIn,
    DbICClub,
    DbICSeries,
    DbICEnrollment,
    DbICVenue,
    DbICStandings,
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


async def csv_ICvenues() -> str:
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


async def mgmt_getXlsAllplayerlist():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(
        ["club", "idnumber", "name", "cluborig", "rating", "F ELO", "B ELO", "Titular"]
    )
    clubs = await DbICClub.find_multiple({"_model": ICClub})
    for c in clubs:
        if not c.enrolled:
            continue
        sortedplayers = sorted(c.players, key=lambda x: x.assignedrating, reverse=True)
        for p in sortedplayers:
            if p.nature not in ["assigned", "requestedin"]:
                continue
            ws.append(
                [
                    c.idclub,
                    p.idnumber,
                    f"{p.last_name}, {p.first_name}",
                    p.idcluborig,
                    p.assignedrating,
                    p.fiderating,
                    p.natrating,
                    p.titular,
                ]
            )
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        return Response(
            content=tmp.read(),
            headers={"Content-Disposition": "attachment; filename=allplayerlist.xlsx"},
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


async def anon_getXlsplayerlist(idclub: int):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(
        ["club", "idnumber", "name", "cluborig", "rating", "F ELO", "B ELO", "Titular"]
    )
    club = await DbICClub.find_single({"_model": ICClub, "idclub": idclub})
    sortedplayers = sorted(club.players, key=lambda x: x.assignedrating, reverse=True)
    for p in sortedplayers:
        if p.nature not in ["assigned", "requestedin"]:
            continue
        ws.append(
            [
                idclub,
                p.idnumber,
                f"{p.last_name}, {p.first_name}",
                p.idcluborig,
                p.assignedrating,
                p.fiderating,
                p.natrating,
                p.titular,
            ]
        )
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        return Response(
            content=tmp.read(),
            headers={
                "Content-Disposition": f"attachment; filename=playerlist_{idclub}.xlsx"
            },
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# Interclub Series, results and standing


async def anon_getICseries(idclub: int, round: int) -> List[ICSeries] | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    db = get_mongodb()
    coll = db[DbICSeries.COLLECTION]
    proj = {i: 1 for i in ICSeries.model_fields.keys()}
    if round:
        proj["rounds"] = {"$elemMatch": {"round": round}}
    logger.info(f"proj {proj}")
    filter = {}
    if idclub:
        filter["teams.idclub"] = idclub
    series = []
    async for doc in coll.find(filter, proj):
        series.append(encode_model(doc, ICSeries))
    return series


async def clb_getICseries(idclub: int, round: int) -> List[ICSeries] | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    db = get_mongodb()
    coll = db[DbICSeries.COLLECTION]
    proj = {i: 1 for i in ICSeries.model_fields.keys()}
    if round:
        proj["rounds"] = {"$elemMatch": {"round": round}}
    logger.info(f"proj {proj}")
    filter = {}
    if idclub:
        filter["teams.idclub"] = idclub
    series = []
    cursor = coll.find(filter, proj)
    ### changed
    for doc in await cursor.to_list(length=50):
        logger.info(f'ICseries {doc.get("division")} {doc.get("index")}')
        series.append(encode_model(doc, ICSeries))
    # async for doc in coll.find(filter, proj):
    #     series.append(encode_model(doc, ICSeries))
    return series


async def clb_saveICplanning(plannings: List[ICPlanning]) -> None:
    """
    save a lists of pleanning per team
    """
    for plan in plannings:
        s = await DbICSeries.find_single(
            {"division": plan.division, "index": plan.index, "_model": ICSeries}
        )
        curround = None
        for r in s.rounds:
            if r.round == plan.round:
                curround = r
        if not curround:
            raise RdBadRequest(description="InvalidRound")
        for enc in curround.encounters:
            if plan.playinghome and (enc.icclub_home == plan.idclub):
                if enc.games:
                    for ix, g in enumerate(enc.games):
                        g.idnumber_home = plan.games[ix].idnumber_home or 0
                else:
                    enc.games = [
                        ICGame(
                            idnumber_home=g.idnumber_home or 0,
                            idnumber_visit=0,
                            result="",
                        )
                        for g in plan.games
                    ]
            if not plan.playinghome and (enc.icclub_visit == plan.idclub):
                if enc.games:
                    for ix, g in enumerate(enc.games):
                        g.idnumber_visit = plan.games[ix].idnumber_visit or 0
                else:
                    enc.games = [
                        ICGame(
                            idnumber_home=0,
                            idnumber_visit=g.idnumber_visit or 0,
                            result="",
                        )
                        for g in plan.games
                    ]
        await DbICSeries.update(
            {"division": plan.division, "index": plan.index},
            {"rounds": [r.model_dump() for r in s.rounds]},
        )


async def mgmt_saveICresults(results: List[ICResult]) -> None:
    """
    save a list of results per team
    """
    for res in results:
        s = await DbICSeries.find_single(
            {"division": res.division, "index": res.index, "_model": ICSeries}
        )
        curround = None
        for r in s.rounds:
            if r.round == res.round:
                curround = r
        if not curround:
            raise RdBadRequest(description="InvalidRound")
        for enc in curround.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            if (
                enc.icclub_home == res.icclub_home
                and enc.icclub_visit == res.icclub_visit
            ):
                enc.games = [
                    ICGame(
                        idnumber_home=g.idnumber_home,
                        idnumber_visit=g.idnumber_visit,
                        result=g.result,
                    )
                    for g in res.games
                ]
                if res.signhome_idnumber:
                    enc.signhome_idnumber = res.signhome_idnumber
                    enc.signhome_ts = res.signhome_ts
                if res.signvisit_idnumber:
                    enc.signvisit_idnumber = res.signvisit_idnumber
                    enc.signvisit_ts = res.signvisit_ts
                calc_points(enc)
        await DbICSeries.update(
            {"division": res.division, "index": res.index},
            {"rounds": [r.model_dump() for r in s.rounds]},
        )
        if enc.played:
            standings = await DbICStandings.find_single(
                {
                    "division": s.division,
                    "index": s.index,
                    "_model": ICStandings,
                }
            )
            if not standings.dirtytime:
                await DbICStandings.update(
                    {
                        "division": s.division,
                        "index": s.index,
                    },
                    {"dirtytime": datetime.now(timezone.utc)},
                )


async def clb_saveICresults(results: List[ICResult]) -> None:
    """
    save a list of results per team
    """
    for res in results:
        s = await DbICSeries.find_single(
            {"division": res.division, "index": res.index, "_model": ICSeries}
        )
        curround = None
        for r in s.rounds:
            if r.round == res.round:
                curround = r
        if not curround:
            raise RdBadRequest(description="InvalidRound")
        for enc in curround.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            if (
                enc.icclub_home == res.icclub_home
                and enc.icclub_visit == res.icclub_visit
            ):
                enc.games = [
                    ICGame(
                        idnumber_home=g.idnumber_home,
                        idnumber_visit=g.idnumber_visit,
                        result=g.result,
                    )
                    for g in res.games
                ]
                if res.signhome_idnumber:
                    enc.signhome_idnumber = res.signhome_idnumber
                    enc.signhome_ts = res.signhome_ts
                if res.signvisit_idnumber:
                    enc.signvisit_idnumber = res.signvisit_idnumber
                    enc.signvisit_ts = res.signvisit_ts
                calc_points(enc)
        await DbICSeries.update(
            {"division": res.division, "index": res.index},
            {"rounds": [r.model_dump() for r in s.rounds]},
        )
        if enc.played:
            standings = await DbICStandings.find_single(
                {
                    "division": s.division,
                    "index": s.index,
                    "_model": ICStandings,
                }
            )
            if not standings.dirtytime:
                await DbICStandings.update(
                    {
                        "division": s.division,
                        "index": s.index,
                    },
                    {"dirtytime": datetime.now(timezone.utc)},
                )


def calc_points(enc: ICEncounter):
    """
    calculate the matchpoint and boardpoint for the encounter
    """
    enc.boardpoint2_home = 0
    enc.boardpoint2_visit = 0
    enc.matchpoint_home = 0
    enc.matchpoint_visit = 0
    allfilled = True
    for g in enc.games:
        if g.result in ["1-0", "1-0 FF"]:
            enc.boardpoint2_home += 2
        if g.result == "½-½":
            enc.boardpoint2_home += 1
            enc.boardpoint2_visit += 1
        if g.result in ["0-1", "0-1 FF"]:
            enc.boardpoint2_visit += 2
        if not g.result:
            allfilled = False
    if allfilled:
        if enc.boardpoint2_home > enc.boardpoint2_visit:
            enc.matchpoint_home = 2
        if enc.boardpoint2_home == enc.boardpoint2_visit:
            enc.matchpoint_home = 1
            enc.matchpoint_visit = 1
        if enc.boardpoint2_home < enc.boardpoint2_visit:
            enc.matchpoint_visit = 2
        enc.played = True


async def anon_getICencounterdetails(
    division: int, index: str, round: int, icclub_home: int, icclub_visit: int
) -> List[ICGameDetails]:
    icserie = await DbICSeries.find_single(
        {
            "_model": ICSeries,
            "division": division,
            "index": index,
        }
    )
    details = []
    for r in icserie.rounds:
        if r.round == round:
            for enc in r.encounters:
                if not enc.icclub_home or not enc.icclub_visit:
                    continue
                if enc.icclub_home == icclub_home and enc.icclub_visit == icclub_visit:
                    homeclub = await anon_getICclub(icclub_home)
                    homeplayers = {p.idnumber: p for p in homeclub.players}
                    visitclub = await anon_getICclub(icclub_visit)
                    visitplayers = {p.idnumber: p for p in visitclub.players}
                    for g in enc.games:
                        hpl = homeplayers[g.idnumber_home]
                        vpl = visitplayers[g.idnumber_visit]
                        details.append(
                            ICGameDetails(
                                idnumber_home=g.idnumber_home,
                                fullname_home=f"{hpl.last_name}, {hpl.first_name}",
                                rating_home=hpl.assignedrating,
                                idnumber_visit=g.idnumber_visit,
                                fullname_visit=f"{vpl.last_name}, {vpl.first_name}",
                                rating_visit=vpl.assignedrating,
                                result=g.result,
                            )
                        )
    return details


async def calc_standings(series: ICSeries) -> ICStandings:
    """
    calculates and persists standings of a series
    """
    try:
        standings = await DbICStandings.find_single(
            {
                "division": series.division,
                "index": series.index,
                "_model": ICStandings,
            }
        )
    except RdNotFound:
        standings = ICStandings(
            division=series.division,
            index=series.index,
            teams=[
                ICTeamStanding(
                    name=t.name,
                    idclub=t.idclub,
                    pairingnumber=t.pairingnumber,
                    matchpoints=0,
                    boardpoints=0,
                    games=[],
                )
                for t in series.teams
                if t.idclub
            ],
        )
        await DbICStandings.add(standings.model_dump(exclude_none=True))
    logger.info("standing {standing}")
    for r in series.rounds:
        for enc in r.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            if not enc.played:
                continue
            team_home = next(
                (x for x in standings.teams if x.pairingnumber == enc.pairingnr_home),
                None,
            )
            team_visit = next(
                (x for x in standings.teams if x.pairingnumber == enc.pairingnr_visit),
                None,
            )
            logger.info(f"team home visit {team_home} {team_visit}")
            game_home = next(
                (
                    x
                    for x in team_home.games
                    if x.pairingnumber_opp == team_visit.pairingnumber
                ),
                None,
            )
            logger.info(f"game home {game_home}")
            if not game_home:
                game_home = ICTeamGame(
                    pairingnumber_opp=team_visit.pairingnumber, round=r.round
                )
                team_home.games.append(game_home)
            game_visit = next(
                (
                    x
                    for x in team_visit.games
                    if x.pairingnumber_opp == team_home.pairingnumber
                ),
                None,
            )
            logger.info(f"game visit {game_visit}")
            if not game_visit:
                game_visit = ICTeamGame(
                    pairingnumber_opp=team_home.pairingnumber, round=r.round
                )
                team_visit.games.append(game_visit)
            game_home.matchpoints = enc.matchpoint_home
            game_home.boardpoints2 = enc.boardpoint2_home
            game_visit.matchpoints = enc.matchpoint_visit
            game_visit.boardpoints2 = enc.boardpoint2_visit
    for t in standings.teams:
        t.matchpoints = sum(g.matchpoints for g in t.games)
        t.boardpoints = sum(g.boardpoints2 for g in t.games) / 2
    standings.teams = sorted(
        standings.teams, key=lambda t: (-t.matchpoints, -t.boardpoints)
    )
    standings.dirtytime = None
    return await DbICStandings.update(
        {
            "division": series.division,
            "index": series.index,
        },
        standings.model_dump(),
        {"_model": ICStandings},
    )


async def anon_getICstandings(idclub: int) -> List[ICStandings] | None:
    """
    get the Standings by club
    """
    options = {"_model": ICStandings}
    if idclub:
        options["teams.idclub"] = idclub
    docs = await DbICStandings.find_multiple(options)
    for ix, d in enumerate(docs):
        dirty = d.dirtytime.replace(tzinfo=timezone.utc) if d.dirtytime else None
        if dirty and dirty < datetime.now(timezone.utc) - timedelta(minutes=5):
            logger.info("recalc standings")
            series = await DbICSeries.find_single(
                {"division": d.division, "index": d.index, "_model": ICSeries}
            )
            docs[ix] = await calc_standings(series)
    return docs
