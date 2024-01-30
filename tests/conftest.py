import pytest

from .factories import *

import mysql.connector


@pytest.fixture
def mysql_connection():
    cnx = mysql.connector.connect(
        pool_name="kbsbpool",
        pool_size=5,
        user="root",
        password="tiger",
        host="127.0.0.1",
        database="testkbsb",
    )
    return cnx
