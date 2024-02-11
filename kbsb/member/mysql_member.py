import logging
import hashlib
import asyncio
from datetime import datetime, timedelta, date
from typing import List
from kbsb.core.db import get_mysql
from reddevil.core import (
    RdNotAuthorized,
    jwt_encode,
    get_settings,
    RdNotFound,
    RdInternalServerError,
)
from kbsb.member.md_member import Member, AnonMember, OldUserPasswordValidator
from kbsb.member import SALT


logger = logging.getLogger(__name__)


async def mysql_login(idnumber: str, password: str):
    logger.info(f"mysqllogin {idnumber} ")
    settings = get_settings()
    cnx = get_mysql()
    query = """
        SELECT user, password from p_user WHERE user = %(user)s
    """
    logger.info(f"idnumber {idnumber}")
    try:
        cursor = cnx.cursor()
        cursor.execute(query, {"user": idnumber})
        user = cursor.fetchone()
    except Exception as e:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    if not user:
        logger.info(f"user empty: idnumber {idnumber} not found")
        raise RdNotAuthorized(description="WrongUsernamePasswordCombination")
    dbuser, dbpassword = user
    logger.info(f"user found {dbuser} {dbpassword}")
    hash = f"Le guide complet de PHP 5 par Francois-Xavier Bois{password}"
    pwcheck = hashlib.md5(hash.encode("utf-8")).hexdigest()
    if dbpassword == pwcheck:
        payload = {
            "sub": idnumber,
            "exp": datetime.utcnow() + timedelta(minutes=settings.TOKEN["timeout"]),
        }
        await asyncio.sleep(0)
        return jwt_encode(payload, SALT)
    logger.info(f"password hash failed for {idnumber} ")
    raise RdNotAuthorized(description="WrongUsernamePasswordCombination")


def get_elotable() -> str:
    today = date.today()
    elomonth = (today.month - 1) // 3 * 3 + 1
    return f"p_player{today.year}{elomonth:02d}"


def current_affiliation_year() -> int:
    today = date.today()
    year = today.year
    if today.month >= 9:
        year += 1
    return year


async def mysql_mgmt_getmember(idmember: int) -> Member:
    cnx = get_mysql()
    query = """
        SELECT 
            signaletique.Dnaiss as birthdate,
            Decede as deceased, 
            DateAffiliation as date_affiliation,            
            fide.Elo as fiderating,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            signaletique.Matricule as idbel,
            signaletique.Club as idclub,
            {elotable}.Fide as idfide,
            signaletique.Nom as last_name,
            signaletique.G as licence_g, 
            signaletique.Locked as locked, 
            signaletique.GSM as mobile, 
            signaletique.Nationalite as nationalitybel,
            signaletique.NatFIDE as nationalityfide,
            {elotable}.Elo as natrating
        FROM signaletique 
        LEFT JOIN {elotable} ON  signaletique.Matricule = {elotable}.Matricule
        LEFT JOIN fide ON {elotable}.Fide =  fide.ID_NUMBER 
        WHERE signaletique.Matricule = %(idbel)s
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable())
        cursor.execute(qf, {"idbel": idmember})
        member = cursor.fetchone()
    except Exception as e:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    if not member:
        raise RdNotFound(description="MemberNotFound")
    logger.info("member", member)
    await asyncio.sleep(0)
    return Member(**member)


async def mysql_mgmt_getclubmembers(idclub: int, active: bool = True) -> List[Member]:
    cnx = get_mysql()
    qactive = " AND signaletique.AnneeAffilie >= %(year)s " if active else ""
    query = """
        SELECT 
            signaletique.Dnaiss as birthdate,
            Decede as deceased, 
            DateAffiliation as date_affiliation,            
            fide.Elo as fiderating,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            signaletique.Matricule as idbel,
            signaletique.Club as idclub,
            {elotable}.Fide as idfide,
            signaletique.Nom as last_name,
            signaletique.G as licence_g, 
            signaletique.Locked as locked, 
            signaletique.GSM as mobile, 
            signaletique.Nationalite as nationalitybel,
            signaletique.NatFIDE as nationalityfide,
            {elotable}.Elo as natrating
        FROM signaletique 
        LEFT JOIN {elotable} ON  signaletique.Matricule = {elotable}.Matricule
        LEFT JOIN fide ON {elotable}.Fide =  fide.ID_NUMBER
        WHERE signaletique.Club = %(idclub)s {qactive}
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable(), qactive=qactive)
        cursor.execute(
            qf,
            {
                "idclub": idclub,
                "year": current_affiliation_year(),
            },
        )
        members = cursor.fetchall()
    except Exception as e:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    await asyncio.sleep(0)
    return [Member(**member) for member in members]


