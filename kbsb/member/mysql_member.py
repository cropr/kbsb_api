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


async def mysql_anon_getclubmembers(idclub: int, active: bool):
    cnx = get_mysql()
    qactive = " AND signaletique.AnneeAffilie = 2024 " if active else ""
    query = f"""
        SELECT 
            signaletique.Matricule as idnumber,
            signaletique.Club as idclub,
            signaletique.Nom as last_name,
            signaletique.Prenom as first_name,
            signaletique.Sexe as gender,
            p_player202307.Elo as natrating,
            fide.ELO as fiderating

        FROM signaletique 

        LEFT JOIN p_player202307 ON  signaletique.Matricule =  p_player202307.Matricule
        LEFT JOIN fide ON p_player202307.Fide =  fide.ID_NUMBER        
        
        WHERE signaletique.Club = %(idclub)s {qactive}
    """
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, {"idclub": idclub})
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
            p_player202307.Elo as natrating,
            fide.ELO as fiderating

        FROM signaletique 

        INNER JOIN p_player202307 ON  signaletique.Matricule =  p_player202307.Matricule
        LEFT JOIN fide ON p_player202307.Fide =  fide.ID_NUMBER           

        WHERE signaletique.Matricule = %(idnumber)s
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
    return AnonMember(**member)

def old_userpassword(oup: OldUserPasswordValidator) -> None:
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
            cursor.execute("""
                UPDATE p_user SET password = %s, email = %s, club = %s
                WHERE user = %s
            """, (pwhashed, oup.email, oup.club, oup.user))
        else:
            logger.info("inserting user with password")
            cursor.execute("""
                INSERT INTO p_user (password, email, club, user)
                VALUES (%s,%s,%s,%s)
            """, (pwhashed, oup.email, oup.club, oup.user))
        cursor.close()
    finally:
        cnx.close()    
