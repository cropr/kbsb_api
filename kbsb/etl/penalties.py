import asyncio
from datetime import datetime, time, timedelta, timezone
from csv import DictWriter
from reddevil.core import get_mongodb, connect_mongodb, register_app
from kbsb.interclubs.md_interclubs import (
    DbICSeries,
    ICSeries,
    DbICClub,
    ICClub,
    ICRound,
    ICTeam,
    ICROUNDS,
)

allseries = {}
issues = []
playerratings = {}
playertitular = {}
titulars = {}
allclubs = []
doublepairings = [
    (174, 3, "A", 1, 12),
    (601, 3, "D", 6, 7),
    (601, 4, "A", 6, 7),
    (607, 4, "A", 9, 10),
]


def report_issue(series, gameix, pairingnr, opp_pairingnr, reason):
    clubnames = {t.pairingnumber: t.name for t in series.teams}
    issues.append(
        {
            "reason": reason,
            "division": f"{series.division}{series.index}",
            "boardnumber": gameix + 1,
            "guilty": clubnames[pairingnr],
            "opponent": clubnames[opp_pairingnr] if opp_pairingnr else "",
        }
    )


def getround(series: ICSeries, rnd: int) -> ICRound:
    for round in series.rounds:
        if round.round == rnd:
            return round
    print(f"We're fucked to get round {rnd} of {series.division}{series.index}")


def getteam(clb, teamname) -> ICTeam:
    for t in clb.teams:
        if t.name == teamname:
            return t
    print(f"We're fucked to get team {teamname}")


async def read_interclubseries():
    print("reading interclub results")
    for s in await DbICSeries.find_multiple({"_model": ICSeries}):
        allseries[(s.division, s.index)] = s


async def read_interclubratings():
    print("reading interclub ratings")
    for clb in await DbICClub.find_multiple({"_model": ICClub, "enrolled": True}):
        allclubs.append(clb)
        for p in clb.players:
            if p.nature in ["assigned", "requestedin"]:
                playerratings[p.idnumber] = p.assignedrating
                if p.titular:
                    teamix = int(p.titular.split(" ")[-1])
                    team = getteam(clb, p.titular)
                    playertitular[p.idnumber] = {
                        "team": teamix,
                        "division": team.division,
                        "index": team.index,
                        "pairingnumber": team.pairingnumber,
                    }


def check_round(r):
    print("checking forfaits")
    check_forfaits(r)
    print("checking signatures")
    check_signatures(r)
    print("checking player order")
    check_order_players(r)
    print("checking average")
    check_average_elo(r)
    print("checking same series")
    check_titular_ok(r)
    print("checking same division")
    check_reserves_in_single_series(r)
    print("done")


def check_forfaits(rnd: int):
    for s in allseries.values():
        round = getround(s, rnd)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            for ix, g in enumerate(enc.games):
                if g.result in ["1-0 FF", "0-0 FF"]:
                    report_issue(
                        s,
                        ix,
                        enc.pairingnr_visit,
                        enc.pairingnr_home,
                        "forfait away",
                    )
                if g.result in ["0-1 FF", "0-0 FF"]:
                    report_issue(
                        s,
                        ix,
                        enc.pairingnr_home,
                        enc.pairingnr_visit,
                        "forfait home",
                    )


def check_signatures(rnd: int):
    for s in allseries.values():
        round = getround(s, rnd)
        nextday = ICROUNDS[rnd] + timedelta(days=1)
        homesigndate = datetime.combine(nextday, time(0)).astimezone(timezone.utc)
        visitsigndate = datetime.combine(nextday, time(12)).astimezone(timezone.utc)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            if not enc.signhome_ts:
                report_issue(
                    s,
                    -1,
                    enc.pairingnr_home,
                    enc.pairingnr_visit,
                    "signature home missing",
                )
            elif enc.signhome_ts.astimezone(timezone.utc) > homesigndate:
                report_issue(
                    s,
                    -1,
                    enc.pairingnr_home,
                    enc.pairingnr_visit,
                    "signature home too late",
                )
            if not enc.signvisit_ts:
                report_issue(
                    s,
                    -1,
                    enc.pairingnr_visit,
                    enc.pairingnr_home,
                    "signature away missing",
                )
            elif enc.signvisit_ts.astimezone(timezone.utc) > visitsigndate:
                report_issue(
                    s,
                    -1,
                    enc.pairingnr_visit,
                    enc.pairingnr_home,
                    "signature home too late",
                )


