# copyright Ruben Decrop 2015-22

import os.path
import logging, logging.config

from fastapi import FastAPI
from fastapi.routing import APIRoute
from reddevil.core import register_app, get_settings, connect_mongodb, close_mongodb
from kbsb import version
import kbsb.core.i18n


# register app
app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version=version,
)
register_app(app, "kbsb.settings", "/api")
settings = get_settings()
logging.config.dictConfig(settings.LOG_CONFIG)
logger = logging.getLogger(__name__)
logger.info(f"Starting KBSB mode {settings.MODE}")

from kbsb.settings import ls

logger.info(ls)
logger.debug("log level is DEBUG")


@app.on_event("startup")
async def startup():
    await connect_mongodb()


@app.on_event("shutdown")
async def shutdown():
    await close_mongodb()


# import different modules

from reddevil.account import api_account
from kbsb.club import api_club
from kbsb.report import api_report
from kbsb.member import api_member
from kbsb.interclubs import api_interclubs
from kbsb.ts import api_ts

app.include_router(api_account.router)
app.include_router(api_club.router)
app.include_router(api_report.router)
app.include_router(api_member.router)
app.include_router(api_interclubs.router)
app.include_router(api_ts.router)


@app.get("/api")
async def api_helloworlds():
    return "Hello world"


for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name[4:]

logger.info("initialisation done")
