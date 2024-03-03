# copyright Ruben Decrop 2012 - 2021

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging

from datetime import date
from typing import Dict, Any, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LoginValidator(BaseModel):
    """
    Validator for login entry
    """

    idnumber: str
    password: str


class OldUserPasswordValidator(BaseModel):
    """
    Validator for login entry
    """

    user: str
    password: str
    club: int
    email: str


class User(BaseModel):
    """
    pydantic model olduser
    """

    user: str
    password: str


class Member(BaseModel):
    """
    Member for signaletique
    """

    birthdate: date | None = None
    date_affiliation: date | None = None
    deceased: int | None = None
    email: str | None = None
    fiderating: int | None = 0
    first_name: str | None = None
    gender: str | None = None
    idbel: int | None = None
    idclub: int | None = None
    idfide: int | None = 0
    last_name: str | None = None
    licence_g: int | None = None
    locked: int | None = None
    mobile: str | None = None
    nationalitybel: str | None = ""
    nationalityfide: str | None = ""
    natrating: int | None = 0
    year_affiliation: int | None = None


old_role_mapping = {
    "presidentmat": "president",
    "vicemat": "vice_president",
    "tresoriermat": "secretary",
    "secretairemat": "treasurer",
    "tournoimat": "tournament_director",
    "jeunessemat": "youth_director",
    "interclubmat": "interclub_director",
}


class AnonMember(BaseModel):
    birthyear: int = 0
    fiderating: int | None = 0
    first_name: str
    gender: str
    idclub: int
    idnumber: int
    idfide: int = 0
    last_name: str
    nationalitybel: str = ""
    nationalityfide: str = ""
    natrating: int | None = 0