def check_order_players(rnd):
    for s in allseries.values():
        round = getround(s, rnd)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            rhome = 3000
            rvisit = 3000
            for ix, g in enumerate(enc.games):
                if not g.idnumber_home or not g.idnumber_visit:
                    continue
                newhome = playerratings[g.idnumber_home]
                newvisit = playerratings[g.idnumber_visit]
                if newhome > rhome:
                    report_issue(
                        s, ix, enc.pairingnr_home, 0, "rating order not correct"
                    )
                if newvisit > rvisit:
                    report_issue(
                        s, ix, enc.pairingnr_visit, 0, "rating order not correct"
                    )
                rhome = newhome
                rvisit = newvisit


def check_average_elo(rnd):
    for clb in allclubs:
        avgdivs = {}
        for t in clb.teams:
            serie = allseries[(t.division, t.index)]
            round = getround(serie, rnd)
            encounters = [
                e
                for e in round.encounters
                if t.pairingnumber in (e.pairingnr_home, e.pairingnr_visit)
            ]
            if len(encounters) != 1:
                print(
                    f"We're fucked to get encounter of {t.name} in {serie.division}{serie.index}"
                )
            enc = encounters[0]
            if not enc.icclub_home or not enc.icclub_visit:  # bye
                continue
            if not enc.boardpoint2_home or not enc.boardpoint2_visit:  # not played]
                continue
            if t.pairingnumber == enc.pairingnr_home:
                ratings = [
                    playerratings[g.idnumber_home] for g in enc.games if g.idnumber_home
                ]
            if t.pairingnumber == enc.pairingnr_visit:
                ratings = [
                    playerratings[g.idnumber_visit]
                    for g in enc.games
                    if g.idnumber_visit
                ]
            avgdiv = avgdivs.setdefault(serie.division, [])
            if ratings:
                avgdiv.append(sum(ratings) / len(ratings))
        maxdiv2 = max(avgdivs.get(2, [0]))
        maxdiv3 = max(avgdivs.get(3, [0]))
        maxdiv4 = max(avgdivs.get(4, [0]))
        maxdiv5 = max(avgdivs.get(5, [0]))
        mindiv1 = avgdivs.get(1, [3000])[0]
        mindiv2 = min(avgdivs.get(2, [3000]))
        mindiv3 = min(avgdivs.get(3, [3000]))
        if maxdiv2 > mindiv1:
            print(t.idclub, "Avg elo too high in division 2")
        if maxdiv3 > min(mindiv1, mindiv2):
            print(t.idclub, "Avg elo too high in division 3")
        if maxdiv4 > min(mindiv1, mindiv2, mindiv3):
            print(t.idclub, "Avg elo too high in division 4")
        if maxdiv5 > min(mindiv1, mindiv2, mindiv3):
            print(t.idclub, "Avg elo too high in division 4")


