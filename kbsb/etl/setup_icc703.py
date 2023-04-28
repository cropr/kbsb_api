import asyncio
import pandas as pd
from fastapi import FastAPI
from reddevil.core import (
    register_app,
    get_settings,
    connect_mongodb,
    close_mongodb,
)

from kbsb.interclub import setup_interclubclub

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()


async def main():
    await connect_mongodb()
    await setup_interclubclub(703)
    await close_mongodb()

if __name__ == "__main__":

    asyncio.run(main())
