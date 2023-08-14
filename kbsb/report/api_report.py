import logging

from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from reddevil.core import RdException, bearer_schema, validate_token
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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/report")


@router.get("/mgmt/file", response_model=FileListOut)
async def api_get_files(
    reports: int = 0, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await getFiles()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_files")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/file", response_model=FileListOut)
async def api_anon_get_files(reports: int = 0):
    try:
        return await getFiles(dict(reports=reports))
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_files")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mgmt/file", response_model=str)
async def aoi_create_file(
    p: FileIn, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await createFile(p)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call create_file")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/file/{id}", response_model=FileOptional)
async def api_get_file(
    id: str, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await getFile(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_file")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/mgmt/file/{id}")
async def api_delete_file(
    id: str, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        await deleteFile(id)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call delete_file")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/mgmt/file/{id}", response_model=FileOptional)
async def api_updateFile(
    id: str, p: FileUpdate, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        await validate_token(auth)
        return await updateFile(id, p)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call update_file")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/filecontent/{url}")
async def api_get_filecontent(
    url: str, auth: HTTPAuthorizationCredentials = Depends(bearer_schema)
):
    try:
        return await getFileContent(url)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_filecontent")
        raise HTTPException(status_code=500, detail="Internal Server Error!")
