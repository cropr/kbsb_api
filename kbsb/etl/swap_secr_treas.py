import asyncio
import logging
from fastapi import FastAPI
from reddevil.core import (
    register_app,
    get_settings,
    connect_mongodb,
)
import kbsb.main
from kbsb.club.md_club import DbClub

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()
logger = logging.getLogger("kbsb")


async def main():
    idclub = 962
    await connect_mongodb()
    club = await DbClub.find_single({"idclub": idclub})
    bm = club["boardmembers"]
    print("club", idclub)
    print("secretary", bm["secretary"]["first_name"], bm["secretary"]["last_name"])
    print("treasurer", bm["treasurer"]["first_name"], bm["treasurer"]["last_name"])
    print("swapping")
    bm["secretary"], bm["treasurer"] = bm["treasurer"], bm["secretary"]
    club = await DbClub.update({"idclub": idclub}, {"boardmembers": bm})
    bm = club["boardmembers"]
    print("secretary", bm["secretary"]["first_name"], bm["secretary"]["last_name"])
    print("treasurer", bm["treasurer"]["first_name"], bm["treasurer"]["last_name"])


if __name__ == "__main__":
    asyncio.run(main())
