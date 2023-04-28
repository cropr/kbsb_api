# copyright Ruben Decrop 2012 - 2022

import logging
import telnetlib
from typing import cast, Any, Optional, List
from datetime import datetime
import io, csv

from reddevil.core import (
    RdBadRequest,
    RdNotFound,
    encode_model,
    get_settings,
)
from reddevil.mail import sendEmail, MailParams

from kbsb.interclub.md_interclub import (
    DbInterclubClub,
    DbInterclubSeries,
    InterclubPlayer,
    InterclubTransfer,
    InterclubVenue,
    InterclubClub,
    InterclubClubOptional,
    InterclubClubList,
)
from kbsb.club import find_club, club_locale, DbClub
from kbsb.oldkbsb import get_member
from . import (
    DbInterclubEnrollment,
    DbInterclubPrevious,
    DbInterclubVenues,
    InterclubEnrollment,
    InterclubEnrollmentIn,
    InterclubEnrollmentList,
    InterclubPrevious,
    InterclubTeam,
    InterclubSeries,
    InterclubVenues,
    InterclubVenuesIn,
    InterclubVenuesList,
    TransferRequestValidator,
)
from reddevil.page.page import PageList, DbPage, isactive

logger = logging.getLogger(__name__)

INTERCLUB_EMAIL = "interclubs@frbe-kbsb-ksb.be"

# basic CRUD actions


async def create_interclubenrollment(enr: InterclubEnrollment) -> str:
    """
    create a new InterclubEnrollment returning its id
    """
    enrdict = enr.dict()
    enrdict.pop("id", None)
    return await DbInterclubEnrollment.add(enrdict)


async def get_interclubenrollment(id: str, options: dict = {}) -> InterclubEnrollment:
    """
    get the interclub enrollment
    """
    _class = options.pop("_class", InterclubEnrollment)
    filter = dict(id=id, **options)
    fdict = await DbInterclubEnrollment.find_single(filter)
    return encode_model(fdict, _class)


async def get_interclubenrollments(options: dict = {}) -> InterclubEnrollmentList:
    """
    get the interclub enrollment
    """
    logger.debug(f"get_interclubenrollments {options}")
    _class = options.pop("_class", InterclubEnrollment)
    docs = await DbInterclubEnrollment.find_multiple(options)
    enrs = [encode_model(d, _class) for d in docs]
    return InterclubEnrollmentList(enrollments=enrs)


async def update_interclubenrollment(
    id: str, iu: InterclubEnrollment, options: dict = {}
) -> InterclubEnrollment:
    """
    update a interclub enrollment
    """
    validator = options.pop("_class", InterclubEnrollment)
    iu.id = None  # don't override the id
    cdict = await DbInterclubEnrollment.update(id, iu.dict(exclude_unset=True), options)
    return cast(InterclubEnrollment, encode_model(cdict, validator))


async def create_interclubprevious(c: InterclubPrevious) -> str:
    """
    create a new InterclubPrevious returning its id
    """
    return await DbInterclubPrevious.add(c.dict())


async def create_interclubvenues(iv: InterclubVenues) -> str:
    """
    create a new InterclubVenues returning its id
    """
    ivdict = iv.dict()
    ivdict.pop("id", None)
    return await DbInterclubVenues.add(ivdict)


async def get_interclubvenues(id: str, options: dict = {}) -> InterclubVenues:
    """
    get the interclubvenues
    """
    _class = options.pop("_class", InterclubVenues)
    filter = dict(id=id, **options)
    fdict = await DbInterclubVenues.find_single(filter)
    return encode_model(fdict, _class)


async def get_interclubvenues_clubs(options: dict = {}) -> InterclubVenuesList:
    """
    get the interclubvenues of all clubs
    """
    _class = options.pop("_class", InterclubVenues)
    docs = await DbInterclubVenues.find_multiple(options)
    logger.debug(f"ivsclubs docs: {docs}")
    clubvenues = [encode_model(d, _class) for d in docs]
    return InterclubVenuesList(clubvenues=clubvenues)


async def update_interclubvenues(
    id: str, iu: InterclubVenues, options: dict = {}
) -> InterclubVenues:
    """
    update a interclub venue
    """
    validator = options.pop("_class", InterclubVenues)
    iu.id = None  # don't override the id
    docdict = await DbInterclubVenues.update(id, iu.dict(exclude_unset=True), options)
    return cast(InterclubVenues, encode_model(docdict, validator))


# business logic


async def find_interclubenrollment(idclub: str) -> Optional[InterclubEnrollment]:
    """
    find an enrollment by idclub
    """
    logger.debug(f"find_interclubenrollment {idclub}")
    enrs = (await get_interclubenrollments({"idclub": idclub})).enrollments
    return enrs[0] if enrs else None


