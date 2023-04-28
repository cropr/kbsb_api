import asyncio
import pandas as pd
from fastapi import FastAPI
from reddevil.core import (
    register_app,
    get_settings,
    connect_mongodb,
    close_mongodb,
    get_mongodb,
)

from kbsb.interclub import (
    DbInterclubClub,
)
from kbsb.club import get_clubs

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()


def df_playerlist(icc):
    titulars = {}
    for t in icc.teams:
        for p in t.titular:
            titulars[p] = t.name
    data = [
        {
            "idnumber": p.idnumber,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "idclub": p.idclub,
            "Nat Elo": p.natrating,
            "Fide Elo": p.fiderating,
            "Assigned Elo": p.assignedrating,
            "Titulars": titulars.get(p.idnumber, ""),
        }
        for p in icc.players
    ]
    df = pd.DataFrame(data, index=[i + 1 for i in range(len(icc.players))])
    return df


def df_transferout(icc):
    data = [
        {
            "idnumber": p.idnumber,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "From club": p.idoriginalclub,
            "To club": p.idvisitingclub,
        }
        for p in icc.transfersout
    ]
    df = pd.DataFrame(data, index=[i + 1 for i in range(len(icc.transfersout))])
    return df


async def main():
    await connect_mongodb()
    with pd.ExcelWriter("playerlist_301.xlsx") as writer:
        db = await get_mongodb()
        iccs = (await DbInterclubClub.p_find_multiple({"idclub": 301})).clubs
        df_p = df_playerlist(iccs[0])
        df_p.to_excel(writer, sheet_name="playerlist 301", index_label="Nr.")
        df_t = df_transferout(iccs[0])
        df_t.to_excel(writer, sheet_name="transfers out 301", index_label="Nr.")
    await close_mongodb()


if __name__ == "__main__":
    asyncio.run(main())
