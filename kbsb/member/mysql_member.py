import logging
import hashlib
import asyncio
from datetime import datetime, timedelta, date
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from kbsb.core.db import mysql_engine
from reddevil.core import RdNotAuthorized, jwt_encode, get_settings, RdNotFound
from kbsb.member.md_member import Member


logger = logging.getLogger(__name__)
Base = declarative_base()

# we simplify the normal jwt libs by setting the SALT fixed
SALT = "OLDSITE"


class User_sql(Base):
    """
    table p_user in mysql
    we only encode the fields we need
    """

    __tablename__ = "p_user"

    user = Column("user", String, primary_key=True)
    password = Column("password", String)


async def mysql_query_password(idnumber: int, password: str):
    settings = get_settings()
    session = sessionmaker(mysql_engine())()
    query = session.query(User_sql).filter_by(user=idnumber)
    users = query.all()
    if not users:
        logger.info(f"not authorized: idnumber {idnumber} not found")
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    hash = f"Le guide complet de PHP 5 par Francois-Xavier Bois{ol.password}"
    pwcheck = hashlib.md5(hash.encode("utf-8")).hexdigest()
    for user in users:
        if user.password == pwcheck:
            payload = {
                "sub": str(idnumber),
                "exp": datetime.utcnow() + timedelta(minutes=settings.TOKEN["timeout"]),
            }
            await asyncio.sleep(0)
            return jwt_encode(payload, SALT)
    logger.info(f"not authorized: password hash {pwcheck} not correct")
    raise RdNotAuthorized(description="WrongUsernamePasswordCombination")


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


async def mysql_getmember(idmmeber: int):
    session = sessionmaker(mysql_engine())()
    member = session.query(OldMember_sql).filter_by(idnumber=idmmeber).one_or_none()
    if not member:
        raise RdNotFound(description="MemberNotFound")
    await asyncio.sleep(0)
    return Member.from_orm(member)


class OldNatRating_sql(Base):
    __tablename__ = "p_player202307"

    idnumber = Column("Matricule", Integer, primary_key=True)
    idfide = Column("Fide", Integer)
    natrating = Column("Elo", Integer)
    nationality = Column("Nat", String)


class OldFideRating_sql(Base):
    __tablename__ = "fide"

    idfide = Column("ID_NUMBER", Integer, primary_key=True)
    fiderating = Column("ELO", Integer)


async def mysql_getclubmembers(idclub: int):
    session = sessionmaker(mysql_engine())()
    members = session.query(OldMember_sql).filter_by(
        idclub=idclub,
    )
    am = []
    for m in members:
        om = Member.from_orm(m)
        if not om.year_affiliation:
            continue
        if om.deceased or om.licence_g or om.year_affiliation < 2023:
            continue
        onr = (
            session.query(OldNatRating_sql)
            .filter_by(idnumber=om.idnumber)
            .one_or_none()
        )
        natrating = 0
        fiderating = 0
        if onr:
            natrating = onr.natrating
            if onr.idfide and onr.idfide > 0:
                ofr = (
                    session.query(OldFideRating_sql)
                    .filter_by(idfide=onr.idfide)
                    .one_or_none()
                )
                if ofr:
                    fiderating = ofr.fiderating
        am.append(
            ActiveMember(
                idnumber=om.idnumber,
                idclub=om.idclub,
                first_name=om.first_name,
                last_name=om.last_name,
                natrating=natrating,
                fiderating=fiderating,
            )
        )
    await asyncio.sleep(0)
    return ActiveMemberList(activemembers=am)


async def mysql_getactivemember(idmember: int):
    settings = get_settings()
    session = sessionmaker(mysql_engine())()
    member = (
        session.query(OldMember_sql)
        .filter_by(
            idnumber=idbel,
        )
        .one_or_none()
    )
    if not member:
        raise RdNotFound(description="MemberNotFound")
    if member.deceased or member.licence_g or member.year_affiliation != 2023:
        raise RdBadRequest(description="MemberNotActive")
    om = Member.from_orm(member)
    onr = session.query(OldNatRating_sql).filter_by(idnumber=idbel).one_or_none()
    natrating = 0
    fiderating = 0
    if onr:
        natrating = onr.natrating
        if onr.idfide and onr.idfide > 0:
            ofr = (
                session.query(OldFideRating_sql)
                .filter_by(idfide=onr.idfide)
                .one_or_none()
            )
            if ofr:
                fiderating = ofr.fiderating
    await asyncio.sleep(0)
    return ActiveMember(
        idnumber=idbel,
        idclub=om.idclub,
        first_name=om.first_name,
        last_name=om.last_name,
        natrating=natrating,
        fiderating=fiderating,
    )
