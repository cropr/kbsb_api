# copyright Ruben Decrop 2012 - 2024

import logging

logger = logging.getLogger(__name__)


from typing import cast, List, Dict, Any
import openpyxl
from tempfile import NamedTemporaryFile
from fastapi.responses import Response


from reddevil.core import (
    RdNotFound,
    get_settings,
)
from reddevil.mail import sendEmail

from kbsb.interclubs import (
    ICPlayer,
    ICClubDB,
    ICClubItem,
    ICPlayerUpdate,
    ICPlayerValidationError,
    ICTeam,
    DbICClub,
    DbICSeries,
    PLAYERSPERDIVISION,
)


settings = get_settings()


# Interclub Clubs, Playerlist and Teams


async def anon_getICteams(idclub: int, options: dict = {}) -> List[ICTeam]:
    """
    get all the interclub teams for a club available in all divisions
    """
    series = await DbICSeries.find_multiple({"teams.idclub": idclub})
    teams = []
    for s in series:
        for t in s.teams:
            if t.idclub == idclub:
                teams.append(t)
    return teams


async def anon_getICclub(idclub: int, options: Dict[str, Any] = {}) -> ICClubDB | None:
    """
    get IC club by idclub, returns None if nothing found
    filter players for active players
    """
    filter = options.copy()
    filter["_model"] = ICClubDB
    filter["idclub"] = idclub
    club = await DbICClub.find_single(filter)
    club.players = [p for p in club.players if p.nature in ["assigned", "requestedin"]]
    return club


async def anon_getICclubs() -> List[ICClubItem] | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    options = {
        "_model": ICClubItem,
        "enrolled": True,
        "_fieldlist": {i: 1 for i in ICClubItem.model_fields.keys()},
    }
    return await DbICClub.find_multiple(options)


async def clb_getICclub(idclub: int, options: Dict[str, Any] = {}) -> ICClubDB | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    filter = options.copy()
    filter["_model"] = ICClubDB
    filter["idclub"] = idclub
    return await DbICClub.find_single(filter)


async def clb_updateICplayers(idclub: int, pi: ICPlayerUpdate) -> None:
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
                    logger.info(f"player {p} moved to transferdeletes")
                    # the transfer is removed
                    transferdeletes.append(p)
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
        # we need to remove the transfer from the receiving club if it is existing
        try:
            receivingclub = await clb_getICclub(t.idclubvisit)
            rcplayers = receivingclub.players
            trplayers = [x for x in rcplayers if x.idnumber != t.idnumber]
            dictplayers = [p.model_dump() for p in trplayers]
            await DbICClub.update({"idclub": t.idclubvisit}, {"players": dictplayers})
        except RdNotFound:
            pass


async def clb_validateICPlayers(
    idclub: int, pi: ICPlayerUpdate
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
            "teamcount": PLAYERSPERDIVISION[t.division],
            "name": t.name,
        }
        totaltitulars += PLAYERSPERDIVISION[t.division]
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
    clubs = await DbICClub.find_multiple({"_model": ICClubDB})
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
    club = await DbICClub.find_single({"_model": ICClubDB, "idclub": idclub})
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
