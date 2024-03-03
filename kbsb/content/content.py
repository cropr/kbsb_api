# copyright Ruben Decrop 2012 - 2022

import logging
import io
from typing import cast, List, Dict, Any
from datetime import datetime
import frontmatter
from google.cloud import storage
from google.cloud.storage import Blob
from google.api_core import exceptions
from functools import lru_cache

from reddevil.core import (
    RdInternalServerError,
    RdNotFound,
    get_settings,
)
from .md_content import Article

logger = logging.getLogger(__name__)


def storage_client():
    if not hasattr(storage_client, "sc"):
        setattr(storage_client, "sc", storage.Client())
    return storage_client.sc


def get_articles() -> List[Article]:
    """
    read the file from the filestore
    returns bytes object
    """
    settings = get_settings()
    client = storage_client()
    articles = []
    try:
        blobs = client.list_blobs(settings.FILESTORE["bucket"], prefix="articles")
        for b in blobs:
            slug = b.name.split("/")[-1].split(".")[0]
            art = get_article(slug)
            articles.append(art)
    except Exception as e:
        logger.exception(f"get articles failed")
    return articles


@lru_cache(maxsize=30)
def get_article(slug: str) -> Article:
    """
    read the file from the filestore
    returns bytes object
    """
    settings = get_settings()
    client = storage_client()
    uri = f'gs://{settings.FILESTORE["bucket"]}/articles/{slug}.md'
    fdc = io.BytesIO()
    try:
        client.download_blob_to_file(uri, fdc)
        fdc.seek(0)
        contdict = frontmatter.loads(fdc.read().decode("utf-8"))
    except exceptions.NotFound:
        logger.info(f"File {uri} not found in CloudStorage")
        raise RdNotFound()
    except Exception as e:
        logger.exception(f"get article failed")
        raise RdInternalServerError()
    return Article(**contdict, slug=slug)
