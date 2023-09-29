import asyncio
import motor.motor_asyncio
from pydantic import BaseModel
from csv import DictReader
from typing import Literal, List
from unidecode import unidecode

client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://kbsb:6IMp3WpvtQkrrgiu@cluster0.a01j2.mongodb.net"
)
db = client.kbsb
clubcol = db.interclub2324club
seriescol = db.interclub2324series


class EloGame(BaseModel):
    idbel_white: int
    idfide_white: int
    fullname_white: str
    belrating_white: int = 0
    fiderating_white: int = 0
    natfide_white: str = "BEL"
    birthday_white: str
    title_white: str
    gender_white: str
    team_white: str

    idbel_black: int
    idfide_black: int
    fullname_black: str
    belrating_black: int = 0
    fiderating_black: int = 0
    natfide_black: str = "BEL"
    birthday_black: str
    idfide_black: int
    title_black: str
    gender_black: str
    team_black: str

    result: Literal["1-0", "½-½", "0-1", "1-0 FF", "0-1 FF", "0-0 FF"]


# data model
# plist = {}  # playerlist indexed by idclub
fided = {}  # fide data indexed by idbel
games = []
tlines = {}  # team lines index by team name, list gnr

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


def read_fide_data():
    with open("data/fide_icn2.csv") as ff:
        csvfide = DictReader(ff)
        for fd in csvfide:
            fided[int(fd["idbel"])] = fd


# TODO unidecode
# TODO Forfait


