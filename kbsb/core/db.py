# copyright Ruben Decrop 2012 - 2020
from asyncio.constants import SSL_HANDSHAKE_TIMEOUT
import logging

logger = logging.getLogger(__name__)

from datetime import datetime, date
from reddevil.core import get_secret, RdInternalServerError
import mysql.connector


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


def get_mysql():
    if not hasattr(get_mysql, "params"):
        setattr(get_mysql, "params", get_secret("mysql"))
    try:
        cnx = mysql.connector.connect(
            pool_name="kbsbpool",
            pool_size=5,
            user=get_mysql.params["dbuser"],
            password=get_mysql.params["dbpassword"],
            host=get_mysql.params["dbhost"],
            database=get_mysql.params["dbname"],
            ssl_disabled=True,
        )
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            logger.exception("Something is wrong with your user name or password")
            raise RdInternalServerError(description="Invalid DB credentials")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            logger.exception("Database does not exist")
            raise RdInternalServerError(description="Invalid DB")
        else:
            logger.exception(err)
            raise RdInternalServerError(description="Unknown DB error")
    return cnx
