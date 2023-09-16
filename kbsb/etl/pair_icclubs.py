from csv import DictReader
from pymongo import MongoClient
from reddevil.core import register_app, get_settings
from reddevil.core.secrets import get_secret
from uuid import uuid4
from kbsb.interclubs.md_interclubs import ICEncounter, ICRound

pairingstable = {
    1: ((1, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)),
    2: ((12, 7), (8, 6), (9, 5), (10, 4), (11, 3), (1, 2)),
    3: ((2, 12), (3, 1), (4, 11), (5, 10), (6, 9), (7, 8)),
    4: ((12, 8), (9, 7), (10, 6), (11, 5), (1, 4), (2, 3)),
    5: ((3, 12), (4, 2), (5, 1), (6, 11), (7, 10), (8, 9)),
    6: ((12, 9), (10, 8), (11, 7), (1, 6), (2, 5), (3, 4)),
    7: ((4, 12), (5, 3), (6, 2), (7, 1), (8, 11), (9, 10)),
    8: ((12, 10), (11, 9), (1, 8), (2, 7), (3, 6), (4, 5)),
    9: ((5, 12), (6, 4), (7, 3), (8, 2), (9, 1), (10, 11)),
    10: ((12, 11), (1, 10), (2, 9), (3, 8), (4, 7), (5, 6)),
    11: ((6, 12), (7, 5), (8, 4), (9, 3), (10, 2), (11, 1)),
}


def setup_mongodb():
    # fake app registration
    register_app(None, "kbsb.settings", None)
    settings = get_settings()
    mongoparams = get_secret("mongodb")
    cl = MongoClient(mongoparams["url"])
    db = cl[mongoparams["db"]]
    return db


def pairclubs(db):
    for s in db.interclub2324series.find():
        teams = {t["pairingnumber"]: t for t in s["teams"]}
        rounds = []
        for r, pairings in pairingstable.items():
            enc = []
            for p in pairings:
                enc.add(
                    ICEncounter(
                        icclub_home=teams[p[0]]["idclub"],
                        icclub_visit=teams[p[1]]["idclub"],
                    )
                )
            rounds.append(
                ICRound(
                    round=r,
                    encounters=enc,
                )
            )
        db.interclub2324club.update_one(
            {"_id": s["_id"]}, {"$set": {"rounds": rounds.model_dump}}
        )


if __name__ == "__main__":
    db = setup_mongodb()
    pairclubs(db)
    print("done")
