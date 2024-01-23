import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from kbsb.main import app


@patch("kbsb.member.api_member.anon_getmember")
def test_anon_getmember(anon_getmember: AsyncMock, anon_member_factory):
    client = TestClient(app)
    anon_getmember.return_value = anon_member_factory.build()
    resp = client.get("/api/v1/member/anon/member/123")
    reply = resp.json()
    assert resp.status_code == 200
    assert "birthyear" in reply
    anon_getmember.assert_awaited()


@patch("kbsb.member.api_member.anon_getfidemember")
def test_anon_getfidemember(anon_getmember: AsyncMock, anon_member_factory):
    client = TestClient(app)
    anon_getmember.return_value = anon_member_factory.build()
    resp = client.get("/api/v1/member/anon/fidemember/123")
    reply = resp.json()
    assert resp.status_code == 200
    assert "birthyear" in reply
    anon_getmember.assert_awaited()