async def mysql_anon_getmember(idnumber: int) -> AnonMember:
    cnx = get_mysql()
    query = """
        SELECT
            signaletique.Dnaiss as birthdate,
            fide.Elo as fiderating,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            signaletique.Club as idclub,
            {elotable}.Fide as idfide,
            signaletique.Matricule as idnumber,
            signaletique.Nom as last_name,
            signaletique.Nationalite as nationalitybel,
            signaletique.NatFIDE as nationalityfide,
            {elotable}.Elo as natrating
        FROM signaletique
        INNER JOIN {elotable} ON  signaletique.Matricule = {elotable}.Matricule
        LEFT JOIN fide on {elotable}.Fide = fide.ID_NUMBER
        WHERE signaletique.Matricule = %(idnumber)s
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable())
        cursor.execute(qf, {"idnumber": idnumber})
        member = cursor.fetchone()
    except Exception as e:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    if not member:
        raise RdNotFound(description="MemberNotFound")
    logger.info(f"member {member}")
    await asyncio.sleep(0)
    am = AnonMember(**member)
    am.birthyear = member["birthdate"].year
    return am


async def mysql_anon_getclubmembers(idclub: int, active: bool = True):
    cnx = get_mysql()
    qactive = " AND signaletique.AnneeAffilie >= %(year)s " if active else ""
    query = """
        SELECT 
            signaletique.Dnaiss as birthdate,
            fide.Elo as fiderating,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            signaletique.Club as idclub,
            {elotable}.Fide as idfide,
            signaletique.Matricule as idnumber,
            signaletique.Nom as last_name,
            signaletique.Nationalite as nationalitybel,
            signaletique.NatFIDE as nationalityfide,
            {elotable}.Elo as natrating
        FROM signaletique 
        LEFT JOIN {elotable} ON  signaletique.Matricule = {elotable}.Matricule
        LEFT JOIN fide ON {elotable}.Fide =  fide.ID_NUMBER
        WHERE signaletique.Club = %(idclub)s {qactive}
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable(), qactive=qactive)
        cursor.execute(
            qf,
            {
                "idclub": idclub,
                "year": current_affiliation_year(),
            },
        )
        members = cursor.fetchall()
    except Exception as e:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    await asyncio.sleep(0)
    return [AnonMember(**member) for member in members]


async def mysql_anon_getfidemember(idfide: int) -> AnonMember:
    logger.info(f"getfide {idfide}")
    cnx = get_mysql()
    query = """
        SELECT
            Name as fullname,
            Elo as fiderating,
            Country as nationalityfide,            
            Sex as gender,
            Birthday as birthday
        FROM fide
        WHERE ID_number = %(idnumber)s
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, {"idnumber": idfide})
        member = cursor.fetchone()
    except Exception as e:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    if not member:
        raise RdNotFound(description="MemberNotFound")
    logger.info("member", member)
    await asyncio.sleep(0)
    nparts = member["fullname"].split(", ")
    am = AnonMember(
        idclub=0,
        idnumber=0,
        idfide=idfide,
        first_name=nparts[1],
        fiderating=member["fiderating"],
        gender=member["gender"],
        last_name=nparts[0],
        natrating=0,
        nationalityfide=member["nationalityfide"],
    )
    am.birthyear = member["birthday"].year
    return am


async def mysql_anon_belid_from_fideid(idfide) -> int:
    cnx = get_mysql()
    query = """
        SELECT Matricule as idbel
        FROM {elotable}
        WHERE Fide = %(idfide)s
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable())
        cursor.execute(qf, {"idfide": idfide})
        m = cursor.fetchone()
    except Exception as e:
        logger.exception("Mysql error")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    if m:
        return m.get("idbel", 0)
    else:
        return 0


async def mysql_old_userpassword(oup: OldUserPasswordValidator) -> None:
    """
    write a new user, or overwrite an existing in the old p_user table
    """
    cnx = get_mysql()
    try:
        cursor = cnx.cursor()
        cursor.execute("SELECT user FROM p_user WHERE user = %s ", (oup.user,))
        found = cursor.fetchone()
        hash = f"Le guide complet de PHP 5 par Francois-Xavier Bois{oup.password}"
        pwhashed = hashlib.md5(hash.encode("utf-8")).hexdigest()
        logger.info(f": password hash {pwhashed} for user {oup.user}")
        if found:
            logger.info("updating user password")
            cursor.execute(
                """
                UPDATE p_user SET password = %s, email = %s, club = %s
                WHERE user = %s
            """,
                (pwhashed, oup.email, oup.club, oup.user),
            )
        else:
            logger.info("inserting user with password")
            cursor.execute(
                """
                INSERT INTO p_user (password, email, club, user)
                VALUES (%s,%s,%s,%s)
            """,
                (pwhashed, oup.email, oup.club, oup.user),
            )
        cursor.close()
    finally:
        cnx.close()
    await asyncio.sleep(0)
