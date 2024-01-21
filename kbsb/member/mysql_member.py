import logging
import hashlib
import asyncio
from datetime import datetime, timedelta, date
from kbsb.core.db import get_mysql
from reddevil.core import (
    RdNotAuthorized,
    jwt_encode,
    get_settings,
    RdNotFound,
    RdInternalServerError,
)
from kbsb.member.md_member import Member, AnonMember
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


async def mysql_mgmt_getmember(idmember: int) -> Member:
    cnx = get_mysql()
    query = """
        SELECT 
            Dnaiss as birthdate, 
            Decede as deceased, 
            Email as email, 
            Prenom as first_name, 
            Sexe as gender, 
            Club as idclub, 
            Matricule as idnumber, 
            Nom as last_name, 
            G as licence_g, 
            Locked as locked, 
            GSM as mobile, 
            AnneeAffilie as year_affiliation
        FROM signaletique 
        WHERE Matricule = %(idmember)s
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, {"idmember": idmember})
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


def get_elotable() -> str:
    today = date.today()
    elomonth = (today.month - 1) // 3 * 3 + 1
    return f"p_player{today.year}{elomonth:02d}"


async def mysql_anon_getclubmembers(idclub: int, active: bool):
    cnx = get_mysql()
    qactive = " AND signaletique.AnneeAffilie = 2024 " if active else ""
    query = """
        SELECT 
            signaletique.Matricule as idnumber,
            signaletique.Club as idclub,
            signaletique.Nom as last_name,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            {elotable}.Elo as natrating,
            fide.ELO as fiderating
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


async def mysql_anon_getmember(idnumber: int) -> AnonMember:
    cnx = get_mysql()
    query = """
        SELECT
            signaletique.Matricule as idnumber,
            signaletique.Club as idclub,
            signaletique.Nom as last_name,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            {elotable}.Elo as natrating,
            fide.Elo as fiderating

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
    logger.info("member", member)
    await asyncio.sleep(0)
    return AnonMember(**member)


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


async def mysql_anon_getfidemember(idnumber: int) -> AnonMember:
    logger.info(f"getfide {idnumber}")
    cnx = get_mysql()
    query = """
        SELECT
            Name as fullname,
            Elo as fiderating,
            Sex as gender,
            Birthday as birthday
        FROM fide
        WHERE ID_number = %(idnumber)s
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, {"idnumber": idnumber})
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
    return AnonMember(
        **{
            "idclub": 0,
            "idnumber": 0,
            "idfide": idnumber,
            "first_name": nparts[0],
            "last_name": nparts[1],
            "natrating": 0,
            "fiderating": member["fiderating"],
            "gender": member["gender"],
        }
    )
