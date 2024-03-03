import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from kbsb.main import app


@patch("kbsb.interclubs.api_interclubs.anon_getICteams")
def test_anon_getICTeams(anon_getICteams: AsyncMock, ic_team_factory):
    client = TestClient(app)
    anon_getICteams.return_value = ic_team_factory.batch(size=3)
    resp = client.get("/api/v1/interclubs/anon/icteams/123")
    reply = resp.json()
    assert resp.status_code == 200
    anon_getICteams.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.anon_getICclub")
def test_anon_getICclub(anon_getICclub: AsyncMock, ic_club_db_factory):
    client = TestClient(app)
    anon_getICclub.return_value = ic_club_db_factory.build()
    resp = client.get("/api/v1/interclubs/anon/icclub/123")
    reply = resp.json()
    assert resp.status_code == 200
    anon_getICclub.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.anon_getICclubs")
def test_anon_getICclubs(anon_getICclubs: AsyncMock, ic_club_item_factory):
    client = TestClient(app)
    anon_getICclubs.return_value = ic_club_item_factory.batch(3)
    resp = client.get("/api/v1/interclubs/anon/icclub")
    reply = resp.json()
    assert resp.status_code == 200
    anon_getICclubs.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_membertoken")
@patch("kbsb.interclubs.api_interclubs.clb_getICclub")
def test_clb_getICclub(clb_getICclub: AsyncMock, vmt: AsyncMock, ic_club_db_factory):
    client = TestClient(app)
    clb_getICclub.return_value = ic_club_db_factory.build()
    resp = client.get("/api/v1/interclubs/clb/icclub/123")
    reply = resp.json()
    assert resp.status_code == 200
    clb_getICclub.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_token")
@patch("kbsb.interclubs.api_interclubs.clb_getICclub")
def test_mgmt_getICclub(mgmt_getICclub: AsyncMock, vt: AsyncMock, ic_club_db_factory):
    client = TestClient(app)
    mgmt_getICclub.return_value = ic_club_db_factory.build()
    resp = client.get("/api/v1/interclubs/mgmt/icclub/123")
    reply = resp.json()
    assert resp.status_code == 200
    mgmt_getICclub.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_membertoken")
@patch("kbsb.interclubs.api_interclubs.clb_validateICPlayers")
def test_clb_validateICPlayers(
    clb_validateICPlayers: AsyncMock,
    vmt: AsyncMock,
    ic_player_update_factory,
    ic_player_validation_error_factory,
):
    client = TestClient(app)
    clb_validateICPlayers.return_value = ic_player_validation_error_factory.batch(3)
    pu = ic_player_update_factory.build()
    resp = client.post(
        "/api/v1/interclubs/clb/icclub/123/validate", json=jsonable_encoder(pu)
    )
    reply = resp.json()
    assert resp.status_code == 200
    clb_validateICPlayers.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_token")
@patch("kbsb.interclubs.api_interclubs.clb_validateICPlayers")
def test_mgmt_validateICPlayers(
    clb_validateICPlayers: AsyncMock,
    vt: AsyncMock,
    ic_player_update_factory,
    ic_player_validation_error_factory,
):
    client = TestClient(app)
    clb_validateICPlayers.return_value = ic_player_validation_error_factory.batch(3)
    pu = ic_player_update_factory.build()
    resp = client.post(
        "/api/v1/interclubs/mgmt/icclub/123/validate", json=jsonable_encoder(pu)
    )
    reply = resp.json()
    assert resp.status_code == 200
    clb_validateICPlayers.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_membertoken")
@patch("kbsb.interclubs.api_interclubs.clb_updateICplayers")
def test_clb_updateICPlayers(
    clb_updateICPlayers: AsyncMock,
    vmt: AsyncMock,
    ic_player_update_factory,
):
    client = TestClient(app)
    pu = ic_player_update_factory.build()
    resp = client.put("/api/v1/interclubs/clb/icclub/123", json=jsonable_encoder(pu))
    assert resp.status_code == 204
    clb_updateICPlayers.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_token")
@patch("kbsb.interclubs.api_interclubs.clb_updateICplayers")
def test_mgmt_updateICPlayers(
    clb_updateICPlayers: AsyncMock,
    vt: AsyncMock,
    ic_player_update_factory,
):
    client = TestClient(app)
    pu = ic_player_update_factory.build()
    resp = client.put("/api/v1/interclubs/mgmt/icclub/123", json=jsonable_encoder(pu))
    assert resp.status_code == 204
    clb_updateICPlayers.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.jwt_getunverifiedpayload")
@patch("kbsb.interclubs.api_interclubs.mgmt_getXlsAllplayerlist")
def test_mgmt_getXlsAllplayerlist(
    mgmt_getXlsAllplayerlist: AsyncMock,
    jwt_getunverifiedpayload: MagicMock,
):
    client = TestClient(app)
    jwt_getunverifiedpayload.return_value = {"sub": "jimi@frbe-kbsb-ksb.be"}
    mgmt_getXlsAllplayerlist.return_value = "a"
    resp = client.get("/api/v1/interclubs/mgmt/command/xls/allplayerlist?token=abc")
    assert resp.status_code == 200
    mgmt_getXlsAllplayerlist.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.anon_getXlsplayerlist")
def test_anon_getXlsplayerlist(
    anon_getXlsplayerlist: AsyncMock,
):
    client = TestClient(app)
    anon_getXlsplayerlist.return_value = "a"
    resp = client.get("/api/v1/interclubs/anon/command/xls/playerlist?idclub=123")
    assert resp.status_code == 200
    anon_getXlsplayerlist.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.anon_getICseries")
