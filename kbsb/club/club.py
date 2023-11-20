# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging

logger = logging.getLogger(__name__)

from typing import cast, Optional, List
import io
import csv
import openpyxl
from tempfile import NamedTemporaryFile
from fastapi.responses import Response

from reddevil.core import encode_model, RdNotFound, get_settings, RdBadRequest
from reddevil.mail import sendEmail, MailParams

from fastapi import BackgroundTasks
from .md_club import (
    Club,
    ClubIn,
    ClubItem,
    ClubRoleNature,
    DbClub,
)
from kbsb.core import RdForbidden


CLUB_EMAIL = "admin@frbe-kbsb-ksb.be"

# basic CRUD actions


async def add_club(clb: dict, options: dict = {}) -> str:
    """
    create a new Club returning its id
    """
    clb.extend(options)
    return await DbClub.add(clb)


async def delete_club(id: str) -> None:
    """
    delete Club
    """
    await DbClub.delete(id)


async def get_club(options: dict = {}) -> Club:
    """
    get the club
    """
    # TODO make difference according to access rights
    _class = options.pop("_class", Club)
    filter = dict(**options)
    fdict = await DbClub.find_single(filter)
    club = encode_model(fdict, _class)
    if club.address is None:
        club.address = ""
    return club


async def get_clubs(options: dict = {}) -> List[ClubItem]:
    """
    get all the Clubs
    """
    _class = options.pop("_class", ClubItem)
    docs = await DbClub.find_multiple(options)
    clubs = [encode_model(d, _class) for d in docs]
    return clubs


async def update_club(idclub: int, updates: dict, options: dict = {}) -> Club:
    """
    update a club
    """

    validator = options.pop("_class", Club)
    cdict = await DbClub.update({"idclub": idclub}, updates, options)
    return cast(Club, encode_model(cdict, validator))


# business  calls


async def create_club(c: ClubIn, user: str = "admin") -> str:
    """
    create a new Club returning its id
    """
    docin = c.dict()
    docin["_username"] = user
    return await DbClub.add(docin)


async def get_club_idclub(idclub: int) -> Optional[Club]:
    """
    find an club by idclub, returns None if not found
    """
    try:
        return await get_club({"idclub": idclub})
    except RdNotFound:
        return None


async def get_anon_clubs() -> List[ClubItem]:
    """
    get anon view of all  active clubs
    """
    clubs = await get_clubs(
        {
            "enabled": True,
            "_class": ClubItem,
        }
    )
    return clubs


async def get_csv_clubs(options: dict = {}) -> io.StringIO:
    """
    get all the Clubs
    """
    options.pop("_class", None)
    fieldnames = ["idclub", "name_short", "name_long", "enabled", "email_main"]
    docs = await DbClub.find_multiple(options)
    docs = [{k: v for k, v in d.items() if k in fieldnames} for d in docs]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(docs)
    return stream


async def verify_club_access(idclub: int, idnumber: int, role: str) -> bool:
    """
    checks if the person identified by idnumber belongs to the memberlist
    of role inside a club, identified by idclub (an int) or id (a str),
    if check fails.
    """
    logger.info(f"XYZ login {idclub} {idnumber} {role}")
    idnumber = int(idnumber)
    roles = role.split(",")
    allowedroles = [e.value for e in ClubRoleNature]
    for r in roles:
        if r not in allowedroles:
            raise RdBadRequest(description="InvalidRole")
    club = await get_club({"idclub": idclub})
    if not club:
        logger.info(f"XYZ club {idnumber} not found")
        raise RdForbidden
    logger.info(f"club {club.clubroles}")
    for r in roles:
        for cr in club.clubroles:
            logger.info(f"XYZ checking {r} {cr.nature.value}")
            if r == cr.nature.value:
                logger.info(f"XYZ checking {idnumber} {cr.memberlist}")
                if idnumber in cr.memberlist:
                    return True
    raise RdForbidden


