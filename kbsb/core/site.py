# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2019

import logging
import yaml
import os
import csv
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from reddevil.service.secrets import get_secret
from kbsb.main import settings

log = logging.getLogger(__name__)
cwd = Path(".")


def get_drive_service():
    """
    get Google drive service with delegated credentials of me myself and I
    this is dangerous, needs imrpovement
    """
    if not hasattr(get_drive_service, "service"):
        secret = get_secret("gdrive")
        cr = service_account.Credentials.from_service_account_info(
            secret, scopes=["https://www.googleapis.com/auth/drive"]
        )
        delegated_credentials = cr.with_subject("ruben.decrop@frbe-kbsb-ksb.be")
        setattr(
            get_drive_service,
            "service",
            build("drive", "v3", credentials=delegated_credentials),
        )
    return get_drive_service.service


async def fetchI18n() -> None:
    """
    fetch the translations file from google drive and create the frontend languages files
    """
    request = (
        get_drive_service()
        .files()
        .export_media(fileId=settings.GOOGLEDRIVE_TRANSLATIONID, mimeType="text/csv")
    )
    with (cwd / "share" / "data" / "i18n.csv").open("wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    with (cwd / "share" / "data" / "i18n.csv").open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        allrows = []
        for r in reader:
            allrows.append(r)
    for l in ["en", "fr", "nl", "de"]:
        with (cwd / "frontend" / "lang" / f"{l}.js").open("w", encoding="utf8") as f:
            f.write("export default {\n")
            for r in allrows:
                f.write(f'"{r["key"]}": `{r[l]}`,\n')
            f.write("}\n")
    log.info('i18n files written')
