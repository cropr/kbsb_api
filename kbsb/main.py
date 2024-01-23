# copyright Ruben Decrop 2015-22

import os.path
import logging, logging.config

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from reddevil.core import (
    register_app,
    get_settings,
    connect_mongodb,
    close_mongodb,
    get_mongodb,
)
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
def startup():
    connect_mongodb()


@app.on_event("shutdown")
def shutdown():
    close_mongodb()


# import different modules

logger.info("importing api ")
from reddevil.account import api_account
from kbsb.club import api_club
from kbsb.report import api_report
from kbsb.member import api_member

logger.info("before importing interclubs ")
from kbsb.interclubs import api_interclubs
from kbsb.content import api_content
from kbsb.ts import api_ts

app.include_router(api_account.router)
app.include_router(api_club.router)
app.include_router(api_report.router)
app.include_router(api_member.router)
logger.info("before api interclubs")
app.include_router(api_interclubs.router)
app.include_router(api_content.router)
app.include_router(api_ts.router)

origins = ["http://localhost:3000", "https://www.frbe-kbsb-ksb.be"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
async def api_helloworlds():
    return "Hello world"


logger.info("setting route names")
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name[4:]

logger.info("initialisation done")