async def set_club(idclub: int, c: Club, user: str, bt: BackgroundTasks = None) -> Club:
    """
    set club details ans send confirmation email
    """

    # remove doubles in all clubroles.memberlist items
    for cr in c.clubroles or []:
        cr.memberlist = list(set(cr.memberlist))
    props = c.model_dump(exclude_unset=True)
    logger.debug(f"update props {props}")
    clb = await update_club(idclub, props, {"_username": user})
    logger.info(f"updated clb {clb}")
    if bt:
        bt.add_task(sendnotification, clb)
    logger.debug(f"club {clb.idclub} updated")
    return clb


from kbsb.member import anon_getmember


def club_locale(club: Club):
    """
    returns the locale of a club, return "nl" if unknown, as this is most common
    """
    if club.federation.startswith("V"):
        return "nl"
    if club.federation.startswith("F"):
        return "fr"
    if club.federation.startswith("D"):
        return "de"
    return "nl"


async def sendnotification(clb: Club):
    settings = get_settings()
    receiver = [clb.email_main, CLUB_EMAIL] if clb.email_main else [CLUB_EMAIL]
    locale = club_locale(clb)
    if clb.email_admin:
        receiver.append(clb.email_admin)
    mp = MailParams(
        locale=locale,
        receiver=",".join(receiver),
        sender="noreply@frbe-kbsb-ksb.be",
        bcc=settings.EMAIL["blindcopy"],
        subject="Club Details",
        template="club/clubdetails_{locale}.md",
    )
    logger.debug(f"receiver {mp.receiver}")
    ctx = clb.model_dump()
    ctx["locale"] = locale
    ctx["email_main"] = ctx["email_main"] or ""
    ctx["venue"] = ctx["venue"].replace("\n", "<br>")
    ctx["address"] = ctx["address"].replace("\n", "<br>")
    ctx["federation"] = ctx["federation"].value
    ctx["bm"] = [
        {
            "first_name": b.first_name,
            "last_name": b.last_name,
            # TODO
            # "function": settings.BOARDROLES[f][locale],
            "function": f,
        }
        for f, b in clb.boardmembers.items()
    ]
    for cr in clb.clubroles:
        if cr.nature == ClubRoleNature.ClubAdmin:
            members = [(await anon_getmember(idmember)) for idmember in cr.memberlist]
            ctx["clubadmin"] = [
                {
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                }
                for p in members
            ]
        if cr.nature == ClubRoleNature.InterclubAdmin:
            members = [(await anon_getmember(idmember)) for idmember in cr.memberlist]
            ctx["interclubadmin"] = [
                {
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                }
                for p in members
            ]
        if cr.nature == ClubRoleNature.InterclubCaptain:
            members = [(await anon_getmember(idmember)) for idmember in cr.memberlist]
            ctx["interclubcaptain"] = [
                {
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                }
                for p in members
            ]
    sendEmail(mp, ctx, "club details")


async def mgmt_mailinglist():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["club", "idclub", "general", "admin", "finance", "interclubs"])
    clubs = await DbClub.find_multiple({"_model": Club})
    for c in clubs:
        if not c.enabled:
            continue
        general = set(c.email_main.split(",")) if c.email_main else set()
        admin = set(c.email_admin.split(",")) if c.email_admin else set()
        admin = admin | general
        secretary = c.boardmembers.get("secretary")
        if secretary and secretary.email:
            admin.add(secretary.email)
        finance = set(c.email_finance.split(",")) if c.email_finance else set()
        finance = finance | general
        treasurer = c.boardmembers.get("treasurer")
        if treasurer and treasurer.email:
            finance.add(treasurer.email)
        interclubs = set(c.email_interclub.split(",")) if c.email_interclub else set()
        interclubs = interclubs | general
        interclub_director = c.boardmembers.get("interclub_director")
        if interclub_director and interclub_director.email:
            interclubs.add(interclub_director.email)
        ws.append(
            [
                c.name_long,
                c.idclub,
                ",".join(general),
                ",".join(admin),
                ",".join(finance),
                ",".join(interclubs),
            ]
        )
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        return Response(
            content=tmp.read(),
            headers={"Content-Disposition": "attachment; filename=mailinglist.xlsx"},
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
