import logging

from pydantic import BaseModel
from csv import DictReader
from datetime import date
from typing import Literal, List
from unidecode import unidecode
from .md_elo import EloGame, EloPlayer
from ..interclubs.md_interclubs import DbICSeries, ic_dates

logger = logging.getLogger(__name__)

# data model
elodata = {}  # elo data indexed by idbel
games1 = []  # divison 1 to 4
games2 = []  # division 5
tlines = {}  # team lines index by team name, list gnr
elopl = {}  # all players index by idbel
cnt = {
    "won": 0,
    "drawn": 0,
    "lost": 0,
    "npart": 0,
    "ngames": 0,
    "nrated": 0,
    "mteams": 0.0,
}
sortedplayers = []  # sorted idbel by elo and name
switch_result = {
    "1-0": "0-1",
    "½-½": "½-½",
    "0-1": "1-0",
    "1-0 FF": "0-1 FF",
    "0-1 FF": "1-0 FF",
    "0-0 FF": "0-0 FF",
}
linefeed = "\x0D\x0A"


def replaceAt(source, index, replace):
    """
    creates a copy of source where replace is filled in at index
    """
    return source[:index] + replace + source[index + len(replace) :]


def read_elo_data():
    with open("data/eloprocessing.csv") as ff:
        csvfide = DictReader(ff)
        for fd in csvfide:
            elodata[int(fd["idnumber"])] = fd


async def games_round(round):
    games1 = []
    games2 = []
    for series in await DbICSeries.find_multiple({"_model": DbICSeries.DOCUMENTTYPE}):
        print(f"processing {series.division} {series.index}")
        for r in series.rounds:
            if r.round == round:
                encounters = r.encounters
                break
        for enc in encounters:
            icclub_home = enc.icclub_home
            icclub_visit = enc.icclub_visit
            if icclub_home == 0 or icclub_visit == 0:
                continue  # skip bye
            for ix, g in enumerate(enc.games):
                idnh = g.idnumber_home
                idnv = g.idnumber_visit
                if not idnh or not idnv:
                    continue
                elodatah = elodata[idnh]
                elodatav = elodata[idnv]
                if ix % 2:
                    idbel_white, idbel_black = idnv, idnh
                    belrating_white, belrating_black = (
                        elodatav["belrating"],
                        elodatah["belrating"],
                    )
                    fullname_white = (
                        f"{elodatav['last_name']}, {elodatav['first_name']}"
                    )
                    fullname_black = (
                        f"{elodatah['last_name']}, {elodatah['first_name']}"
                    )
                    natfide_white, natfide_black = (
                        elodatav["natfide"] or "BEL",
                        elodatah["natfide"] or "BEL",
                    )
                    gender_white, gender_black = (
                        elodatav["gender2"],
                        elodatah["gender2"],
                    )
                    result = switch_result[g.result]
                else:
                    idbel_white, idbel_black = idnh, idnv
                    belrating_white, belrating_black = (
                        elodatah["belrating"],
                        elodatav["belrating"],
                    )
                    fullname_white = (
                        f"{elodatah['last_name']}, {elodatah['first_name']}"
                    )
                    fullname_black = (
                        f"{elodatav['last_name']}, {elodatav['first_name']}"
                    )
                    natfide_white, natfide_black = (
                        elodatah["natfide"],
                        elodatav["natfide"],
                    )
                    gender_white, gender_black = (
                        elodatah["gender"] or elodatah["gender2"],
                        elodatav["gender"] or elodatav["gender2"],
                    )
                    result = g.result
                game = EloGame(
                    belrating_white=belrating_white,
                    fullname_white=fullname_white,
                    gender_white=gender_white,
                    idbel_white=idbel_white,
                    natfide_white=natfide_white,
                    belrating_black=belrating_black,
                    fullname_black=fullname_black,
                    gender_black=gender_black,
                    idbel_black=idbel_black,
                    natfide_black=natfide_black,
                    result=result,
                )
                if series.division == 5:
                    games2.append(game)
                else:
                    games1.append(game)
    return games1, games2


