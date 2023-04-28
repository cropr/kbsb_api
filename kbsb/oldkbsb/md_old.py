# copyright Ruben Decrop 2012 - 2021

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import declarative_base
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel
from kbsb.core.db import get_mysql

logger = logging.getLogger(__name__)

Base = declarative_base()


class OldLoginValidator(BaseModel):
    """
    Validator for login entry
    """

    idnumber: int
    password: str


class OldUser_sql(Base):
    """
    table p_user in mysql
    we only encode the fields we need
    """

    __tablename__ = "p_user"

    user = Column("user", String, primary_key=True)
    password = Column("password", String)


class OldUser(BaseModel):
    """
    pydantic model olduser
    """

    user: str
    password: str

    class Config:
        orm_mode = True


class OldMember_sql(Base):
    """
    table signaletique in mysql
    we only encode the fields we need
    """

    __tablename__ = "signaletique"

    birthdate = Column("Dnaiss", Date)
    deceased = Column("Decede", Integer)
    email = Column("Email", String(48))
    first_name = Column("Prenom", String)
    gender = Column("Sexe", String)
    idclub = Column("Club", Integer, index=True)
    idnumber = Column("Matricule", Integer, primary_key=True)
    last_name = Column("Nom", String)
    licence_g = Column("G", Integer)
    locked = Column("Locked", Integer)
    mobile = Column("Gsm", String)
    year_affiliation = Column("AnneeAffilie", Integer, index=True)


class OldMember(BaseModel):
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

    class Config:
        orm_mode = True


class OldMemberList(BaseModel):
    members: List[OldMember]


class OldClub_sql(Base):
    __tablename__ = "p_clubs"

    club = Column("Club", Integer, primary_key=True)
    federation = Column("Federation", String(collation="latin1_general_cs"))
    ligue = Column("Ligue", Integer)
    intitule = Column("Intitule", String(collation="latin1_general_cs"))
    abbrev = Column("Abbrev", String(collation="latin1_general_cs"))
    local = Column("Local", String(collation="latin1_general_cs"))
    adresse = Column("Adresse", String(collation="latin1_general_cs"))
    codepostal = Column("CodePostal", String(collation="latin1_general_cs"))
    localite = Column("Localite", String(collation="latin1_general_cs"))
    telephone = Column("Telephone", String(collation="latin1_general_cs"))
    siegesocial = Column("SiegeSocial", String(collation="latin1_general_cs"))
    joursdejeux = Column("JoursDeJeux", String(collation="latin1_general_cs"))
    website = Column("WebSite", String(collation="latin1_general_cs"))
    webmaster = Column("WebMaster", String(collation="latin1_general_cs"))
    forum = Column("Forum", String(collation="latin1_general_cs"))
    email = Column("Email", String(collation="latin1_general_cs"))
    mandataire = Column("Mandataire", Integer)
    mandataire = Column("MandataireNr", Integer)
    presidentmat = Column("PresidentMat", Integer)
    vicemat = Column("ViceMat", Integer)
    tresoriermat = Column("TresorierMat", Integer)
    secretairemat = Column("SecretaireMat", Integer)
    tournoimat = Column("TournoiMat", Integer)
    jeunessemat = Column("JeunesseMat", Integer)
    interclubmat = Column("InterclubMat", Integer)
    bquetitulaire = Column("BqueTitulaire", String(collation="latin1_general_cs"))
    bquecompter = Column("BqueCompte", String(collation="latin1_general_cs"))
    bquebic = Column("BqueBIC", String(collation="latin1_general_cs"))
    divers = Column("Divers", String(collation="latin1_general_cs"))


old_role_mapping = {
    "presidentmat": "president",
    "vicemat": "vice_president",
    "tresoriermat": "secretary",
    "secretairemat": "treasurer",
    "tournoimat": "tournament_director",
    "jeunessemat": "youth_director",
    "interclubmat": "interclub_director",
}


class OldNatRating_sql(Base):
    __tablename__ = "p_player202207"

    idnumber = Column("Matricule", Integer, primary_key=True)
    idfide = Column("Fide", Integer)
    natrating = Column("Elo", Integer)
    nationality = Column("Nat", String)


class OldNatRating(BaseModel):

    idnumber: int
    idfide: Optional[int]
    natrating: int = 0
    nationality: str

    class Config:
        orm_mode = True


class OldFideRating_sql(Base):
    __tablename__ = "fide"

    idfide = Column("ID_NUMBER", Integer, primary_key=True)
    fiderating = Column("ELO", Integer)


class OldFideRating(BaseModel):

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