async def games_round1():
    cursor = seriescol.find({})
    for series in await cursor.to_list(length=50):
        encounters = series["rounds"][0]["encounters"]
        teams = {t["pairingnumber"]: t for t in series["teams"]}
        for enc in encounters:
            icclub_home = enc["icclub_home"]
            icclub_visit = enc["icclub_visit"]
            if icclub_home == 0 or icclub_visit == 0:
                continue  # skip bye
            for ix, g in enumerate(enc["games"]):
                idnh = g["idnumber_home"]
                idnv = g["idnumber_visit"]
                if not idnh or not idnv:
                    continue
                fideh = fided[idnh]
                fidev = fided[idnv]
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
                    team_white = teams[enc["pairingnr_visit"]]["name"]
                    team_black = teams[enc["pairingnr_home"]]["name"]
                    result = switch_result[g["result"]]
                else:
                    idbel_white, idbel_black = idnh, idnv
                    idfide_white, idfide_black = (
                        fideh["idfide"] or "",
                        fidev["idfide"] or "",
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
                    team_white = teams[enc["pairingnr_home"]]["name"]
                    team_black = teams[enc["pairingnr_visit"]]["name"]
                    result = g["result"]
                games.append(
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


def to_fide_elo():
    """
    writing a list EloGame records in a Belgian ELO file
    """
    hlines = [
        "012 Belgian Interclubs 2023 - 2024 - Round 1",
        "022 Various locations in Belgian Clubs",
        "032 BEL",
        "042 2023-09-24",
        "052 2023-09-24",
        "062 {npart}",
        "072 {nrated}",
        "082 {nteams}",
        "092 Standard Team Round Robin",
        "102 225185 Bailleul, Geert",
        "112 205494 Cornet, Luc",
        """122 90'/40 + 30'/end + 30"/move from move 1""",
    ]
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
    nrated = 0
    glines = []
    for g in games:
        if g.fiderating_white > 0:
            nrated += 1
        if g.fiderating_black > 0:
            nrated += 1
        glines.append({"gnr": npart + 1, "c": "w", "game": g, "opnr": npart + 2})
        glines.append({"gnr": npart + 2, "c": "b", "game": g, "opnr": npart + 1})
        wt = tlines.setdefault(unidecode(g.team_white), [])
        wt.append(npart + 1)
        bt = tlines.setdefault(unidecode(g.team_black), [])
        bt.append(npart + 2)
        ngames += 1
        npart += 2
    nteams = len(tlines)
    headerdict = {
        "ngames": ngames,
        "npart": npart,
        "nrated": nrated,
        "won": won,
        "drawn": drawn,
        "lost": lost,
        "nteams": nteams,
    }
    with open("test.txt", "w") as f:
        for l in hlines:
            fl = l.format(**headerdict)
            f.write(fl)
            f.write(linefeed)
        for gd in glines:
            ls = " " * 100
            ls = replaceAt(ls, 0, "001")
            ls = replaceAt(ls, 4, "{:4d}".format(gd["gnr"]))
            g = gd["game"]
            if gd["c"] == "w":
                if g.result == "1-0":
                    sc1 = 1.0
                    sc2 = "1"
                    opp = "{:4d}".format(gd["opnr"])
                if g.result == "½-½":
                    sc1 = 0.5
                    sc2 = "="
                    opp = "{:4d}".format(gd["opnr"])
                if g.result == "0-1":
                    sc1 = 0.0
                    sc2 = "0"
                    opp = "{:4d}".format(gd["opnr"])
                if g.result == "1-0 FF":
                    sc1 = 1.0
                    sc2 = "+"
                    opp = "0000"
                if g.result == "0-1 FF":
                    sc1 = 0.0
                    sc2 = "-"
                    opp = "0000"
                ls = replaceAt(ls, 9, "{:1s}".format(g.gender_white).lower())
                ls = replaceAt(ls, 10, "{:>3s}".format(g.title_white))
                ls = replaceAt(ls, 14, "{:33s}".format(g.fullname_white))
                ls = replaceAt(ls, 48, "{:4d}".format(g.fiderating_white))
                ls = replaceAt(ls, 53, "{:3s}".format(g.natfide_white))
                ls = replaceAt(ls, 57, "{:11d}".format(g.idfide_white))
                ls = replaceAt(ls, 69, "{:10s}".format(g.birthday_white))
                ls = replaceAt(ls, 80, "{:4.1f}".format(sc1))
                ls = replaceAt(ls, 91, opp)
                ls = replaceAt(ls, 96, "w")
                ls = replaceAt(ls, 98, sc2)
            else:
                if g.result == "1-0":
                    sc1 = 0.0
                    sc2 = "0"
                    opp = "{:4d}".format(gd["opnr"])
                if g.result == "½-½":
                    sc1 = 0.5
                    sc2 = "="
                    opp = "{:4d}".format(gd["opnr"])
                if g.result == "0-1":
                    sc1 = 1.0
                    sc2 = "1"
                    opp = "{:4d}".format(gd["opnr"])
                if g.result == "1-0 FF":
                    sc1 = 0.0
                    sc2 = "-"
                    opp = "0000"
                if g.result == "0-1 FF":
                    sc1 = 1.0
                    sc2 = "+"
                    opp = "0000"
                ls = replaceAt(ls, 9, "{:1s}".format(g.gender_black).lower())
                ls = replaceAt(ls, 10, "{:>3s}".format(g.title_black))
                ls = replaceAt(ls, 14, "{:33s}".format(g.fullname_black))
                ls = replaceAt(ls, 48, "{:4d}".format(g.fiderating_black))
                ls = replaceAt(ls, 53, "{:3s}".format(g.natfide_black))
                ls = replaceAt(ls, 57, "{:11d}".format(g.idfide_black))
                ls = replaceAt(ls, 69, "{:10s}".format(g.birthday_black))
                ls = replaceAt(ls, 80, "{:4.1f}".format(sc1))
                ls = replaceAt(ls, 91, opp)
                ls = replaceAt(ls, 96, "b")
                ls = replaceAt(ls, 98, sc2)
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


async def create_elo_file():
    read_fide_data()
    await games_round1()
    print("n games", len(games))
    to_fide_elo()


loop = client.get_io_loop()
loop.run_until_complete(create_elo_file())
