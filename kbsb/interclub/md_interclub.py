# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022


# all models in the service level exposed to the API
# we are using pydantic as tool

from datetime import datetime
from typing import Dict, Any, List, Optional
from xml.dom.expatbuilder import DOCUMENT_NODE
from pydantic import BaseModel
from reddevil.core import DbBase, DocumentType, ListType

# interclubclub


class InterclubTeam(BaseModel):
    division: int
    titular: List[int]
    idclub: int
    index: str
    name: str  # includes number like "KOSK 1"
    pairingnumber: int
    playersplayed: List[int]


class InterclubPlayer(BaseModel):
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


class InterclubTransfer(BaseModel):
    """
    players which are playing for another club
    """

    confirmed_date: Optional[datetime]
    first_name: str
    idnumber: int
    idoriginalclub: int
    idvisitingclub: int
    last_name: str
    request_date: Optional[datetime]


class InterclubClubOptional(BaseModel):
    name: Optional[str]
    idclub: Optional[int]
    teams: Optional[List[InterclubTeam]]
    players: Optional[List[InterclubPlayer]]
    transfersout: Optional[List[InterclubTransfer]]


class InterclubClub(DocumentType):
    name: str
    id: Optional[str]
    idclub: int
    teams: List[InterclubTeam]
    players: List[InterclubPlayer]
    transfersout: List[InterclubTransfer]


class InterclubClubList(ListType):
    clubs: List[InterclubClub]


class DbInterclubClub(DbBase):
    COLLECTION = "interclubclub"
    DOCUMENTTYPE = "InterclubClub"
    VERSION = 1
    IDGENERATOR = "uuid"
    DT = InterclubClub
    LT = InterclubClubList
    ItemField = "clubs"


class TransferRequestValidator(BaseModel):
    members: List[int]
    idoriginalclub: int
    idvisitingclub: int


# series


class InterclubSeries(DocumentType):
    """
    representation of a single series
    """

    division: int
    index: str
    teams: List[InterclubTeam]


class InterclubSeriesList(ListType):
    allseries: List[InterclubSeries]


class DbInterclubSeries(DbBase):
    COLLECTION = "interclubseries"
    DOCUMENTTYPE = "InterclubSeries"
    VERSION = 1
    IDGENERATOR = "uuid"
    DT = InterclubSeries
    LT = InterclubSeriesList
    ItemField = "allseries"


# enrollment


class InterclubEnrollment(DocumentType):
    id: Optional[str]
    idclub: Optional[int]
    idinvoice: Optional[str]
    idpaymentrequest: Optional[str]
    locale: Optional[str]
    name_long: Optional[str]
    name_short: Optional[str]
    teams1: Optional[int]
    teams2: Optional[int]
    teams3: Optional[int]
    teams4: Optional[int]
    teams5: Optional[int]
    wishes: Optional[Dict]


class InterclubEnrollmentList(ListType):
    enrollments: List[InterclubEnrollment]


class DbInterclubEnrollment(DbBase):
    COLLECTION = "interclubenrollment"
    DOCUMENTTYPE = "InterclubEnrollment"
    VERSION = 1
    IDGENERATOR = "uuid"
    DT = InterclubEnrollment
    LT = InterclubEnrollmentList
    ItemField = "enrollments"


# enrollment validators


class InterclubEnrollmentIn(BaseModel):
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int
    wishes: dict


# venues


class InterclubVenue(BaseModel):
    address: str
    email: str
    phone: str
    capacity: int  # number of boards, 0  is unlimited
    notavailable: List[str]


class InterclubVenuesIn(BaseModel):
    venues: List[InterclubVenue]


class InterclubVenues(BaseModel):
    id: Optional[str]
    idclub: Optional[int]
    name_long: Optional[str]
    name_short: Optional[str]
    venues: List[InterclubVenue]


class InterclubVenuesList(BaseModel):
    clubvenues: List[Any]


class DbInterclubVenues(DbBase):
    COLLECTION = "interclubvenues"
    DOCUMENTTYPE = "InterclubVenues"
    VERSION = 1
    IDGENERATOR = "uuid"


# previous
class InterclubPrevious(BaseModel):
    idclub: int
    name_long: str
    name_short: str
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int
    promotionFrom: Optional[List[int]] = None
    degradationFrom: Optional[List[int]] = None
    stopped: Optional[List[int]] = None


class DbInterclubPrevious(DbBase):
    COLLECTION = "interclubprevious"
    DOCUMENTTYPE = "InterclubPrevious"
    VERSION = 1
    IDGENERATOR = "uuid"
