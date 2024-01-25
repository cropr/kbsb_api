import pytest
import datetime
from typing import List
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from kbsb.member.mysql_member import (
    mysql_anon_getmember,
    mysql_anon_getclubmembers,
    mysql_anon_getfidemember,
    mysql_anon_belid_from_fideid,
    mysql_mgmt_getclubmembers,
    mysql_mgmt_getmember,
)
from kbsb.member.md_member import AnonMember, Member


@patch("kbsb.member.mysql_member.get_elotable")
@patch("kbsb.member.mysql_member.get_mysql")
@pytest.mark.asyncio
async def test_mysql_anon_getmember(get_mysql, get_elotable, mysql_connection):
    get_mysql.return_value = mysql_connection
    get_elotable.return_value = "p_player202401"
    me = await mysql_anon_getmember(45608)
    assert isinstance(me, AnonMember)
    assert me.first_name == "Ruben"
    assert me.idclub == 301
    assert me.birthyear == 1965
    assert me.idfide == 201308


@patch("kbsb.member.mysql_member.current_affiliation_year")
@patch("kbsb.member.mysql_member.get_elotable")
@patch("kbsb.member.mysql_member.get_mysql")
@pytest.mark.asyncio
async def test_mysql_mgmt_getmember(
    get_mysql, get_elotable, current_affiliation_year, mysql_connection
):
    get_mysql.return_value = mysql_connection
    get_elotable.return_value = "p_player202401"
    current_affiliation_year.return_value = 2024
    me = await mysql_mgmt_getmember(45608)
    assert isinstance(me, Member)
    assert me.first_name == "Ruben"
    assert me.idclub == 301
    assert me.birthdate == datetime.date(1965, 4, 21)
    assert me.idfide == 201308
    assert me.deceased == 0


@patch("kbsb.member.mysql_member.current_affiliation_year")
@patch("kbsb.member.mysql_member.get_elotable")
@patch("kbsb.member.mysql_member.get_mysql")
@pytest.mark.asyncio
async def test_mysql_anon_getclubmembers(
    get_mysql, get_elotable, current_affiliation_year, mysql_connection
):
    get_mysql.return_value = mysql_connection
    get_elotable.return_value = "p_player202401"
    current_affiliation_year.return_value = 2024
    we = await mysql_anon_getclubmembers(301)
    assert isinstance(we, list)
    me = we[0]
    assert isinstance(me, AnonMember)
    assert me.last_name == "Decrop"


@patch("kbsb.member.mysql_member.current_affiliation_year")
@patch("kbsb.member.mysql_member.get_elotable")
@patch("kbsb.member.mysql_member.get_mysql")
@pytest.mark.asyncio
async def test_mysql_mgmt_getclubmembers(
    get_mysql, get_elotable, current_affiliation_year, mysql_connection
):
    get_mysql.return_value = mysql_connection
    get_elotable.return_value = "p_player202401"
    current_affiliation_year.return_value = 2024
    we = await mysql_mgmt_getclubmembers(301)
    assert isinstance(we, list)
    me = we[0]
    assert isinstance(me, Member)
    assert me.last_name == "Decrop"


@patch("kbsb.member.mysql_member.get_elotable")
@patch("kbsb.member.mysql_member.get_mysql")
@pytest.mark.asyncio
async def test_mysql_anon_getfidemember(get_mysql, get_elotable, mysql_connection):
    get_mysql.return_value = mysql_connection
    get_elotable.return_value = "p_player202401"
    me = await mysql_anon_getfidemember(201308)
    assert isinstance(me, AnonMember)
    assert me.first_name == "Ruben"
    assert me.birthyear == 1965
    assert me.nationalityfide == "BEL"


@patch("kbsb.member.mysql_member.get_elotable")
@patch("kbsb.member.mysql_member.get_mysql")
@pytest.mark.asyncio
async def test_mysql_anon_belid_form_fideid(get_mysql, get_elotable, mysql_connection):
    get_mysql.return_value = mysql_connection
    get_elotable.return_value = "p_player202401"
    me = await mysql_anon_belid_from_fideid(201308)
    assert me == 45608
