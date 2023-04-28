# copyright Ruben Decrop 2015-22

import os.path
import logging, logging.config

from fastapi import FastAPI
from fastapi.routing import APIRoute
from reddevil.core import register_app, get_settings, connect_mongodb, close_mongodb
from kbsb import version


# register app
app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version=version,
)
register_app(app, "kbsb.settings", "/api")
settings = get_settings()
logging.config.dictConfig(settings.LOG_CONFIG)
log = logging.getLogger(__name__)
log.info(f"Starting KBSB mode {settings.MODE}")

from kbsb.settings import ls

log.info(ls)

# set up the database async handlers
app.add_event_handler("startup", connect_mongodb)
app.add_event_handler("shutdown", close_mongodb)

# import different modules

import reddevil.account
import reddevil.page
import kbsb.club
import kbsb.report
import kbsb.oldkbsb
import kbsb.interclub

@app.get("/api")
async def api_helloworlds():
    return "Hello world"

for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name[4:]

log.info("initialisation done")

