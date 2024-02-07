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
