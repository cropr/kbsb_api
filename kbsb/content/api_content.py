import logging

logger = logging.getLogger(__name__)

from fastapi import HTTPException, Depends, APIRouter
from fastapi.security import HTTPAuthorizationCredentials
from reddevil.core import RdException, bearer_schema, validate_token
from typing import List, Any

from kbsb.member import validate_membertoken
from .md_content import Article
from .content import get_article, get_articles


router = APIRouter(prefix="/api/v1/content")

# emrollments


@router.get(
    "/anon/article",
    response_model=List[Article],
)
def api_get_articles():
    """
    get all articles
    """
    try:
        return get_articles()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_articles")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/anon/article/{slug}",
    response_model=Article | None,
)
def api_get_article(slug: str):
    """
    get an article by slug
    """
    try:
        return get_article(slug)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except:
        logger.exception("failed api call get_article")
        raise HTTPException(status_code=500, detail="Internal Server Error")
