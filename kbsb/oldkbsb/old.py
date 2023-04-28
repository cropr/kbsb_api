# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

import logging
import hashlib
import asyncio
from jose import JWTError, ExpiredSignatureError
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timedelta, date
from sqlalchemy.orm import sessionmaker
from typing import cast, Any, IO, Union

from reddevil.core import (
    RdNotAuthorized,
    RdNotFound,
    RdBadRequest,
    RdInternalServerError,
    get_settings,
    jwt_encode,
    jwt_getunverifiedpayload,
    jwt_verify,
)
from kbsb.oldkbsb import (
    OldLoginValidator,
    OldMember,
    OldMember_sql,
    OldMemberList,
    OldUser,
    OldUser_sql,
    OldNatRating_sql,
    OldNatRating,
    OldFideRating_sql,
    OldFideRating,
    ActiveMember,
    ActiveMemberList,
)

from kbsb.core.db import mysql_engine

logger = logging.getLogger(__name__)
# we simplify the normal jwt libs by setting the SALT fixed
SALT = "OLDSITE"


def old_login(ol: OldLoginValidator) -> str:
    """
    use the mysql database to mimic the old php login procedure
    return a JWT token
    """
    settings = get_settings()
    session = sessionmaker(mysql_engine())()
    query = session.query(OldUser_sql).filter_by(user=ol.idnumber)
    users = query.all()
    if not users:
        logger.info(f"not authorized: idnumber {ol.idnumber} not found")
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    hash = f"Le guide complet de PHP 5 par Francois-Xavier Bois{ol.password}"
    pwcheck = hashlib.md5(hash.encode("utf-8")).hexdigest()
    for user in users:
        if user.password == pwcheck:
            payload = {
                "sub": str(ol.idnumber),
                "exp": datetime.utcnow() + timedelta(minutes=settings.TOKEN["timeout"]),
            }
            return jwt_encode(payload, SALT)
    logger.info(f"not authorized: password hash {pwcheck} not correct")
    raise RdNotAuthorized(description="WrongUsernamePasswordCombination")


def validate_oldtoken(auth: HTTPAuthorizationCredentials) -> int:
    """
    checks a JWT token for validity
    return an idnumber if the token is correctly validated
    if token is not valid the function :
        - either returns None
        - either raise RdNotAuthorized if raising is set
    """
    settings = get_settings()
    token = auth.credentials if auth else None
    if not token:
        raise RdNotAuthorized(description="MissingToken")
    if settings.TOKEN.get("nocheck"):
        return 0
    try:
        payload = jwt_getunverifiedpayload(token)
    except JWTError:
        raise RdNotAuthorized(description="BadToken")
    username = payload.get("sub")
    try:
        jwt_verify(token, settings.JWT_SECRET + SALT)
    except ExpiredSignatureError as e:
        logger.debug(f"expired {e}")
        raise RdNotAuthorized(description="TokenExpired")
    except JWTError as e:
        logger.debug(f"jwt error {e}")
        raise RdNotAuthorized(description="BadToken")
    return username


def get_member(idbel: Union[str, int]) -> OldMember:
    settings = get_settings()
    session = sessionmaker(mysql_engine())()
    try:
        nidbel = int(idbel)
    except Exception:
        raise RdBadRequest(description="idbelNotInteger")
    member = session.query(OldMember_sql).filter_by(idnumber=idbel).one_or_none()
    if not member:
        raise RdNotFound(description="MemberNotFound")
    return OldMember.from_orm(member)


def get_clubmembers(idclub: int, active: bool = True) -> ActiveMemberList:
    """
    find in the signaletique all members of a club
    """
    session = sessionmaker(mysql_engine())()
    members = session.query(OldMember_sql).filter_by(
        idclub=idclub,
    )
    am = []
    for m in members:
        om = OldMember.from_orm(m)
        if om.deceased or om.licence_g or om.year_affiliation != 2023:
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
    return ActiveMemberList(activemembers=am)


def get_member(idbel: int) -> ActiveMember:
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
    om = OldMember.from_orm(member)
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
    return ActiveMember(
        idnumber=idbel,
        idclub=om.idclub,
        first_name=om.first_name,
        last_name=om.last_name,
        natrating=natrating,
        fiderating=fiderating,
    )
