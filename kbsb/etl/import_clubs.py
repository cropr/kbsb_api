import asyncio
import logging
from csv import writer
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from reddevil.core import register_app, get_settings
from reddevil.db import connect_mongodb, close_mongodb, get_mongodb
from kbsb.club import (
    ClubMember,
    ClubRole,
    ClubIn,
    create_club,
    Visibility,
)
from kbsb.oldkbsb import OldClub_sql, OldMember_sql, old_role_mapping
from kbsb.core.db import mysql_engine

app = FastAPI(
    title="FRBE-KBSB-KSB",
    description="Website Belgian Chess federation FRBE KBSB KSB",
    version="0",
)
register_app(app=app, settingsmodule="kbsb.settings")
settings = get_settings()
dbsession = sessionmaker(mysql_engine())()

logger = logging.getLogger("kbsb")


class MongodbClubWriter:
    """
    async writer of club Mongodb collection
    """

    async def __aenter__(self):
        await connect_mongodb()
        return self

    async def __aexit__(self, *args):
        await close_mongodb()

    async def write(self, p: OldClub_sql):
        email = p.email
        if email:
            email = email.replace("[at]", "@")
        staff = []
        boardmembers = {}
        query = dbsession.query(OldMember_sql)
        for f in [
            "presidentmat",
            "vicemat",
            "tresoriermat",
            "secretairemat",
            "tournoimat",
            "jeunessemat",
            "interclubmat",
        ]:
            if id := getattr(p, f, 0):
                staff.append(id)
                m = query.filter_by(idnumber=id).one_or_none()
                if m:
                    cm = ClubMember(
                        first_name=m.first_name,
                        last_name=m.last_name,
                        email=m.email,
                        email_visibility=Visibility.club,
                        idnumber=id,
                        mobile=m.mobile,
                        mobile_visibility=Visibility.club,
                    )
                    logger.debug(f"cm {cm}")
                    boardmembers[old_role_mapping[f]] = cm
        clubroles = [
            ClubRole(
                nature="ClubAdmin",
                memberlist=staff,
            ),
            ClubRole(
                nature="InterclubAdmin",
                memberlist=staff,
            ),
        ]
        c = ClubIn(
            address=p.siegesocial,
            bankaccount_name=p.bquetitulaire,
            bankaccount_iban=p.bquecompter,
            bankaccount_bic=p.bquebic,
            boardmembers=boardmembers,
            clubroles=clubroles,
            email_admin="",
            email_finance="",
            email_interclub="",
            email_main=email,
            enabled=True,
            federation=p.federation[0],
            idclub=p.club,
            league=p.ligue,
            name_long=p.intitule,
            name_short=p.abbrev,
            openinghours=None,
            venue=f"{p.local}\n{p.adresse}\n{p.codepostal} {p.localite}",
            website=p.website,
        )
        await create_club(c)


class MysqlClubReader:
    def __iter__(self):
        self.query = dbsession.scalars(select(OldClub_sql))
        return self.query

    def __next__(self):
        for r in self.query:
            yield r


async def main():
    async with MongodbClubWriter() as writer:
        db = await get_mongodb()
        await db.club.drop()
        for i, record in enumerate(MysqlClubReader()):
            logger.info(f"club {record.club}")
            await writer.write(record)


if __name__ == "__main__":
    asyncio.run(main())
