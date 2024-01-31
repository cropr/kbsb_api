import logging

from pydantic import BaseModel
from csv import DictReader
from datetime import date
from typing import Literal, List
from unidecode import unidecode
from .md_elo import EloGame, EloPlayer
from .md_interclubs import DbICSeries, ICROUNDS

logger = logging.getLogger(__name__)


# TODO eloprocessing.csv needs to be automated !!!

# data model
elodata = {}  # elo data indexed by idbel
belgames1 = []  # divison 1 to 4
belgames2 = []  # division 5
fidegames = []
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


async def belgames_round(round):
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


async def fidegames_round(round):
    for series in await DbICSeries.find_multiple({"_model": DbICSeries.DOCUMENTTYPE}):
        for r in series.rounds:
            if r.round == round:
                encounters = r.encounters
                break
        teams = {t.pairingnumber: t for t in series.teams}
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
                fideh = elodata.get(idnh, None)
                fidev = elodata.get(idnv, None)
                if not fideh or not fidev:
                    logger.info(
                        f"failed fidev or fideh, updateing eloprocessin.csv might help"
                    )
                if ix % 2:
                    idbel_white, idbel_black = idnv, idnh
                    idfide_white, idfide_black = (
                        fidev["idfide"] or "",
                        fideh["idfide"] or "",
                    )
                    fullname_white = fidev["fullname"]
                    if not fullname_white:
                        ln = unidecode(fidev["last_name"])
                        fn = unidecode(fidev["first_name"])
                        fullname_white = f"{ln}, {fn}"
                    fullname_black = fideh["fullname"]
                    if not fullname_black:
                        ln = unidecode(fideh["last_name"])
                        fn = unidecode(fideh["first_name"])
                        fullname_black = f"{ln}, {fn}"
                    fiderating_white, fiderating_black = (
                        fidev["fiderating"] or 0,
                        fideh["fiderating"] or 0,
                    )
                    natfide_white, natfide_black = (
                        fidev["natfide"] or "BEL",
                        fideh["natfide"] or "BEL",
                    )
                    birthday_white, birthday_black = (
                        fidev["birthday"],
                        fideh["birthday"],
                    )
                    title_white, title_black = fidev["title"], fideh["title"]
                    gender_white, gender_black = (
                        fidev["gender"] or fidev["gender2"],
                        fideh["gender"] or fideh["gender2"],
                    )
                    team_white = teams[enc.pairingnr_visit].name
                    team_black = teams[enc.pairingnr_home].name
                    result = switch_result[g.result]
                else:
                    idbel_white, idbel_black = idnh, idnv
                    idfide_white, idfide_black = (
                        fideh.get("idfide", "") or "",
                        fidev.get("idfide", "") or "",
                    )
                    fullname_white = fideh["fullname"]
                    if not fullname_white:
                        ln = unidecode(fideh["last_name"])
                        fn = unidecode(fideh["first_name"])
                        fullname_white = f"{ln}, {fn}"
                    fullname_black = fidev["fullname"]
                    if not fullname_black:
                        ln = unidecode(fidev["last_name"])
                        fn = unidecode(fidev["first_name"])
                        fullname_black = f"{ln}, {fn}"
                    fiderating_white, fiderating_black = (
                        fideh["fiderating"] or 0,
                        fidev["fiderating"] or 0,
                    )
                    natfide_white, natfide_black = fideh["natfide"], fidev["natfide"]
                    birthday_white, birthday_black = (
                        fideh["birthday"],
                        fidev["birthday"],
                    )
                    title_white, title_black = fideh["title"], fidev["title"]
                    gender_white, gender_black = (
                        fideh["gender"] or fideh["gender2"],
                        fidev["gender"] or fidev["gender2"],
                    )
                    team_white = teams[enc.pairingnr_home].name
                    team_black = teams[enc.pairingnr_visit].name
                    result = g.result
                fidegames.append(
                    EloGame(
                        idbel_white=idbel_white,
                        idfide_white=idfide_white,
                        fullname_white=fullname_white,
                        fiderating_white=fiderating_white or 0,
                        natfide_white=natfide_white,
                        birthday_white=birthday_white,
                        title_white=title_white,
                        gender_white=gender_white,
                        team_white=team_white,
                        idbel_black=idbel_black,
                        idfide_black=idfide_black,
                        fullname_black=fullname_black,
                        fiderating_black=fiderating_black,
                        natfide_black=natfide_black,
                        birthday_black=birthday_black,
                        title_black=title_black,
                        gender_black=gender_black,
                        team_black=team_black,
                        result=result,
                    )
                )


