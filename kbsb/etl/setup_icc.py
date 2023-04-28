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
    setup_interclubclub,
)
from kbsb.club import get_clubs

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()


class MongodbInterclubClubWriter:
    async def __aenter__(self):
        await connect_mongodb()
        return self

    async def __aexit__(self, *args):
        await close_mongodb()

    async def write(self, idclub):
        print('setup ', idclub)
        await setup_interclubclub(idclub)


async def main():
    async with MongodbInterclubClubWriter() as writer:
        db = await get_mongodb()
        await db.interclubclub.drop()
        clubs = (await get_clubs()).clubs
        for c in clubs:
            await writer.write(c.idclub)


if __name__ == "__main__":
    asyncio.run(main())
