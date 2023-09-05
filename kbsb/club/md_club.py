# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union, Set
from pydantic import BaseModel
from enum import Enum
from reddevil.core import DbBase


class Visibility(str, Enum):
    hidden = "HIDDEN"  # only by member itself and by KBSB baord
    club = "CLUB"  # hidden + club members can view
    public = "PUBLIC"  # open to everyone


class Federation(str, Enum):
    v = "V"
    f = "F"
    d = "D"


class ClubRoleNature(str, Enum):
    ClubAdmin = "ClubAdmin"
    InterclubAdmin = "InterclubAdmin"
    InterclubCaptain = "InterclubCaptain"


class Day(str, Enum):
    monday = "Monday"
    tuesday = "Tuesday"
    wednesday = "Wednesday"
    thursday = "Thursday"
    friday = "Friday"
    saturday = "Saturday"
    sunday = "Sunday"


class ClubMember(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    email_visibility: Visibility | None = None
    idnumber: int
    mobile: str | None = None
    mobile_visibility: Visibility | None = None


class ClubRole(BaseModel):
    nature: ClubRoleNature
    memberlist: List[int]  # list of id numbers that have the role


class Club(BaseModel):
    """
    basic club used in service layer
    """

    address: Optional[str] = ""  # full contact address
    bankaccount_name: Optional[str]
    bankaccount_iban: Optional[str]
    bankaccount_bic: Optional[str]
    boardmembers: Optional[Dict[str, ClubMember]]
    clubroles: Optional[List[ClubRole]]
    email_admin: Optional[str]  # email address for administrative tasks
    email_finance: Optional[str]  # email address for financial tasks
    email_interclub: Optional[str]  # email_fdor interclub tasks
    email_main: Optional[str]  # main email address to contact, must be available
    enabled: Optional[bool]
    federation: Optional[Federation]
    idclub: Optional[int]
    id: Optional[str]
    name_long: Optional[str]  # long name without abbrevioations
    name_short: Optional[str]  # short name with abbreviations
    openinghours: Optional[Dict[Day, str]]
    venue: Optional[str] = ""  # full multiline address of playing venue
    website: Optional[str]


class ClubHistory(BaseModel):
    action: str
    label: str
    idclub: str
    time: datetime


class ClubIn(BaseModel):
    """
    Validator for inserting a club
    """

    address: Optional[str]  # full contact address
    bankaccount_name: Optional[str]
    bankaccount_iban: Optional[str]
    bankaccount_bic: Optional[str]
    boardmembers: Optional[Dict[str, ClubMember]]
    clubroles: Optional[List[ClubRole]]
    email_admin: Optional[str]  # email address for administrative tasks
    email_finance: Optional[str]  # email address for financial tasks
    email_interclub: Optional[str]  # email_fdor interclub tasks
    email_main: Optional[str]  # main email address to contact, must be available
    enabled: Optional[bool]
    federation: Federation
    idclub: int
    name_long: str  # long name without abbrevioations
    name_short: str  # short name with abbreviations
    openinghours: Optional[Dict[Day, str]]
    venue: Optional[str]  # full multiline address of playing venue
    website: Optional[str]


class ClubUpdate(BaseModel):
    """
    Validator for updating a club
    """

    address: str | None = None  # full contact address
    bankaccount_name: str | None = None
    bankaccount_iban: str | None = None
    bankaccount_bic: str | None = None
    boardmembers: Dict[str, ClubMember] | None = None
    clubroles: List[ClubRole] | None = None
    email_admin: str | None = None
    email_finance: str | None = None
    email_interclub: str | None = None
    email_main: str | None = None
    federation: Federation | None = None
    name_long: str | None = None
    name_short: str | None = None
    openinghours: Dict[Day, str] | None = None
    venue: str | None = None
    website: str | None = None


class ClubItem(BaseModel):
    email_main: Optional[str]
    enabled: bool
    idclub: int
    id: str
    name_long: str
    name_short: str


class ClubAnon(BaseModel):
    address: Optional[str] = ""
    boardmembers: Optional[Dict[str, ClubMember]]
    email_main: Optional[str]
    email_admin: Optional[str]
    email_finance: Optional[str]
    email_interclub: Optional[str]
    enabled: bool
    idclub: int
    id: str
    name_long: str
    name_short: str
    venue: Optional[str] = ""
    website: Optional[str]


class DbClub(DbBase):
    COLLECTION = "club"
    DOCUMENTTYPE = "Club"
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True
