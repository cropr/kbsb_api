from csv import DictReader
from pymongo import MongoClient
from reddevil.core import register_app, get_settings
from reddevil.core.secrets import get_secret
from uuid import uuid4
import requests

series = []


def setup_mongodb():
    # fake app registration
    register_app(None, "kbsb.settings", None)
    settings = get_settings()
    mongoparams = get_secret("mongodb")
    cl = MongoClient(mongoparams["url"])
    db = cl[mongoparams["db"]]
    return db


def createicclub(db):
    for c in db.club.find({"enabled": True}):
        teams = []
        idclub = c["idclub"]
        series = [s for s in db.interclub2324series.find({"teams.idclub": idclub})]
        if series:
            for s in series:
                for t in s["teams"]:
                    if t["idclub"] == idclub:
                        teams.append(
                            {
                                "division": s["division"],
                                "titular": [],
                                "idclub": idclub,
                                "index": s["index"],
                                "name": t["name"],
                                "pairingnumber": t["pairingnumber"],
                                "playersplayed": [],
                            }
                        )
            aclubname = teams[0]["name"].split()
            clubname = " ".join(aclubname[:-1])
            print(f"inserting {idclub} enrolled")
            db.interclub2324club.insert_one(
                {
                    "name": clubname,
                    "_id": str(uuid4()),
                    "idclub": idclub,
                    "teams": teams,
                    "players": [],
                    "enrolled": True,
                }
            )
        else:
            print(f"inserting {idclub} not enrolled")
            db.interclub2324club.insert_one(
                {
                    "name": c["name_short"],
                    "_id": str(uuid4()),
                    "idclub": idclub,
                    "teams": [],
                    "players": [],
                    "enrolled": False,
                }
            )
            continue


if __name__ == "__main__":
    db = setup_mongodb()
    createicclub(db)
