import logging

log = logging.getLogger(__name__)

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from reddevil.core import RdException, bearer_schema, validate_token
from kbsb.main import app
from kbsb.report.report import (
    createFile,
    deleteFile,
    getFile,
    getFileContent,
    getFiles,
    updateFile,
)
from kbsb.report.md_report import (
    FileIn,
    FileListOut,
    FileOptional,
    FileUpdate,
)


@app.get("/api/v1/files", response_model=FileListOut)
async def api_getFiles(
    reports: int = 0, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await getFiles()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call get_files")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/a/files", response_model=FileListOut)
async def api_anon_getFiles(reports: int = 0):
    try:
        return await getFiles(dict(reports=reports))
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call get_files")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/api/v1/files", response_model=str)
async def aoi_createFile(
    p: FileIn, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await createFile(p)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call create_file")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/file/{id}", response_model=FileOptional)
async def api_getFile(
    id: str, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await getFile(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call get_file")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/api/v1/file/{id}")
async def api_deleteFile(
    id: str, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        await deleteFile(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call delete_file")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/api/v1/file/{id}", response_model=FileOptional)
async def api_updateFile(
    id: str, p: FileUpdate, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await updateFile(id, p)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call update_file")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/api/v1/filecontent/{url}")
async def api_getFilecontent(
    url: str, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        return await getFileContent(url)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        log.exception("failed api call get_filecontent")
        raise HTTPException(status_code=500, detail="Internal Server Error!")
