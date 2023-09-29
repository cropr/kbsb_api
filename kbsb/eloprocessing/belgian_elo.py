from pydantic import BaseModel
from typing import Literal, List
from csv import DictReader


class EloGame(BaseModel):
    idnumber_white: int
    fullname_white: str
    belrating_white: int
    idnumber_black: int
    fullname_black: str
    belrating_black: int
    result: Literal["1-0", "½-½", "0-1", "1-0 FF", "0-1 FF", "0-0 FF"]


linefeed = "\x0D\x0A"


def replaceAt(source, index, replace):
    """
    creates a copy of source where replace is filled in at index
    """
    return source[:index] + replace + source[index + len(replace) :]


def to_belgian_elo(records: List[EloGame]):
    """
    writing a list EloGame records in a Belgian ELO file
    """
    hlines = [
        "00A ### Interclubs",
        "00B 11 rondes",
        "00C Envoi des rondes 1 à 1",
        "00D Envoi par interclubs@frbe-kbsb-ksb.be",
        "00E Envoi par le club 998",
        "00F P={npart} R=11 S=24/09/2023 E=21/04/2024 +{won} ={drawn} -{lost}",
        "012 Belgian Interclubs 2023 - 2024 - Round 1",
        "022 Various locations in Belgian Clubs",
        "032 BEL",
        "042 2023-09-24",
        "052 2023-04-21",
        "062 {npart}",
        "102 Cornet, Luc",
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
    glines = []
    for g in records:
        if g.result not in ["1-0", "0-1", "½-½"]:
            continue
        # fetch player from signaletique
        whiteline = {
            "n": npart + 1,
            "name": g.fullname_white,
            "idn": g.idnumber_white,
            "nat": "BEL",  # correction needed
            "elo": g.belrating_white,
            "opponent": npart + 2,
            "color": "w",
        }
        blackline = {
            "n": npart + 2,
            "name": g.fullname_black,
            "idn": g.idnumber_black,
            "nat": "BEL",  # correction needed
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
    with open("test.txt", "w") as f:
        headerdict = {
            "ngames": ngames,
            "npart": npart,
            "won": won,
            "drawn": drawn,
            "lost": lost,
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


def read_csv_R1():
    games = []
    with open("data/eloR1.csv") as felo:
        csvelo = DictReader(felo)
        for g in csvelo:
            if g["result"] not in ["1-0", "0-1", "½-½"]:
                continue
            games.append(
                EloGame(
                    idnumber_white=g["idbel_white"],
                    fullname_white=g["fullname_white"],
                    belrating_white=g["belrating_white"] or 0,
                    idnumber_black=g["idbel_black"],
                    fullname_black=g["fullname_black"],
                    belrating_black=g["belrating_black"] or 0,
                    result=g["result"],
                )
            )
    return games


if __name__ == "__main__":
    games = read_csv_R1()
    to_belgian_elo(games)
