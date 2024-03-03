# copyright Ruben Decrop 2012 - 2024

import logging

logger = logging.getLogger(__name__)


from typing import cast, List, Dict, Any
from datetime import datetime, timezone, timedelta, time
import openpyxl
from tempfile import NamedTemporaryFile
from fastapi.responses import Response


from reddevil.core import (
    RdBadRequest,
    RdNotFound,
    get_settings,
    get_mongodb,
    encode_model,
)
from reddevil.mail import sendEmail

from kbsb.interclubs import (
    ICEncounter,
    ICGame,
    ICGameDetails,
    ICPlanningItem,
    ICResultItem,
    ICSeries,
    ICSeriesDB,
    ICStandingsDB,
    ICTeamGame,
    ICTeamStanding,
    DbICSeries,
    DbICStandings,
    ICROUNDS,
    GAMERESULT,
    PLAYERSPERDIVISION,
    anon_getICclub,
)

settings = get_settings()

# planning, results, standings


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
    icdate = datetime.combine(ICROUNDS[round], time(15))
    async for doc in coll.find(filter, proj):
        s = encode_model(doc, ICSeries)
        if datetime.now() < icdate:
            for r in s.rounds:
                for enc in r.encounters:
                    enc.games = []
        series.append(s)
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


async def clb_saveICplanning(plannings: List[ICPlanningItem]) -> None:
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
                        )
                        for g in plan.games
                    ]
        await DbICSeries.update(
            {"division": plan.division, "index": plan.index},
            {"rounds": [r.model_dump() for r in s.rounds]},
        )


async def mgmt_saveICresults(results: List[ICResultItem]) -> None:
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
                and enc.pairingnr_home == res.pairingnr_home
                and enc.pairingnr_visit == res.pairingnr_visit
            ):
                enc.games = [
                    ICGame(
                        idnumber_home=g.idnumber_home,
                        idnumber_visit=g.idnumber_visit,
                        result=g.result,
                        overruled=g.overruled,
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
        await calc_standings(s)


async def clb_saveICresults(results: List[ICResultItem]) -> None:
    """
    save a list of results per team
    """
    # TODO check for time
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
                    "_model": ICStandingsDB,
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
    forfeited = False
    for g in enc.games:
        result = (
            g.overruled
            if g.overruled and g.overruled != GAMERESULT.NOTOVERRULED
            else g.result
        )
        if result in [GAMERESULT.HOMEWIN, GAMERESULT.FORFEIT_VISIT]:
            enc.boardpoint2_home += 2
        if result in [GAMERESULT.VISITWIN, GAMERESULT.FORFEIT_HOME]:
            enc.boardpoint2_visit += 2
        if result in [GAMERESULT.DRAW, GAMERESULT.SPECIAL_5_0]:
            enc.boardpoint2_home += 1
        if result in [GAMERESULT.DRAW, GAMERESULT.SPECIAL_0_5]:
            enc.boardpoint2_visit += 1
        if result == GAMERESULT.FORFEIT_TEAM:
            forfeited = True
        if result == GAMERESULT.NOTPLAYED:
            allfilled = False
    if allfilled:
        enc.played = True
        if not forfeited:
            if enc.boardpoint2_home > enc.boardpoint2_visit:
                enc.matchpoint_home = 2
            if enc.boardpoint2_home == enc.boardpoint2_visit:
                enc.matchpoint_home = 1
                enc.matchpoint_visit = 1
            if enc.boardpoint2_home < enc.boardpoint2_visit:
                enc.matchpoint_visit = 2


async def anon_getICencounterdetails(
    division: int,
    index: str,
    round: int,
    icclub_home: int,
    icclub_visit: int,
    pairingnr_home: int,
    pairingnr_visit: int,
) -> List[ICGameDetails]:
    icserie = await DbICSeries.find_single(
        {
            "_model": ICSeries,
            "division": division,
            "index": index,
        }
    )
    icdate = datetime.combine(ICROUNDS[round], time(15))
    if datetime.now() < icdate:
        return []
    details = []
    for r in icserie.rounds:
        if r.round == round:
            for enc in r.encounters:
                if not enc.icclub_home or not enc.icclub_visit:
                    continue
                if (
                    enc.icclub_home == icclub_home
                    and enc.icclub_visit == icclub_visit
                    and enc.pairingnr_home == pairingnr_home
                    and enc.pairingnr_visit == pairingnr_visit
                ):
                    homeclub = await anon_getICclub(icclub_home)
                    homeplayers = {p.idnumber: p for p in homeclub.players}
                    visitclub = await anon_getICclub(icclub_visit)
                    visitplayers = {p.idnumber: p for p in visitclub.players}
                    for g in enc.games:
                        if not g.idnumber_home or not g.idnumber_visit:
                            continue
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
                                overruled=g.overruled,
                            )
                        )
    return details


async def calc_standings(series: ICSeries) -> ICStandingsDB:
    """
    calculates and persists standings of a series
    """
    logger.info(f"recalculate standings {series.division}{series.index}")
    try:
        standings = await DbICStandings.find_single(
            {
                "division": series.division,
                "index": series.index,
                "_model": ICStandingsDB,
            }
        )
    except RdNotFound:
        standings = ICStandingsDB(
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
            game_home = next(
                (
                    x
                    for x in team_home.games
                    if x.pairingnumber_opp == team_visit.pairingnumber
                ),
                None,
            )
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
        {"_model": ICStandingsDB},
    )


async def anon_getICstandings(idclub: int) -> List[ICStandingsDB] | None:
    """
    get the Standings by club
    """
    options = {"_model": ICStandingsDB}
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


async def mgmt_register_teamforfeit(division: int, index: str, name: str) -> None:
    """
    register a team default
    don't do this for the last round or the standings won't be correct
    """
    logger.info("teamforfeit")
    series = cast(
        ICSeries,
        await DbICSeries.find_single(
            {
                "division": division,
                "index": index,
                "_model": ICSeriesDB,
            }
        ),
    )
    logger.info(f"found series {series.division} {series.index}")
    for t in series.teams:
        if t.name == name:
            team = t
            break
    else:
        raise RdNotFound(description="TeamNotFound")
    team.teamforfeit = True
    for r in series.rounds:
        for enc in r.encounters:
            if team.pairingnumber in [enc.pairingnr_home, enc.pairingnr_visit]:
                if enc.games:
                    for g in enc.games:
                        g.overruled = GAMERESULT.FORFEIT_TEAM
                else:
                    enc.games = [
                        ICGame(overruled=GAMERESULT.FORFEIT_TEAM)
                        for ix in range(PLAYERSPERDIVISION[division])
                    ]
                calc_points(enc)
    await DbICSeries.update(
        {"_id": series.id},
        {
            "rounds": [r.model_dump() for r in series.rounds],
            "teams": [t.model_dump() for t in series.teams],
        },
    )
    logger.info("series updated")
    await calc_standings(series)
    logger.info("standings updated")