def check_titular_ok(rnd):
    for s in allseries.values():
        round = getround(s, rnd)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            for ix, g in enumerate(enc.games):
                if g.idnumber_home in playertitular:
                    if s.division > playertitular[g.idnumber_home]["division"]:
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_home,
                            0,
                            "Titular played in a division too low",
                        )
                    if (
                        s.division == playertitular[g.idnumber_home]["division"]
                        and s.index != playertitular[g.idnumber_home]["index"]
                    ):
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_home,
                            0,
                            "Titular played in wrong series",
                        )
                    if (
                        s.division == playertitular[g.idnumber_home]["division"]
                        and s.index == playertitular[g.idnumber_home]["index"]
                        and enc.pairingnr_home
                        != playertitular[g.idnumber_home]["pairingnumber"]
                    ):
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_home,
                            0,
                            "Titular played in wrong team in the series",
                        )
                if g.idnumber_visit in playertitular:
                    if s.division > playertitular[g.idnumber_visit]["division"]:
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_visit,
                            0,
                            "Titular played in a division too low",
                        )
                    if (
                        s.division == playertitular[g.idnumber_visit]["division"]
                        and s.index != playertitular[g.idnumber_visit]["index"]
                    ):
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_visit,
                            0,
                            "Titular played in wrong series",
                        )
                    if (
                        s.division == playertitular[g.idnumber_visit]["division"]
                        and s.index == playertitular[g.idnumber_visit]["index"]
                        and enc.pairingnr_visit
                        != playertitular[g.idnumber_visit]["pairingnumber"]
                    ):
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_visit,
                            0,
                            "Titular played in wrong team in the series",
                        )


def check_reserves_in_single_series(r):
    for idclub, division, index, pnr1, pnr2 in doublepairings:
        series = allseries[(division, index)]
        # build up sets of previous players
        players1 = set()
        players2 = set()
        for rr in range(1, r):
            round = getround(series, rr)
            for enc in round.encounters:
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if pnr1 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for g in enc.games:
                        if pnr1 == enc.pairingnr_home:
                            players1.add(g.idnumber_home)
                        else:
                            players1.add(g.idnumber_visit)
                if pnr2 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for g in enc.games:
                        if pnr2 == enc.pairingnr_home:
                            players2.add(g.idnumber_home)
                        else:
                            players2.add(g.idnumber_visit)
        # print("club", idclub)
        # print("pl1", players1)
        # print("pl2", players2)
        # now check the players of this round
        round = getround(series, r)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            if pnr1 in (enc.pairingnr_home, enc.pairingnr_visit):
                for ix, g in enumerate(enc.games):
                    # print("game pn1", g.idnumber_home, "-", g.idnumber_visit)
                    if pnr1 == enc.pairingnr_home and g.idnumber_home in players2:
                        report_issue(
                            series,
                            ix,
                            enc.icclub_home,
                            enc.icclub_visit,
                            "player {g.idnumber_home} already played in other team of series",
                        )
                    elif pnr1 == enc.pairingnr_visit and g.idnumber_visit in players2:
                        report_issue(
                            series,
                            ix,
                            enc.icclub_visit,
                            enc.icclub_home,
                            "player {g.idnumber_visit} already played in other team of series",
                        )
            if pnr2 in (enc.pairingnr_home, enc.pairingnr_visit):
                for ix, g in enumerate(enc.games):
                    # print("game pn2", g.idnumber_home, "-", g.idnumber_visit)
                    if pnr2 == enc.pairingnr_home and g.idnumber_home in players1:
                        report_issue(
                            series,
                            ix,
                            enc.icclub_home,
                            enc.icclub_visit,
                            "player {g.idnumber_home} already played in other team of series",
                        )
                    elif pnr2 == enc.pairingnr_visit and g.idnumber_visit in players1:
                        report_issue(
                            series,
                            ix,
                            enc.icclub_visit,
                            enc.icclub_home,
                            "player {g.idnumber_visit} already played in other team of series",
                        )


async def main():
    register_app(settingsmodule="kbsb.settings")
    connect_mongodb()
    await read_interclubseries()
    await read_interclubratings()
    check_round(4)
    with open("penalties.csv", "w") as f:
        writer = DictWriter(
            f, fieldnames=["reason", "division", "boardnumber", "guilty", "opponent"]
        )
        writer.writeheader()
        writer.writerows(issues)


if __name__ == "__main__":
    asyncio.run(main())
