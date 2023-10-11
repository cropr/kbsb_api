# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

# models for Fielstore cpmpatible with statamic blueprint

from datetime import date
from pydantic import BaseModel


class Article(BaseModel):
    id: str
    blueprint: str
    title: str
    active_days: int
    active_since: date
    title_nl: str | None = None
    intro_nl: str | None = None
    text_nl: str | None = None
    title_fr: str | None = None
    intro_fr: str | None = None
    slug: str
    text_fr: str | None = None
    text_de: str | None = None
    text_en: str | None = None
    updated_by: str
    updated_at: int
