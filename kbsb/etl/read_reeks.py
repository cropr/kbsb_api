from csv import DictReader
from pymongo import MongoClient
from reddevil.core import register_app, get_settings
from reddevil.core.secrets import get_secret
from uuid import uuid4

series = []


def setup_mongodb():
    # fake app registration
    register_app(None, "kbsb.settings", None)
    settings = get_settings()
    mongoparams = get_secret("mongodb")
    cl = MongoClient(mongoparams["url"])
    db = cl[mongoparams["db"]]
    return db


def readcsvfile():
    with open("data/reeks_v2.csv") as csvfile:
        csvseries = DictReader(csvfile)
        for line in csvseries:
            if not line["Nr"]:
                # a new line of series
                series1 = {}
                series2 = {}
                series3 = {}
                series4 = {}
                teams1 = []
                teams2 = []
                teams3 = []
                teams4 = []
                namediv1 = line["Club1"].split()
                namediv2 = line["Club2"].split()
                namediv3 = line["Club3"].split()
                namediv4 = line["Club4"].split()
                division1 = int(namediv1[1][0:1])
                division2 = int(namediv2[1][0:1]) if namediv2 else None
                division3 = int(namediv3[1][0:1])
                division4 = int(namediv4[1][0:1])
                index1 = namediv1[1][1:]
                index2 = namediv2[1][1:] if namediv2 else None
                index3 = namediv3[1][1:]
                index4 = namediv4[1][1:]
            else:
                club1 = line["Club1"].split()
                club2 = line["Club2"].split() if namediv2 else None
                club3 = line["Club3"].split()
                club4 = line["Club4"].split()
                idclub1 = int(club1[0])
                idclub2 = int(club2[0]) if namediv2 else None
                idclub3 = int(club3[0])
                idclub4 = int(club4[0])
                name1 = " ".join(club1[1:])
                name2 = " ".join(club2[1:]) if namediv2 else None
                name3 = " ".join(club3[1:])
                name4 = " ".join(club4[1:])
                teams1.append({"idclub": idclub1, "name": name1})
                if namediv2:
                    teams2.append({"idclub": idclub2, "name": name2})
                teams3.append({"idclub": idclub3, "name": name3})
                teams4.append({"idclub": idclub4, "name": name4})
                if line["Nr"] == "12":
                    series.append(
                        {
                            "division": division1,
                            "index": index1,
                            "teams": teams1,
                        }
                    )
                    if namediv2:
                        series.append(
                            {
                                "division": division2,
                                "index": index2,
                                "teams": teams2,
                            }
                        )
                    series.append(
                        {
                            "division": division3,
                            "index": index3,
                            "teams": teams3,
                        }
                    )
                    series.append(
                        {
                            "division": division4,
                            "index": index4,
                            "teams": teams4,
                        }
                    )


def printseries():
    for s in series:
        print(f"Div {s['division']}{s['index']}")
        for i, t in enumerate(s["teams"]):
            print(f"{i+1}:  {t['idclub']} {t['name']}")


def createcompetition(db):
    for s in series:
        teams = [
            {
                "division": s["division"],
                "titular": [],
                "idclub": t["idclub"],
                "index": s["index"],
                "name": t["name"],
                "pairingnumber": ix + 1,
                "playersplayed": [],
            }
            for ix, t in enumerate(s["teams"])
        ]
        db.interclub2324series.insert_one(
            {
                "_id": str(uuid4()),
                "division": s["division"],
                "index": s["index"],
                "teams": teams,
            }
        )


if __name__ == "__main__":
    readcsvfile()
    db = setup_mongodb()
    createcompetition(db)
