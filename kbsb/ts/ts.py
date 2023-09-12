import csv
from kbsb.interclubs.md_interclubs import DbICClub
from kbsb import ROOT_DIR


async def setup_series():
    # await empty_icclubs()
    with open(ROOT_DIR / "data" / "test_clubs.csv") as fcl:
        dr = csv.DictReader(fcl)
        for row in dr:
            await DbICClub.add(
                {
                    "idclub": row["idclub"],
                    "name": row["name"],
                    "teams": [],
                    "players": [],
                    "transfersout": [],
                }
            )
