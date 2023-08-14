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

    idnumber: int
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


class MemberList(BaseModel):
    members: List[Member]


# class OldClub_sql(Base):
#     __tablename__ = "p_clubs"

#     club = Column("Club", Integer, primary_key=True)
#     federation = Column("Federation", String(collation="latin1_general_cs"))
#     ligue = Column("Ligue", Integer)
#     intitule = Column("Intitule", String(collation="latin1_general_cs"))
#     abbrev = Column("Abbrev", String(collation="latin1_general_cs"))
#     local = Column("Local", String(collation="latin1_general_cs"))
#     adresse = Column("Adresse", String(collation="latin1_general_cs"))
#     codepostal = Column("CodePostal", String(collation="latin1_general_cs"))
#     localite = Column("Localite", String(collation="latin1_general_cs"))
#     telephone = Column("Telephone", String(collation="latin1_general_cs"))
#     siegesocial = Column("SiegeSocial", String(collation="latin1_general_cs"))
#     joursdejeux = Column("JoursDeJeux", String(collation="latin1_general_cs"))
#     website = Column("WebSite", String(collation="latin1_general_cs"))
#     webmaster = Column("WebMaster", String(collation="latin1_general_cs"))
#     forum = Column("Forum", String(collation="latin1_general_cs"))
#     email = Column("Email", String(collation="latin1_general_cs"))
#     mandataire = Column("Mandataire", Integer)
#     mandataire = Column("MandataireNr", Integer)
#     presidentmat = Column("PresidentMat", Integer)
#     vicemat = Column("ViceMat", Integer)
#     tresoriermat = Column("TresorierMat", Integer)
#     secretairemat = Column("SecretaireMat", Integer)
#     tournoimat = Column("TournoiMat", Integer)
#     jeunessemat = Column("JeunesseMat", Integer)
#     interclubmat = Column("InterclubMat", Integer)
#     bquetitulaire = Column("BqueTitulaire", String(collation="latin1_general_cs"))
#     bquecompter = Column("BqueCompte", String(collation="latin1_general_cs"))
#     bquebic = Column("BqueBIC", String(collation="latin1_general_cs"))
#     divers = Column("Divers", String(collation="latin1_general_cs"))
#     supdate = Column("SupDate", Date)


old_role_mapping = {
    "presidentmat": "president",
    "vicemat": "vice_president",
    "tresoriermat": "secretary",
    "secretairemat": "treasurer",
    "tournoimat": "tournament_director",
    "jeunessemat": "youth_director",
    "interclubmat": "interclub_director",
}


class NatRating(BaseModel):
    idnumber: int
    idfide: Optional[int]
    natrating: int = 0
    nationality: str

    class Config:
        orm_mode = True


class FideRating(BaseModel):
    idfide: int
    fiderating: int = 0

    class Config:
        orm_mode = True


class ActiveMember(BaseModel):
    idclub: int
    idnumber: int
    first_name: str
    last_name: str
    natrating: int = 0
    fiderating: int = 0


class ActiveMemberList(BaseModel):
    activemembers: List[ActiveMember]
