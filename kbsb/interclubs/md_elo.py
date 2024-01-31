from pydantic import BaseModel
from typing import Literal


class EloGame(BaseModel):
    belrating_white: int = 0
    birthday_white: str = ""
    fiderating_white: int = 0
    fullname_white: str = ""
    gender_white: str = ""
    idbel_white: int
    idclub_white: int = 0
    idfide_white: int = 0
    natfide_white: str = "BEL"
    team_white: str = ""
    title_white: str = ""

    belrating_black: int = 0
    birthday_black: str = ""
    fiderating_black: int = 0
    fullname_black: str = ""
    gender_black: str = ""
    idbel_black: int = 0
    idclub_black: int = 0
    idfide_black: int = 0
    natfide_black: str = "BEL"
    team_black: str = ""
    title_black: str = ""

    result: Literal["1-0", "½-½", "0-1", "1-0 FF", "0-1 FF", "0-0 FF"]


class EloPlayer(BaseModel):
    birthday: str
    belrating: int = 0
    color: str
    fullname: str
    fiderating: int = 0
    gender: str
    idbel: int
    idfide: int
    idclub: int = 0
    idopp: int
    myix: int = 0
    natfide: str = "BEL"
    oppix: int = 0
    sc1: float
    sc2: str = ""
    team: str
    title: str
