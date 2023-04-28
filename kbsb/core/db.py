# copyright Ruben Decrop 2012 - 2020
from asyncio.constants import SSL_HANDSHAKE_TIMEOUT
import logging

log = logging.getLogger(__name__)

from datetime import datetime, date
from reddevil.core import get_secret
from fastapi import HTTPException
from sqlalchemy import create_engine
import pymysql, pymysql.cursors


def date2datetime(d: dict, f: str):
    """
    d: document that is used as input to a mongodb operation
    f: fieldname
    converts field f of the document d from date to datetime
    as mongodb only supports the datetime type
    """
    if f in d and isinstance(d[f], date):
        t = datetime.min.time()
        d[f] = datetime.combine(d[f], t)


def get_mongodb():
    """
    a singleton function to get the mongodb database asynchronously
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    from asyncio import get_event_loop

    if not hasattr(get_mongodb, "database"):
        mongoparams = get_secret("mongodb")
        loop = get_event_loop()
        client = AsyncIOMotorClient(mongoparams["url"], io_loop=loop)
        get_mongodb.database = client[mongoparams["db"]]
    return get_mongodb.database


def get_mysql():
    """
    a singleton function to get the mysql database
    """
    if not hasattr(get_mysql, "conn"):
        mysqlparams = get_secret("mysql")
        try:
            conn = pymysql.connect(
                host=mysqlparams["dbhost"],
                user=mysqlparams["dbuser"],
                password=mysqlparams["dbpassword"],
                database=mysqlparams["dbname"],
                ssl_disabled=True,
            )
            setattr(get_mysql, "conn", conn)
        except pymysql.Error as e:
            log.error(f"Failed to set up Mysql connection: {e}")
            raise HTTPException(status_code=503, detail="CannotConnectMysql")
    return getattr(get_mysql, "conn")


def mysql_engine():
    """
    a singleton function returning a sqlalchemy engine for the mysql database
    """
    if not hasattr(mysql_engine, "engine"):
        mysqlparams = get_secret("mysql")
        host = mysqlparams["dbhost"]
        user = mysqlparams["dbuser"]
        password = mysqlparams["dbpassword"]
        dbname = mysqlparams["dbname"]
        url = f"mysql+pymysql://{user}:{password}@{host}/{dbname}"
        mysql_engine.engine = create_engine(
            url,
            pool_recycle=300,
            pool_pre_ping=True,
            connect_args={
                "ssl_disabled": True,
            },
        )
    return mysql_engine.engine


# import all database classes