def to_elo_players():
    global sortedplayers
    for g in fidegames:
        wt = tlines.setdefault(unidecode(g.team_white), [])
        bt = tlines.setdefault(unidecode(g.team_black), [])
        wopp = ""
        bopp = ""
        if g.result == "1-0":
            wsc1 = 1.0
            bsc1 = 0.0
            wsc2 = "1"
            bsc2 = "0"
        if g.result == "½-½":
            wsc1 = 0.5
            bsc1 = 0.5
            wsc2 = "="
            bsc2 = "="
        if g.result == "0-1":
            wsc1 = 0.0
            bsc1 = 1.0
            wsc2 = "0"
            bsc2 = "1"
        if g.result == "1-0 FF":
            wsc1 = 1.0
            wsc2 = "+"
            wopp = "0000"
            bsc1 = 0.0
            bsc2 = "-"
            bopp = "0000"
        if g.result == "0-1 FF":
            wsc1 = 0.0
            wsc2 = "-"
            wopp = "0000"
            bsc1 = 1.0
            bsc2 = "+"
            bopp = "0000"
        white = EloPlayer(
            idbel=g.idbel_white,
            idfide=g.idfide_white,
            fullname=g.fullname_white,
            fiderating=g.fiderating_white,
            natfide=g.natfide_white,
            birthday=g.birthday_white,
            title=g.title_white,
            gender=g.gender_white,
            sc1=wsc1,
            sc2=wsc2,
            idopp=g.idbel_black,
            team=unidecode(g.team_white),
            color="w",
        )
        black = EloPlayer(
            idbel=g.idbel_black,
            idfide=g.idfide_black,
            fullname=g.fullname_black,
            fiderating=g.fiderating_black,
            natfide=g.natfide_black,
            birthday=g.birthday_black,
            title=g.title_black,
            gender=g.gender_black,
            sc1=bsc1,
            sc2=bsc2,
            idopp=g.idbel_white,
            team=unidecode(g.team_black),
            color="b",
        )
        elopl[white.idbel] = white
        elopl[black.idbel] = black
    sortedplayers = sorted(
        elopl.keys(), key=lambda x: (-elopl[x].fiderating, elopl[x].fullname)
    )
    logger.info(f"sortedplayers {len(sortedplayers)}")
    for ix, key in enumerate(sortedplayers):
        elopl[key].myix = ix + 1
        elopl[elopl[key].idopp].oppix = ix + 1
        tlines[elopl[key].team].append(ix + 1)


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
    icdate = ICROUNDS[round]
    ls = " " * 100
    # make line 132
    ls = replaceAt(ls, 0, "132")
    ls = replaceAt(ls, 91, icdate.strftime("%y.%m.%d"))
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


def to_fide_elo(round):
    global sortedplayers
    """
    writing a list EloGame records in a Belgian ELO file
    """
    hlines = [
        "012 Belgian Interclubs 2023 - 2024 - Round {round}",
        "022 Various locations in Belgian Clubs",
        "032 BEL",
        "042 {icdate}",
        "052 {icdate}",
        "062 {npart}",
        "072 {nrated}",
        "082 {nteams}",
        "092 Standard Team Round Robin",
        "102 225185 Bailleul, Geert",
        "112 205494 Cornet, Luc",
        """122 90'/40 + 30'/end + 30"/move from move 1""",
    ]
    icdate = ICROUNDS[round]
    ls = " " * 100
    # make line 132
    ls = replaceAt(ls, 0, "132")
    ls = replaceAt(ls, 91, icdate.strftime("%d/%m/%y"))
    hlines.append(ls)
    for g in fidegames:
        if g.fiderating_white > 0:
            cnt["nrated"] += 1
        if g.fiderating_black > 0:
            cnt["nrated"] += 1
        cnt["ngames"] += 1
        cnt["npart"] += 2
    cnt["nteams"] = len(tlines)
    cnt["icdate"] = icdate
    cnt["round"] = round
    with open(f"ICN_fide_R{round}.txt", "w") as f:
        for l in hlines:
            fl = l.format(**cnt)
            f.write(fl)
            f.write(linefeed)
        for key in sortedplayers:
            pl = elopl[key]
            ls = " " * 100
            ls = replaceAt(ls, 0, "001")
            ls = replaceAt(ls, 4, "{:4d}".format(pl.myix))
            ls = replaceAt(ls, 9, "{:1s}".format(pl.gender.lower()))
            ls = replaceAt(ls, 10, "{:>3s}".format(pl.title))
            ls = replaceAt(ls, 14, "{:33s}".format(pl.fullname))
            ls = replaceAt(ls, 48, "{:4d}".format(pl.fiderating))
            ls = replaceAt(ls, 53, pl.natfide)
            ls = replaceAt(ls, 57, "{:11d}".format(pl.idfide))
            ls = replaceAt(ls, 69, "{:10s}".format(pl.birthday))
            ls = replaceAt(ls, 80, "{:4.1f}".format(pl.sc1))
            ls = replaceAt(ls, 91, "{:4d}".format(pl.oppix))
            ls = replaceAt(ls, 96, pl.color)
            ls = replaceAt(ls, 98, pl.sc2)
            if "`" in ls:
                ls = ls.replace("`", "'")
            f.write(ls)
            f.write(linefeed)
        sortedkeys = sorted(tlines.keys())
        for tk in sortedkeys:
            ls = " " * 100
            ls = replaceAt(ls, 0, "013")
            ls = replaceAt(ls, 5, tk)
            for ix, pl in enumerate(tlines[tk]):
                ls = replaceAt(ls, 36 + 6 * ix, "{:4d}".format(pl))
            f.write(ls)
            f.write(linefeed)


async def calc_fide_elo(round: int):
    read_elo_data()
    await fidegames_round(round)
    to_elo_players()
    to_fide_elo(round)


async def calc_belg_elo(round):
    read_elo_data()
    games1, games2 = await belgames_round(round)
    logger.info(f"games {len(games1)} {len(games2)}")
    to_belgian_elo(games1, "part1", round)
    to_belgian_elo(games2, "part2", round)
