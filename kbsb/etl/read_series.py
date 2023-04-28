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
    DbInterclubSeries,
    InterclubSeries,
    InterclubTeam,
    add_team_to_series,
)

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()


class MongodbInterclubSeriesWriter:
    async def __aenter__(self):
        await connect_mongodb()
        return self

    async def __aexit__(self, *args):
        await close_mongodb()

    async def write(self, team):
        it = InterclubTeam(
            division=team.Afdeling,
            titular=[],
            idclub=team.Clubnr,
            index="" if str(team.Reeks) == "nan" else team.Reeks,
            name=team.Ploegnaam,
            pairingnumber=team.Nr,
            playersplayed=[],
        )
        print(it)
        await add_team_to_series(it)


class ExcelSeries:
    def __init__(self, *args, **kwargs):
        self.df = pd.read_excel("../share/data/reeks_22_23.xlsx")
        print(self.df)

    def __iter__(self):
        self.it = self.df.itertuples(name="Team")
        return self.it

    def __next__(self):
        for team in self.it:
            yield team


async def main():
    async with MongodbInterclubSeriesWriter() as writer:
        db = await get_mongodb()
        await db.interclubseries.drop()
        for team in ExcelSeries():
            await writer.write(team)


if __name__ == "__main__":
    asyncio.run(main())
