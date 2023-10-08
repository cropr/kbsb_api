# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022


# all models in the service level exposed to the API
# we are using pydantic as tool

from datetime import datetime, date
from typing import Dict, Any, List, Optional
from xml.dom.expatbuilder import DOCUMENT_NODE
from pydantic import BaseModel
from typing import Literal
from reddevil.core.dbbase import DbBase

# interclub club


class ICTeam(BaseModel):
    division: int
    titular: List[int]
    idclub: int
    index: str
    name: str  # includes numbercat like "KOSK 1"
    pairingnumber: int
    playersplayed: List[int]


class ICPlayer(BaseModel):
    """
    a Player on player list of a club
    """

    assignedrating: int
    average: float = 0
    fiderating: int | None = 0
    first_name: str
    idnumber: int
    idcluborig: int  # the club the player belongs to in signaletique
    idclubvisit: int  # the club the player is playing if he plays elsewhere. a transfer
    last_name: str
    natrating: int | None = 0
    nature: Literal[
        "assigned",
        "unassigned",
        "requestedout",
        "requestedin",
        "comfirmedin",
        "confirmedout",
        "locked",
    ]
    titular: str | None = None
    # transfer: ICTransfer | None = None


class ICPlayerUpdate(BaseModel):
    """
    an update of a Player in the playerlist
    """

    assignedrating: int
    fiderating: int | None = 0
    first_name: str
    idnumber: int
    idcluborig: int  # the club the player belongs to in signaletique
    idclubvisit: int  # the club the player is playing if he plays elsewhere
    last_name: str
    natrating: int | None = 0
    nature: Literal[
        "assigned",
        "unassigned",
        "requestedout",
        "requestedin",
        "comfirmedin",
        "confirmedout",
        "locked",
    ]
    titular: str | None = None


class ICPlayerIn(BaseModel):
    players: List[ICPlayerUpdate]


class ICPlayerValidationError(BaseModel):
    errortype: Literal["ELO", "TitularOrder", "TitularCount"]
    idclub: int
    message: str
    detail: Any


class ICClub(BaseModel):
    name: str
    id: str | None
    idclub: int
    teams: List[ICTeam]
    players: List[ICPlayer]
    enrolled: bool


class ICClubOut(BaseModel):
    """
    for a list of ICclubs
    """

    name: str
    idclub: int
    teams: List[ICTeam]
    enrolled: bool


class ICClubIn(BaseModel):
    name: str
    teams: List[ICTeam]
    players: List[ICPlayer]


# series


class ICGame(BaseModel):
    idnumber_home: int | None
    idnumber_visit: int | None
    result: str


class ICGameDetails(BaseModel):
    idnumber_home: int
    fullname_home: str
    rating_home: int
    idnumber_visit: int
    fullname_visit: str
    rating_visit: int
    result: str


class ICEncounter(BaseModel):
    icclub_home: int
    icclub_visit: int
    pairingnr_home: int
    pairingnr_visit: int
    matchpoint_home: int = 0
    matchpoint_visit: int = 0
    boardpoint2_home: int = 0
    boardpoint2_visit: int = 0
    games: List[ICGame] = []
    played: bool = False
    signhome_idnumber: int = 0
    signhome_ts: datetime | None = None
    signvisit_idnumber: int = 0
    signvisit_ts: datetime | None = None


class ICRound(BaseModel):
    round: int
    rdate: str
    encounters: List[ICEncounter]


class ICSeries(BaseModel):
    """
    representation of a single series
    """

    division: int
    index: str
    teams: List[ICTeam]
    rounds: List[ICRound] = []


class ICTeamGame(BaseModel):
    boardpoints2: int = 0  # double boardpoints team won against opponent
    matchpoints: int = 0  # matchpoints team won against opponent
    pairingnumber_opp: int
    round: int


class ICTeamStanding(BaseModel):
    name: str
    idclub: int
    pairingnumber: int
    matchpoints: int
    boardpoints: float
    games: List[ICTeamGame]


class ICStandings(BaseModel):
    """
    representation of a the standings of a single series
    """

    dirtytime: datetime | None = None
    division: int
    id: str | None = None
    index: str
    teams: List[ICTeamStanding]


class ICPlanning(BaseModel):
    """
    a validator for incoming planning
    """

    division: int
    games: List[ICGame]
    idclub: int
    idclub_opponent: int
    index: str
    name: str
    name_opponent: str
    nrgames: int
    pairingnumber: int
    playinghome: bool
    round: int


class ICPlanningIn(BaseModel):
    plannings: List[ICPlanning]


class ICResult(BaseModel):
    """
    a validator for incoming results
    """

    boardpoints: str | None = None
    division: int
    games: List[ICGame]
    icclub_home: int
    icclub_visit: int
    index: str
    name_home: str
    name_visit: str
    nrgames: int
    matchpoints: str | None = None
    round: int
    signhome_idnumber: int | None = 0
    signhome_ts: datetime | None = None
    signvisit_idnumber: int | None = 0
    signvisit_ts: datetime | None = None


class ICResultIn(BaseModel):
    results: List[ICResult]


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
    remarks: str | None = ""
    notavailable: List[str]


class ICVenuesIn(BaseModel):
    venues: List[ICVenue]


class ICVenues(BaseModel):
    id: Optional[str] = None
    idclub: Optional[int]
    venues: List[ICVenue]


playersPerDivision = {
    1: 8,
    2: 8,
    3: 6,
    4: 4,
    5: 4,
}

# DB classes


class DbICSeries(DbBase):
    COLLECTION = "interclub2324series"
    DOCUMENTTYPE = ICSeries
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICStandings(DbBase):
    COLLECTION = "interclub2324standings"
    DOCUMENTTYPE = ICStandings
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICVenue(DbBase):
    COLLECTION = "interclub2324venues"
    DOCUMENTTYPE = ICVenues
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


class DbICClub(DbBase):
    COLLECTION = "interclub2324club"
    DOCUMENTTYPE = ICClub
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


class DbICEnrollment(DbBase):
    COLLECTION = "interclub2324enrollment"
    DOCUMENTTYPE = ICEnrollment
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True
