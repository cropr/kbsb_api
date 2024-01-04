import asyncio
from pymongo import MongoClient
from reddevil.core import get_mongodb, connect_mongodb, register_app
from kbsb.interclubs.md_interclubs import DbICSeries
from kbsb.interclubs.interclubs import calc_standings


async def standings():
    for s in await DbICSeries.find_multiple({"_model": DbICSeries.DOCUMENTTYPE}):
        await calc_standings(s)


async def main():
    register_app(settingsmodule="kbsb.settings")
    connect_mongodb()
    await standings()


if __name__ == "__main__":
    asyncio.run(main())
