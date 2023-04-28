# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2021

import logging
from fastapi import HTTPException, BackgroundTasks
from reddevil.core import RdException
from kbsb.main import app
from kbsb.core.site import fetchI18n

log = logging.getLogger("kbsb")


@app.post("/api/site/fetchi18n", response_model=str)
async def api_fetchMarkdownFiles():
    try:
        return await fetchI18n()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call generate_site")
        raise HTTPException(status_code=500)
