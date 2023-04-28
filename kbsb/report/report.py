# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2019

import logging

log = logging.getLogger(__name__)

import uuid
from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone
from mimetypes import guess_type
from random import randrange
from base64 import b64encode, b64decode
from typing import cast, Any, IO
from fastapi.responses import Response

from reddevil.core import (
    RdInternalServerError,
    RdNotFound,
    RdBadRequest,
    get_settings,
)

from . import FileIn, FileOut, FileUpdate, FileListOut, FileOptional, DbFile


def encode_file(e: dict, _class=FileOptional) -> FileOptional:
    try:
        eo = _class(**e)
    except Exception:
        log.exception(f"cannot encode File {e}")
        raise RdInternalServerError(description="CannotEncodeFile")
    return cast(FileOptional, eo)


def path_prefix(fdict: dict):
    """
    return the path prefix for a file
    """
    topic = fdict.get("topic")
    if topic == "Report General Assembly":
        return "reports_ga"
    if topic == "Report Board Meeting":
        return "reports_bm"
    return "other"


async def createFile(d: FileIn) -> str:
    """
    create a new File returning its id
    """
    tsnow = datetime.now(tz=timezone.utc)
    dd = d.dict()
    ns = dd["name"].split(".")
    dd["id"] = str(uuid.uuid4())
    dd["url"] = f'{".".join(ns[0:-1])}__{randrange(1000000):06d}.{ns[-1]}'
    dd["mimetype"] = guess_type(dd["name"])[0]
    content = b64decode(dd.pop("content"))
    fileobj = BytesIO(content)
    dd["filelength"] = len(content)
    dd["topicdate"] = ""
    dd["path"] = f'{path_prefix(dd)}/{dd["url"]}'
    rf = await DbFile.add(dd)
    writeFilecontent(dd["path"], fileobj)
    return rf


async def deleteFile(id: str) -> None:
    d = await getFile(
        id,
        {
            "_class": FileOptional,
            "_fieldlist": ["path"],
        },
    )
    # TODO delete the fileobj
    await DbFile.delete(id)


async def getFile(id: str, options: dict = {}) -> FileOptional:
    """
    get the file
    """
    _class = options.pop("_class", FileOut)
    filter = dict(id=id, **options)
    fdict = await DbFile.find_single(filter)
    return encode_file(fdict, _class)


async def getFiles(options: dict = {}) -> FileListOut:
    """
    get all the Files
    """
    if options.pop("reports", None):
        options["topic"] = {"$in": ["Report General Assembly", "Report Board Meeting"]}
    _class = options.pop("_class", FileOut)
    docs = await DbFile.find_multiple(options)
    files = [encode_file(d, _class) for d in docs]
    return FileListOut(files=files)


async def getFileContent(url: str) -> Response:
    """
    get the file
    """
    fd = await DbFile.find_single(
        {
            "url": url,
            "_fieldlist": ["url", "mimetype", "topic"],
        }
    )
    prefix = path_prefix(fd)
    content = readFilecontent(f"{prefix}/{fd['url']}")
    return Response(content=content, media_type=fd["mimetype"])


async def updateFile(id: str, d: FileUpdate) -> FileOptional:
    """
    update a file
    """
    oldfiledict = await DbFile.find_single({"id": id})
    fd = d.dict(exclude_unset=True)
    try:
        content = readFilecontent(oldfiledict["path"])
    except Exception as e:
        log.warning(
            f'updateFile: existing file content is empty at {oldfiledict["url"]}'
        )
        content = b""
    if "name" in fd:
        name = f'{fd["name"]}__{randrange(1000000):06d}'
        fd["mimetype"] = guess_type(fd["name"])[0]
    fd_content = BytesIO(content)
    fd["path"] = f'{path_prefix(fd)}/{oldfiledict["url"]}'
    log.info(f"file update {fd}")
    ufd = await DbFile.update(id, fd)
    writeFilecontent(fd["path"], fd_content)
    return encode_file(ufd)


from google.cloud import storage
from google.cloud.storage import Blob
from google.api_core import exceptions


def storage_client():
    if not hasattr(storage_client, "sc"):
        setattr(storage_client, "sc", storage.Client())
    return storage_client.sc


def readFilecontent(path: str) -> bytes:
    """
    read the file from the filestore
    returns bytes object
    """
    settings = get_settings()
    if settings.FILESTORE["manager"] == "google":
        log.info(f"reading {path}")
        client = storage_client()
        bucket = client.bucket(settings.FILESTORE["bucket"])
        blob = Blob(path, bucket)
        try:
            contents = blob.download_as_bytes(client=client)
            return contents
        except exceptions.NotFound:
            log.info(f"File {path} not found in CloudStorage")
            raise RdNotFound()
        except Exception as e:
            log.exception(f"readFileContent failed")
            raise RdInternalServerError()
    if settings.FILESTORE["manager"] == "local":
        basedir = Path(settings.FILESTORE["basedir"])
        with open(basedir / path, "rb") as f:
            return f.read()


def writeFilecontent(path: str, fileobj: IO) -> None:
    """
    wrtite a file like object to the filestore
    """
    log.info("writing file content")
    settings = get_settings()
    if settings.FILESTORE["manager"] == "google":
        client = storage_client()
        bucket = client.bucket(settings.FILESTORE["bucket"])
        log.info(f"Blob write: {path}")
        blob = Blob(path, bucket)
        blob.upload_from_file(fileobj)
    if settings.FILESTORE["manager"] == "local":
        basedir = Path(settings.FILESTORE["basedir"])
        with open(basedir / path, "wb") as f:
            f.write(fileobj.getvalue())