async def set_interclubenrollment(
    idclub: str, ie: InterclubEnrollmentIn
) -> InterclubEnrollment:
    """
    set enrollment (and overwrite it if it already exists)
    """
    club = await find_club(idclub)
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    settings = get_settings()
    enr = await find_interclubenrollment(idclub)
    if enr:
        nenr = await update_interclubenrollment(
            enr.id,
            InterclubEnrollment(
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
            InterclubEnrollment(
                idclub=idclub,
                locale=locale,
                name_long=club.name_long,
                name_short=club.name_short,
                teams1=ie.teams1,
                teams2=ie.teams2,
                teams3=ie.teams3,
                teams4=ie.teams4,
                teams5=ie.teams5,
                wishes=ie.wishes,
            )
        )
        nenr = await get_interclubenrollment(id)
    receiver = [club.email_main, INTERCLUB_EMAIL] if club.email_main else [INTERCLUB_EMAIL]        
    if club.email_interclub:
        receiver.append(club.email_interclub)
    logger.debug(f"EMAIL settings {settings.EMAIL}")
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL["bcc"],
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
    for enr in await DbInterclubEnrollment.find_multiple(
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


async def find_interclubvenues_club(idclub: str) -> Optional[InterclubVenues]:
    clvns = (await get_interclubvenues_clubs({"idclub": idclub})).clubvenues
    return clvns[0] if clvns else None


async def set_interclubvenues(idclub: str, ivi: InterclubVenuesIn) -> InterclubVenues:
    club = await find_club(idclub)
    logger.debug(f"set_interclubvenues: {idclub} {ivi}")
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    logger.info(f"locale {locale}")
    settings = get_settings()
    ivn = await find_interclubvenues_club(idclub)
    iv = InterclubVenues(
        idclub=idclub,
        name_long=club.name_long,
        name_short=club.name_short,
        venues=ivi.venues,
    )
    if ivn:
        logger.info(f"update interclubvenues {ivn.id} {iv}")
        niv = await update_interclubvenues(ivn.id, iv)
    else:
        logger.info(f"insert interclubvenues {iv}")
        id = await create_interclubvenues(iv)
        niv = await get_interclubvenues(id)
    receiver = [club.email_main, INTERCLUB_EMAIL] if club.email_main else [INTERCLUB_EMAIL]        
    if club.email_interclub:
        receiver.append(club.email_interclub)
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL["bcc"],
        subject="Interclub 2022-23",
        template="interclub/venues_{locale}.md",
    )
    nivdict = niv.dict()
    nivdict["locale"] = locale
    sendEmail(mp, nivdict, "interclub venues")


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
    for vns in await DbInterclubVenues.find_multiple():
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


async def add_team_to_series(team: InterclubTeam) -> None:
    """
    add a team to the Interclub series
    overwrite the existing team if its position is already taken
    """
    s = await DbInterclubSeries.find_multiple(
        {
            "division": team.division,
            "index": team.index,
        }
    )
    if s:
        id = s[0]["id"]
    else:
        id = await DbInterclubSeries.add(
            {
                "division": team.division,
                "index": team.index,
                "teams": [
                    InterclubTeam(
                        division=team.division,
                        titular=[],
                        idclub=0,
                        index=team.index,
                        name="",
                        pairingnumber=i + 1,
                        playersplayed=[],
                    ).dict()
                    for i in range(12)
                ],
            }
        )
    series = await DbInterclubSeries.find_single({"id": id})
    for t in series["teams"]:
        if t["pairingnumber"] == team.pairingnumber:
            t["idclub"] = team.idclub
            t["titular"] = [pl.dict() for pl in team.titular]
            t["name"] = team.name
    await DbInterclubSeries.update(id, {"teams": series["teams"]})


async def find_teamclubsseries(idclub: int) -> List[InterclubTeam]:
    """
    find all teams of a club in the series
    """
    allseries = (await DbInterclubSeries.p_find_multiple({})).allseries
    allteams = []
    for s in allseries:
        for t in s.teams:
            if t.idclub == idclub:
                allteams.append(t)
    return allteams


async def find_interclubclub(idclub: int) -> Optional[InterclubClub]:
    """
    find a club by idclub, returns None if nothing found
    """
    logger.debug(f"find_interclubclub {idclub}")
    clubs = (await DbInterclubClub.p_find_multiple({"idclub": idclub})).clubs
    logger.debug(f"clubs {clubs}")
    return clubs[0] if clubs else None


async def setup_interclubclub(idclub: int) -> InterclubClub:
    """
    finds an interclubclub, and set it up if it does not exist
    clubs that don't partipate still get a record, but attribute teams is empty
    """
    logger.debug(f"setup_interclubclub {idclub}")
    icc = await find_interclubclub(idclub)
    if icc:
        return icc
    logger.debug(f"no icc for {idclub}")
    teams = await find_teamclubsseries(idclub)
    if teams:
        name = " ".join(teams[0].name.split()[:-1])
        icc = InterclubClub(
            name=name,
            idclub=idclub,
            teams=teams,
            players=[],
            transfersout=[],
        )
    else:
        name = (await find_club(idclub)).name_short
        icc = InterclubClub(
            name=name,
            idclub=idclub,
            teams=[],
            players=[],
            transfersout=[],
        )
    logger.info(f"creating icc for club {idclub}")
    id = await DbInterclubClub.add(
        {
            "name": icc.name,
            "idclub": icc.idclub,
            "teams": [t.dict() for t in icc.teams],
            "players": [],
            "transfersout": [],
        }
    )
    logger.info(f"icc id {id}")
    # return await DbInterclubClub.p_find_single({"id", id})


async def transfer_players(requester: int, tr: TransferRequestValidator) -> None:
    """
    perform a transfer of a list of players
    """
    origclub = await find_interclubclub(tr.idoriginalclub)
    if not origclub:
        raise RdNotFound(description="InterclubOrigClubNotFound")
    visitclub = await find_interclubclub(tr.idvisitingclub)
    if not visitclub:
        raise RdNotFound(description="InterclubVisitClubNotFound")
    if not visitclub.teams:
        raise RdBadRequest(description="VisitingClubNotParticipating")
    for m in tr.members:
        am = get_member(m)
        if not am:
            logger.info("cannot transfer player {m} because player is inactive")
            continue
        ict = InterclubTransfer(
            idnumber=m,
            idoriginalclub=tr.idoriginalclub,
            idvisitingclub=tr.idvisitingclub,
            request_date=datetime.utcnow(),
            request_id=requester,
        )
        # check if member is in orig playerlist and remove if necessary
        for ix, p in enumerate(origclub.players):
            if p.idnumber == m:
                origclub.players.pop(ix)
                break
        # check if member is in orig transfersout and remove if necessary
        for ix, p in enumerate(origclub.transfersout):
            if p.idnumber == m:
                origclub.transfersout.pop(ix)
                break
        # fill in the transfer in origclub.transfersout
        origclub.transfersout.append(ict)
        # add player to visitclub.playerlist
        for ix, p in enumerate(visitclub.players):
            if p.idnumber == m:
                break
        else:
            visitclub.players.append(
                InterclubPlayer(
                    assignedrating=max(am.fiderating, am.natrating),
                    fiderating=am.fiderating,
                    first_name=am.first_name,
                    idnumber=m,
                    idclub=origclub.idclub,
                    natrating=am.natrating,
                    last_name=am.last_name,
                    transfer=True,
                )
            )
    DbInterclubClub.p_update(
        origclub.id,
        InterclubClubOptional(
            players=origclub.players, transfersout=origclub.transfersout
        ),
    )
    DbInterclubClub.p_update(
        visitclub.id, InterclubClubOptional(players=visitclub.players)
    )


async def update_clublist(idclub: int, playerlist: List[int]) -> None:
    """
    update the clublist with a list of members, belonging to that club
    """
    icc = await find_interclubclub(idclub)
    playerset = {p.idnumber for p in icc.players}
    for p in playerlist:
        am = get_member(p)
        if not am:
            logger.info("cannot add player {m} to clublist: player is inactive")
            continue
        if am.idclub != idclub:
            logger.info(
                "cannot add player {m} to clublist player is not member of {idclub}"
            )
            continue
        if p in playerset:
            continue
        playerset.add(p)
        icc.players.append(
            InterclubPlayer(
                assignedrating=max(am.fiderating, am.natrating),
                fiderating=am.fiderating,
                first_name=am.first_name,
                idnumber=p,
                idclub=icc.idclub,
                natrating=am.natrating,
                last_name=am.last_name,
                transfer=False,
            )
        )
    DbInterclubClub.p_update(icc.id, InterclubClubOptional(players=icc.players))


async def set_interclubclub(idclub: int, icc: InterclubClubOptional) -> InterclubClub:
    """
    updates the interclubclub
    """
    club = await find_club(idclub)
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    ic = await find_interclubclub(idclub)
    settings = get_settings()
    icupdated = await DbInterclubClub.p_update(ic.id, icc)
    receiver = [club.email_main, INTERCLUB_EMAIL] if club.email_main else [INTERCLUB_EMAIL]        
    if club.email_interclub:
        receiver.append(club.email_interclub)
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL["blindcopy"],
        subject="Interclub 2022-23",
        template="interclub/club_{locale}.md",
    )
    icdict = icupdated.dict()
    icdict["locale"] = locale
    sendEmail(mp, icdict, "interclub playerlist")
    return icupdated


async def get_announcements() -> PageList:
    """
    get all the pages
    """
    dl = await DbPage.find_multiple(
        {
            "doctype": "interclub",
            "enabled": True,
            "_fieldlist": [
                "creationtime",
                "enabled",
                "expirationdate",
                "name",
                "modificationtime",
                "publicationdate",
                "slug",
                "id",
                "body",
                "intro",
                "title",
            ],
            "publicationdate": {"$ne": ""},
        }
    )
    ap = [x for x in dl if isactive(x)]
    ap = sorted(ap, key=lambda x: x["publicationdate"], reverse=True)
    return PageList(items=ap)