def test_anon_getICseries(
    anon_getICseries: AsyncMock,
    ic_series_factory,
):
    client = TestClient(app)
    anon_getICseries.return_value = ic_series_factory.batch(size=3)
    resp = client.get("/api/v1/interclubs/anon/icseries?idclub=123&round=2")
    assert resp.status_code == 200
    anon_getICseries.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_membertoken")
@patch("kbsb.interclubs.api_interclubs.clb_getICseries")
def test_clb_getICseries(
    clb_getICseries: AsyncMock,
    vmt: AsyncMock,
    ic_series_factory,
):
    client = TestClient(app)
    clb_getICseries.return_value = ic_series_factory.batch(size=3)
    resp = client.get("/api/v1/interclubs/clb/icseries?idclub=123&round=2")
    assert resp.status_code == 200
    clb_getICseries.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_token")
@patch("kbsb.interclubs.api_interclubs.clb_getICseries")
def test_mgmt_getICseries(
    clb_getICseries: AsyncMock,
    vt: AsyncMock,
    ic_series_factory,
):
    client = TestClient(app)
    clb_getICseries.return_value = ic_series_factory.batch(size=3)
    resp = client.get("/api/v1/interclubs/mgmt/icseries?idclub=123&round=2")
    assert resp.status_code == 200
    clb_getICseries.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_membertoken")
@patch("kbsb.interclubs.api_interclubs.clb_saveICplanning")
def test_clb_saveICplanning(
    clb_saveICplanning: AsyncMock,
    vmt: AsyncMock,
    ic_planning_factory,
):
    client = TestClient(app)
    icp = ic_planning_factory.build()
    resp = client.put("/api/v1/interclubs/clb/icplanning", json=jsonable_encoder(icp))
    assert resp.status_code == 201
    clb_saveICplanning.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_token")
@patch("kbsb.interclubs.api_interclubs.mgmt_saveICresults")
def test_mgmt_saveICresults(
    mgmt_saveICresults: AsyncMock,
    vt: AsyncMock,
    ic_result_factory,
):
    client = TestClient(app)
    icr = ic_result_factory.build()
    resp = client.put("/api/v1/interclubs/mgmt/icresults", json=jsonable_encoder(icr))
    assert resp.status_code == 201
    mgmt_saveICresults.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_membertoken")
@patch("kbsb.interclubs.api_interclubs.clb_saveICresults")
def test_clb_saveICresults(
    clb_saveICresults: AsyncMock,
    vt: AsyncMock,
    ic_result_factory,
):
    client = TestClient(app)
    icr = ic_result_factory.build()
    resp = client.put("/api/v1/interclubs/clb/icresults", json=jsonable_encoder(icr))
    assert resp.status_code == 201
    clb_saveICresults.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.anon_getICencounterdetails")
def test_anon_getICencounterdetails(
    anon_getICencounterdetails: AsyncMock,
    ic_game_details_factory,
):
    client = TestClient(app)
    anon_getICencounterdetails.return_value = ic_game_details_factory.batch(size=3)
    qp = {
        "division": 1,
        "index": "a",
        "round": 2,
        "icclub_home": 123,
        "icclub_visit": 234,
        "pairingnr_home": 3,
        "pairingnr_visit": 4,
    }
    qpstr = "&".join([f"{k}={v}" for (k, v) in qp.items()])
    resp = client.get(f"/api/v1/interclubs/anon/icresultdetails?{qpstr}")
    assert resp.status_code == 200
    anon_getICencounterdetails.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.anon_getICstandings")
def test_anon_getICstandings(
    anon_getICstandings: AsyncMock,
    ic_standings_db_factory,
):
    client = TestClient(app)
    anon_getICstandings.return_value = ic_standings_db_factory.batch(size=3)
    resp = client.get(f"/api/v1/interclubs/anon/icstandings?idclub=123")
    assert resp.status_code == 200
    anon_getICstandings.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_token")
@patch("kbsb.interclubs.api_interclubs.calc_belg_elo")
def test_calc_belg_elo(
    calc_belg_elo: AsyncMock,
    vt: AsyncMock,
):
    client = TestClient(app)
    resp = client.post("/api/v1/interclubs/mgmt/command/belg_elo?round=2")
    assert resp.status_code == 201
    calc_belg_elo.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_token")
@patch("kbsb.interclubs.api_interclubs.calc_belg_elo")
def test_calc_belg_elo(
    calc_belg_elo: AsyncMock,
    vt: AsyncMock,
):
    client = TestClient(app)
    resp = client.post("/api/v1/interclubs/mgmt/command/belg_elo?round=2")
    assert resp.status_code == 201
    calc_belg_elo.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_token")
@patch("kbsb.interclubs.api_interclubs.calc_fide_elo")
def test_calc_fide_elo(
    calc_fide_elo: AsyncMock,
    vt: AsyncMock,
):
    client = TestClient(app)
    resp = client.post("/api/v1/interclubs/mgmt/command/fide_elo?round=2")
    assert resp.status_code == 201
    calc_fide_elo.assert_awaited()


@patch("kbsb.interclubs.api_interclubs.validate_token")
@patch("kbsb.interclubs.api_interclubs.mgmt_generate_penalties")
def test_mgmt_generate_penalties(
    mgmt_generate_penalties: AsyncMock,
    vt: AsyncMock,
):
    client = TestClient(app)
    resp = client.post("/api/v1/interclubs/mgmt/command/penalties/2")
    assert resp.status_code == 201
    mgmt_generate_penalties.assert_awaited()
