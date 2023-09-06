# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022


# all models in the service level exposed to the API
# we are using pydantic as tool

from datetime import datetime
from typing import Dict, Any, List, Optional
from xml.dom.expatbuilder import DOCUMENT_NODE
from pydantic import BaseModel
from typing import Literal
from reddevil.core.dbbase import DbBase

# DB classes


class DbICSeries(DbBase):
    COLLECTION = "interclub2324series"
    DOCUMENTTYPE = "InterclubSeries"
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICVenue(DbBase):
    COLLECTION = "interclub2324venues"
    DOCUMENTTYPE = "InterclubVenues"
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


class DbICClub(DbBase):
    COLLECTION = "interclub2324club"
    DOCUMENTTYPE = "ICClub"
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


class DbICEnrollment(DbBase):
    COLLECTION = "interclub2324enrollment"
    DOCUMENTTYPE = "InterclubEnrollment"
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


# interclubclub


class ICTeam(BaseModel):
    division: int
    titular: List[int]
    idclub: int
    index: str
    name: str  # includes number like "KOSK 1"
    pairingnumber: int
    playersplayed: List[int]


class ICTransfer(BaseModel):
    """
    players which are playing for another club
    """

    orig_confirmedate: datetime | None = None
    visit_confirmdate: datetime | None = None
    request_date: Optional[datetime]


class ICPlayer(BaseModel):
    """
    a Player on player list of a club
    """

    assignedrating: int
    fiderating: int
    first_name: str
    idnumber: int
    idcluborig: int  # the club the player belongs to in signaletique
    idclubvist: int  # the club the player is playing if he plays elsewhere
    last_name: str
    natrating: int
    nature: Literal[
        "assigned",
        "unassigned",
        "requestedout",
        "requestedin",
        "comfirmedin",
        "confirmedout",
        "locked",
    ]
    transfer: ICTransfer | None = None


class ICClub(BaseModel):
    name: str
    id: str | None
    idclub: int
    teams: List[ICTeam]
    players: List[ICPlayer]
    enrolled: bool


class ICClubIn(BaseModel):
    name: str
    teams: List[ICTeam]
    players: List[ICPlayer]


# series


class ICSeries(BaseModel):
    """
    representation of a single series
    """

    division: int
    index: str
    teams: List[ICTeam]


class ICCompetition(BaseModel):
    season: str
    allseries: List[ICSeries]


# enrollment


class ICEnrollment(BaseModel):
    id: Optional[str]
    idclub: Optional[int]
    idinvoice: Optional[str]
    idpaymentrequest: Optional[str]
    locale: Optional[str]
    name: Optional[str]
    teams1: Optional[int]
    teams2: Optional[int]
    teams3: Optional[int]
    teams4: Optional[int]
    teams5: Optional[int]
    wishes: Optional[Dict]


class ICEnrollmentHistory(BaseModel):
    action: str
    label: str
    idclub: str
    time: datetime


class ICEnrollmentList(BaseModel):
    enrollments: List[ICEnrollment]


# enrollment validators


class ICEnrollmentIn(BaseModel):
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int
    wishes: dict
    name: str


# venues


class ICVenue(BaseModel):
    address: str
    email: str | None
    phone: str | None
    capacity: int  # number of boards, 0  is unlimited
    notavailable: List[str]


class ICVenuesIn(BaseModel):
    venues: List[ICVenue]


class ICVenues(BaseModel):
    id: Optional[str]
    idclub: Optional[int]
    venues: List[ICVenue]


class ICVenuesList(BaseModel):
    clubvenues: List[Any]
