# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022


# all models in the service level exposed to the API
# we are using pydantic as tool

from datetime import datetime
from typing import Dict, Any, List, Optional
from xml.dom.expatbuilder import DOCUMENT_NODE
from pydantic import BaseModel


# interclubclub


class ICTeam(BaseModel):
    division: int
    titular: List[int]
    idclub: int
    index: str
    name: str  # includes number like "KOSK 1"
    pairingnumber: int
    playersplayed: List[int]


class ICPlayer(BaseModel):
    """
    Player on player list of a club
    """

    assignedrating: int
    fiderating: int
    first_name: str
    idnumber: int
    idclub: int
    last_name: str
    natrating: int
    transfer_confirmed: Optional[bool] = None
    transfer: bool = False


class ICTransfer(BaseModel):
    """
    players which are playing for another club
    """

    orig_confirmedate: Optional[datetime]
    visit_confirmdate: Optional[datetime]
    first_name: str
    idnumber: int
    orig_idclub: int
    visit_idclub: int
    last_name: str
    request_date: Optional[datetime]


class ICClub(BaseModel):
    name: str
    id: Optional[str]
    idclub: int
    teams: List[ICTeam]
    players: List[ICPlayer]
    transfersout: List[ICTransfer]


class ICClubIn(BaseModel):
    name: Optional[str]
    teams: Optional[List[ICTeam]]
    players: Optional[List[ICPlayer]]
    transfersout: Optional[List[ICTransfer]]


class TransferRequestValidator(BaseModel):
    members: List[int]
    idoriginalclub: int
    idvisitingclub: int


# series


class ICSeries(BaseModel):
    """
    representation of a single series
    """

    division: int
    index: str
    teams: List[ICTeam]


class ICSeriesList(BaseModel):
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