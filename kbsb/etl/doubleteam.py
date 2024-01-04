import asyncio
import json
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
doubleteams = []


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


def check_doubleteams():
    print("checking double teams")
    for k, s in allseries.items():
        teams = set()
        doublefound = []
        for t in s.teams:
            if t.idclub in teams:
                doublefound.append(t.idclub)
            else:
                teams.add(t.idclub)
        for d in doublefound:
            double = {"idclub": d, "teams": [], "k": k}
            for t in s.teams:
                if t.idclub == d:
                    double["teams"].append(t)
            doubleteams.append(double)
    print("done")


async def main():
    register_app(settingsmodule="kbsb.settings")
    connect_mongodb()
    await read_interclubseries()
    check_doubleteams()
    with open("double.csv", "w") as f:
        writer = DictWriter(
            f, fieldnames=["idclub", "division", "index", "team1", "team2"]
        )
        writer.writeheader()
        for d in doubleteams:
            t1 = d["teams"][0:1]
            t2 = d["teams"][1:2]
            if t2:
                td2 = {"name": t2[0].name, "pairingnumber": t2[0].pairingnumber}
            writer.writerow(
                {
                    "idclub": d["idclub"],
                    "division": d["k"][0],
                    "index": d["k"][1],
                    "team1": t1[0].pairingnumber,
                    "team2": t2[0].pairingnumber,
                }
            )


if __name__ == "__main__":
    asyncio.run(main())