def to_belgian_elo(records: List[EloGame], label: str, round: int):
    """
    writing a list EloGame records in a Belgian ELO file
    """
    hlines = [
        "00A ### Interclubs",
        "00B 1 rondes",
        "00C Envoi des rondes {round} à {round}",
        "00D Envoi par : interclubs@frbe-kbsb-ksb.be",
        "00E Envoi par le club : 998",
        "00F P={npart} R=1 S={icdate:%d/%m/%y} E={icdate:%d/%m/%y} +{won} ={drawn} -{lost}",
        "012 Belgian Interclubs 2023 - 2024 - Round {round}",
        "022 Various locations in Belgian Clubs",
        "032 BEL",
        "042 {icdate}",
        "052 {icdate}",
        "062 {npart}",
        "102 Cornet, Luc",
    ]
    icdate = date.fromisoformat(ic_dates[round])
    ls = " " * 100
    # make line 132
    ls = replaceAt(ls, 0, "132")
    ls = replaceAt(ls, 91, "24/09/23")
    hlines.append(ls)
    won = 0
    drawn = 0
    lost = 0
    npart = 0
    ngames = 0
    glines = []
    for g in records:
        if g.result not in ["1-0", "0-1", "½-½"]:
            continue
        # fetch player from signaletique
        whiteline = {
            "n": npart + 1,
            "name": g.fullname_white,
            "idn": g.idbel_white,
            "nat": g.natfide_white or "BEL",
            "elo": g.belrating_white,
            "opponent": npart + 2,
            "color": "w",
        }
        blackline = {
            "n": npart + 2,
            "name": g.fullname_black,
            "idn": g.idbel_black,
            "nat": g.natfide_black or "BEL",
            "elo": g.belrating_black,
            "opponent": npart + 1,
            "color": "b",
        }
        if g.result == "1-0":
            whiteline["rs"] = "1"
            blackline["rs"] = "0"
            whiteline["score"] = 1.0
            blackline["score"] = 0.0
            won += 1
            lost += 1
        if g.result == "½-½":
            drawn += 2
            whiteline["rs"] = "="
            blackline["rs"] = "="
            whiteline["score"] = 0.5
            blackline["score"] = 0.5
        if g.result == "0-1":
            won += 1
            lost += 1
            whiteline["rs"] = "0"
            blackline["rs"] = "1"
            whiteline["score"] = 0.0
            blackline["score"] = 1.0
        glines.append(whiteline)
        glines.append(blackline)
        ngames += 1
        npart += 2
    with open(f"ICN_R{round}_{label}.txt", "w", encoding="latin1") as f:
        headerdict = {
            "ngames": ngames,
            "npart": npart,
            "won": won,
            "drawn": drawn,
            "lost": lost,
            "round": round,
            "icdate": icdate,
        }
        for l in hlines:
            fl = l.format(**headerdict)
            f.write(fl)
            f.write(linefeed)
        for l in glines:
            ls = " " * 100
            ls = replaceAt(ls, 0, "001")
            ls = replaceAt(ls, 4, "{:4d}".format(l["n"]))
            ls = replaceAt(ls, 14, "{:32s}".format(l["name"]))
            ls = replaceAt(ls, 48, "{:4d}".format(l["elo"]))
            ls = replaceAt(ls, 63, "{:5d}".format(l["idn"]))
            ls = replaceAt(ls, 81, "{:3.1f}".format(l["score"]))
            ls = replaceAt(ls, 91, "{:4d}".format(l["opponent"]))
            ls = replaceAt(ls, 96, "{:1s}".format(l["color"]))
            ls = replaceAt(ls, 98, "{:1s}".format(l["rs"]))
            f.write(ls)
            f.write(linefeed)


async def calc_belg_elo(round):
    read_elo_data()
    games1, games2 = await games_round(round)
    logger.info(f"games {len(games1)} {len(games2)}")
    to_belgian_elo(games1, "part1", round)
    to_belgian_elo(games2, "part2", round)
