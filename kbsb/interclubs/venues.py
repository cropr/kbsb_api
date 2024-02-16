# copyright Ruben Decrop 2012 - 2024

import logging

logger = logging.getLogger(__name__)


from typing import cast, List, Dict, Any
import io, csv
from tempfile import NamedTemporaryFile
from fastapi.responses import Response


from reddevil.core import (
    RdNotFound,
    get_settings,
)
from reddevil.mail import sendEmail
from kbsb.club import get_club_idclub, club_locale
from kbsb.interclubs import (
    ICVenueDB,
    ICVenueIn,
    DbICVenue,
)

# CRUD actions


async def create_interclubvenues(iv: ICVenueDB) -> str:
    """
    create a new InterclubVenues returning its id
    """
    ivdict = iv.model_dump()
    ivdict.pop("id", None)
    return await DbICVenue.add(ivdict)


async def get_interclubvenues(id: str, options: dict = {}) -> ICVenueDB:
    """
    get the interclubvenues
    """
    filter = options.copy()
    filter["_model"] = filter.pop("_model", ICVenueDB)
    filter["id"] = id
    return cast(ICVenueDB, await DbICVenue.find_single(filter))


async def get_interclubvenues_clubs(options: dict = {}) -> List[ICVenueDB]:
    """
    get the interclubvenues of all clubs
    """
    filter = options.copy()
    filter["_model"] = filter.pop("_model", ICVenueDB)
    return [cast(ICVenueDB, x) for x in await DbICVenue.find_multiple(filter)]


async def update_interclubvenues(
    id: str, iu: ICVenueDB, options: dict = {}
) -> ICVenueDB:
    """
    update a interclub venue
    """
    options1 = options.copy()
    options1["_model"] = options1.get("_model", ICVenueDB)
    iudict = iu.model_dump(exclude_unset=True)
    iudict.pop("id", None)
    return cast(ICVenueDB, await DbICVenue.update(id, iudict, options1))


async def getICvenues(idclub: int) -> ICVenueDB:
    try:
        venues = await DbICVenue.find_single({"_model": ICVenueDB, "idclub": idclub})
    except RdNotFound as e:
        return ICVenueDB(id="", idclub=idclub, venues=[])
    return venues


# business logic


async def set_interclubvenues(idclub: str, ivi: ICVenueIn) -> ICVenueDB:
    club = await get_club_idclub(idclub)
    logger.debug(f"set_interclubvenues: {idclub} {ivi}")
    if not club:
        raise RdNotFound(description="ClubNotFound")
    locale = club_locale(club)
    logger.info(f"locale {locale}")
    settings = get_settings()
    ivn = await getICvenues(idclub)
    iv = ICVenueDB(
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
        vnsdict = vns.model_dump()
        idclub = vnsdict.get("idclub")
        name_long = vnsdict.get("name_long")
        name_short = vnsdict.get("name_short")
        venues = vnsdict.get("venues")
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
