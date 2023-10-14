import asyncio
from pymongo import MongoClient
from reddevil.core import get_mongodb, connect_mongodb, register_app
from kbsb.interclubs.md_interclubs import DbICSeries, ICSeries


async def setplayed():
    for s in await DbICSeries.find_multiple({"_model": ICSeries}):
        for r in s.rounds:
            if r.round != 1:
                continue
            for enc in r.encounters:
                enc.played = True
        await DbICSeries.update(
            {"division": s.division, "index": s.index},
            {"rounds": s.model_dump()["rounds"]},
        )


async def main():
    register_app(settingsmodule="kbsb.settings")
    connect_mongodb()
    await setplayed()


if __name__ == "__main__":
    asyncio.run(main())
