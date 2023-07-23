# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging

logger = logging.getLogger(__name__)

from typing import cast, Optional
import io
import csv

from reddevil.core import encode_model, RdNotFound, get_settings
from reddevil.mail import sendEmail, MailParams

from fastapi import BackgroundTasks
from . import (
    Club,
    ClubIn,
    ClubList,
    ClubItem,
    ClubAnon,
    ClubRoleNature,
    DbClub,
    Visibility,
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
    _class = options.pop("_class", Club)
    filter = dict(**options)
    fdict = await DbClub.find_single(filter)
    club = encode_model(fdict, _class)
    if club.address is None:
        club.address = ""
    logger.debug(f"got club {club}")
    return club


async def get_clubs(options: dict = {}) -> ClubList:
    """
    get all the Clubs
    """
    _class = options.pop("_class", ClubItem)
    docs = await DbClub.find_multiple(options)
    clubs = [encode_model(d, _class) for d in docs]
    return ClubList(clubs=clubs)


async def update_club(idclub: int, updates: dict, options: dict = {}) -> Club:
    """
    update a club
    """

    validator = options.pop("_class", Club)
    cdict = await DbClub.update({"idclub": idclub}, updates, options)
    return cast(Club, encode_model(cdict, validator))


# business  calls


async def create_club(c: ClubIn, user: str) -> str:
    """
    create a new Club returning its id
    """
    return await DbClub.add(c.dict(), {"_username": user})


async def get_club_idclub(idclub: int) -> Optional[Club]:
    """
    find an club by idclub, returns None if not found
    """
    try:
        return await get_club({"idclub": idclub})
    except RdNotFound:
        return None


async def get_anon_clubs() -> ClubList:
    """
    get anon view of all  active clubs
    """
    cl = await get_clubs(
        {
            "enabled": True,
            "_class": ClubAnon,
        }
    )
    # now filter all the visibility of the boardmembers and set None fields to ""
    for c in cl.clubs:
        for role, member in c.boardmembers.items():
            if member.email_visibility != Visibility.public:
                member.email = "#NA"
            if member.mobile_visibility != Visibility.public:
                member.mobile = "#NA"
        if c.address is None:
            c.address = ""
        if c.venue is None:
            c.venue = ""
        if c.website is None:
            c.website = ""
    return cl


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


async def verify_club_access(idclub: int, idnumber: int, role: ClubRoleNature) -> bool:
    """
    checks if the person identified by idnumber belongs to the memberlist
    of role inside a club, identified by idclub (an int) or id (a str),
    if check fails
    """
    idnumber = int(idnumber)
    logger.debug(f"verify {idclub} {idnumber} {role}")
    club = await get_club({"idclub": idclub})
    logger.debug(f"club in verify {club.idclub}")
    if club and club.clubroles:
        for r in club.clubroles:
            logger.debug(f"r: {r.nature} {r.memberlist}")
            if role == r.nature:
                if idnumber in r.memberlist:
                    return True
                else:
                    logger.debug(f"member not in list {r.nature}")
    raise RdForbidden


async def set_club(idclub: int, c: Club, user: str, bt: BackgroundTasks = None) -> Club:
    """
    set club details ans send confirmation email
    """

    # remove doubles in all clubroles.memberlist items
    for cr in c.clubroles:
        cr.memberlist = list(set(cr.memberlist))
    props = c.dict(exclude_unset=True)
    logger.debug(f"update props {props}")
    clb = await update_club(idclub, props, {"_username": user})
    if bt:
        bt.add_task(sendnotification, clb)
    logger.debug(f"club {clb.idclub} updated")
    return clb


from kbsb.oldkbsb import get_member


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


def sendnotification(clb: Club):
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
    ctx = clb.dict()
    ctx["locale"] = locale
    ctx["email_main"] = ctx["email_main"] or ""
    ctx["venue"] = ctx["venue"].replace("\n", "<br>")
    ctx["address"] = ctx["address"].replace("\n", "<br>")
    ctx["federation"] = ctx["federation"].value
    ctx["bm"] = [
        {
            "first_name": b.first_name,
            "last_name": b.last_name,
            "function": settings.BOARDROLES[f][locale],
        }
        for f, b in clb.boardmembers.items()
    ]
    for cr in clb.clubroles:
        if cr.nature == ClubRoleNature.ClubAdmin:
            members = [get_member(idmember) for idmember in cr.memberlist]
            ctx["clubadmin"] = [
                {
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                }
                for p in members
            ]
        if cr.nature == ClubRoleNature.InterclubAdmin:
            members = [get_member(idmember) for idmember in cr.memberlist]
            ctx["interclubadmin"] = [
                {
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                }
                for p in members
            ]
        if cr.nature == ClubRoleNature.InterclubCaptain:
            members = [get_member(idmember) for idmember in cr.memberlist]
            ctx["interclubcaptain"] = [
                {
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                }
                for p in members
            ]
    sendEmail(mp, ctx, "club details")
