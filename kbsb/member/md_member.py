# copyright Ruben Decrop 2012 - 2021

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging

from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LoginValidator(BaseModel):
    """
    Validator for login entry
    """

    idnumber: str
    password: str


class User(BaseModel):
    """
    pydantic model olduser
    """

    user: str
    password: str


class Member(BaseModel):
    birthdate: Optional[date]
    deceased: Optional[int]
    email: Optional[str]
    first_name: Optional[str]
    gender: Optional[str]
    idclub: Optional[int]
    idnumber: Optional[int]
    last_name: Optional[str]
    licence_g: Optional[int]
    locked: Optional[int]
    mobile: Optional[str]
    year_affiliation: Optional[int]


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
    idclub: int
    idnumber: int
    first_name: str
    last_name: str
    natrating: int = 0
    fiderating: int | None = 0
    gender: str
