import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from kbsb.main import app
from kbsb.interclubs import ICGame
from kbsb.interclubs.series import mgmt_saveICresults, clb_saveICresults, calc_points


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@pytest.mark.asyncio
async def test_mgmt_saveICresults(
    dbSeries: MagicMock,
    dbStandings: MagicMock,
    calc_points: MagicMock,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    game1 = ic_game_factory.build(result="", overruled=None)
    encounter1 = ic_encounter_factory.build(games=[game1])
    round1 = ic_round_factory.build(encounters=[encounter1])
    series1 = ic_series_factory.build(rounds=[round1])
    dbSeries.find_single = AsyncMock(return_value=series1)
    updategame1 = game1.model_copy()
    updategame1.result = "1-0"
    resultitem1 = ic_result_item_factory.build(
        games=[updategame1],
        round=round1.round,
        icclub_home=encounter1.icclub_home,
        icclub_visit=encounter1.icclub_visit,
        pairingnr_home=encounter1.pairingnr_home,
        pairingnr_visit=encounter1.pairingnr_visit,
    )
    dbSeries.update = AsyncMock()
    dbStandings.find_single = AsyncMock(return_value=ic_standings_db_factory.build())
    dbStandings.update = AsyncMock()
    await mgmt_saveICresults([resultitem1])
    dbSeries.update.assert_awaited()
    round = dbSeries.update.call_args[0][1]["rounds"][0]
    game = round["encounters"][0]["games"][0]
    assert game["result"] == "1-0"
    assert game["overruled"] is None


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@pytest.mark.asyncio
async def test_mgmt_saveICresults_overrule(
    dbSeries: MagicMock,
    dbStandings: MagicMock,
    calc_points: MagicMock,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    game1 = ic_game_factory.build(result="1-0", overruled=None)
    encounter1 = ic_encounter_factory.build(games=[game1])
    round1 = ic_round_factory.build(encounters=[encounter1])
    series1 = ic_series_factory.build(rounds=[round1])
    dbSeries.find_single = AsyncMock(return_value=series1)
    updategame1 = game1.model_copy()
    updategame1.overruled = "0-1"
    resultitem1 = ic_result_item_factory.build(
        games=[updategame1],
        round=round1.round,
        icclub_home=encounter1.icclub_home,
        icclub_visit=encounter1.icclub_visit,
        pairingnr_home=encounter1.pairingnr_home,
        pairingnr_visit=encounter1.pairingnr_visit,
    )
    dbSeries.update = AsyncMock()
    dbStandings.find_single = AsyncMock(return_value=ic_standings_db_factory.build())
    dbStandings.update = AsyncMock()
    await mgmt_saveICresults([resultitem1])
    dbSeries.update.assert_awaited()
    round = dbSeries.update.call_args[0][1]["rounds"][0]
    game = round["encounters"][0]["games"][0]
    assert game["result"] == "1-0"
    assert game["overruled"] == "0-1"


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@pytest.mark.asyncio
async def test_clb_saveICresults(
    dbSeries: MagicMock,
    dbStandings: MagicMock,
    calc_points: MagicMock,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    game1 = ic_game_factory.build(result="", overruled=None)
    encounter1 = ic_encounter_factory.build(games=[game1])
    round1 = ic_round_factory.build(encounters=[encounter1])
    series1 = ic_series_factory.build(rounds=[round1])
    dbSeries.find_single = AsyncMock(return_value=series1)
    updategame1 = game1.model_copy()
    updategame1.result = "1-0"
    resultitem1 = ic_result_item_factory.build(
        games=[updategame1],
        round=round1.round,
        icclub_home=encounter1.icclub_home,
        icclub_visit=encounter1.icclub_visit,
        pairingnr_home=encounter1.pairingnr_home,
        pairingnr_visit=encounter1.pairingnr_visit,
    )
    dbSeries.update = AsyncMock()
    dbStandings.find_single = AsyncMock(return_value=ic_standings_db_factory.build())
    dbStandings.update = AsyncMock()
    await clb_saveICresults([resultitem1])
    dbSeries.update.assert_awaited()
    round = dbSeries.update.call_args[0][1]["rounds"][0]
    game = round["encounters"][0]["games"][0]
    assert game["result"] == "1-0"
    assert game["overruled"] is None


@patch("kbsb.interclubs.series.calc_points")
@patch("kbsb.interclubs.series.DbICStandings")
@patch("kbsb.interclubs.series.DbICSeries")
@pytest.mark.asyncio
async def test_clb_saveICresults_overrule(
    dbSeries: MagicMock,
    dbStandings: MagicMock,
    calc_points: MagicMock,
    ic_result_item_factory,
    ic_series_factory,
    ic_game_factory,
    ic_encounter_factory,
    ic_round_factory,
    ic_standings_db_factory,
):
    game1 = ic_game_factory.build(result="1-0", overruled=None)
    encounter1 = ic_encounter_factory.build(games=[game1])
    round1 = ic_round_factory.build(encounters=[encounter1])
    series1 = ic_series_factory.build(rounds=[round1])
    dbSeries.find_single = AsyncMock(return_value=series1)
    updategame1 = game1.model_copy()
    updategame1.overruled = "0-1"
    resultitem1 = ic_result_item_factory.build(
        games=[updategame1],
        round=round1.round,
        icclub_home=encounter1.icclub_home,
        icclub_visit=encounter1.icclub_visit,
        pairingnr_home=encounter1.pairingnr_home,
        pairingnr_visit=encounter1.pairingnr_visit,
    )
    dbSeries.update = AsyncMock()
    dbStandings.find_single = AsyncMock(return_value=ic_standings_db_factory.build())
    dbStandings.update = AsyncMock()
    await clb_saveICresults([resultitem1])
    dbSeries.update.assert_awaited()
    round = dbSeries.update.call_args[0][1]["rounds"][0]
    game = round["encounters"][0]["games"][0]
    assert game["result"] == "1-0"
    assert game["overruled"] is None


def test_calc_points(ic_encounter_factory, ic_game_factory):
    game1 = ic_game_factory.build(result="1-0", overruled=None)
    game2 = ic_game_factory.build(result="½-½", overruled=None)
    encounter1 = ic_encounter_factory.build(games=[game1, game2], played=False)
    calc_points(encounter1)
    assert encounter1.played
    assert encounter1.boardpoint2_home == 3
    assert encounter1.boardpoint2_visit == 1
    assert encounter1.matchpoint_home == 2
    assert encounter1.matchpoint_visit == 0


def test_calc_points_empty(ic_encounter_factory, ic_game_factory):
    game1 = ic_game_factory.build(result="1-0", overruled=None)
    game2 = ic_game_factory.build(result="", overruled=None)
    encounter1 = ic_encounter_factory.build(games=[game1, game2], played=False)
    calc_points(encounter1)
    assert not encounter1.played
    assert encounter1.boardpoint2_home == 2
    assert encounter1.boardpoint2_visit == 0
    assert encounter1.matchpoint_home == 0
    assert encounter1.matchpoint_visit == 0


def test_calc_points_overrule(ic_encounter_factory, ic_game_factory):
    game1 = ic_game_factory.build(result="1-0", overruled=None)
    game2 = ic_game_factory.build(result="½-½", overruled="0-1")
    encounter1 = ic_encounter_factory.build(games=[game1, game2], played=False)
    calc_points(encounter1)
    assert encounter1.played
    assert encounter1.boardpoint2_home == 2
    assert encounter1.boardpoint2_visit == 2
    assert encounter1.matchpoint_home == 1
    assert encounter1.matchpoint_visit == 1
