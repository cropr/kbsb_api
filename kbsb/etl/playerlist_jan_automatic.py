import asyncio
from datetime import datetime, time, timedelta, timezone
from csv import DictWriter
from reddevil.core import get_mongodb, connect_mongodb, register_app
from kbsb.interclubs.md_interclubs import (
    ICClub,
)

allclubs = []


async def read_interclubclubs():
    print("reading interclub clubs")
    for clb in await DbICClub.find_multiple({"_model": ICClub, "enrolled": True}):
        allclubs.append(clb)


async def autoassign_players(c: ICClub):
    minelo = 1150
    nonassigned = [] 
    for p in c.players:
        if p.nature in 
        if c.assignedrating == 0:
            nonassigned


async def main():
    register_app(settingsmodule="kbsb.settings")
    connect_mongodb()
    await read_interclubclubs()
    for c in allclubs:
        await autoassign_players(c)


if __name__ == "__main__":
    asyncio.run(main())
