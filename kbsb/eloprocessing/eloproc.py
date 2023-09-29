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


class EloPlayer(BaseModel):
    idbel: int
    idfide: int
    fullname: str
    fiderating: int = 0
    natfide: str = "BEL"
    birthday: str
    title: str
    gender: str
    idopp: int
    myix: int = 0
    oppix: int = 0
    team: str
    sc1: float
    sc2: str = ""
    color: str


# data model
# plist = {}  # playerlist indexed by idclub
fided = {}  # fide data indexed by idbel
games = []
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


def to_elo_players():
    global sortedplayers
    for g in games:
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
    print("sortedplayers", len(sortedplayers))
    for ix, key in enumerate(sortedplayers):
        elopl[key].myix = ix + 1
        elopl[elopl[key].idopp].oppix = ix + 1
        tlines[elopl[key].team].append(ix + 1)


def to_fide_elo():
    global sortedplayers
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
    for g in games:
        if g.fiderating_white > 0:
            cnt["nrated"] += 1
        if g.fiderating_black > 0:
            cnt["nrated"] += 1
        cnt["ngames"] += 1
        cnt["npart"] += 2
    cnt["nteams"] = len(tlines)
    with open("test.txt", "w") as f:
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
    to_elo_players()
    to_fide_elo()


loop = client.get_io_loop()
loop.run_until_complete(create_elo_file())
