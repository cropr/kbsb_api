import asyncio
from csv import DictReader

from reddevil.core import register_app, get_settings
from reddevil.db import connect_mongodb, close_mongodb, get_mongodb

register_app(settingsmodule="kbsb.settings")
settings = get_settings()

settings.SECRETS["mysql"] = {
    "name": "kbsb-mysql-infomaniak",
    "manager": "filejson",
}
settings.SECRETS["mongodb"] = {
    "name": "kbsb-mongodb-staging",
    "manager": "filejson",
}
settings.SECRETS_PATH = "/home/ruben/develop/secrets/kbsb"

import kbsb.service
from kbsb.interclub.md_interclub import InterclubPrevious
from kbsb.interclub.interclub import create_interclubprevious


class MongodbInterclubPreviousWriter:
    async def __aenter__(self):
        await connect_mongodb()
        return self

    async def __aexit__(self, *args):
        await close_mongodb()

    async def write(self, r: dict):
        ip = InterclubPrevious(
            idclub=int(r["club"]),
            teams1=int(r["teams1"]),
            teams2=int(r["teams2"]),
            teams3=int(r["teams3"]),
            teams4=int(r["teams4"]),
            teams5=int(r["teams5"]),
            name_long="",
            name_short="",
        )
        await create_interclubprevious(ip)


class InterclubPreviousCsvReader:
    def __enter__(self):
        self.fd = open("../share/data/interclubprevious.csv", "r")
        self.reader = DictReader(self.fd)
        return self.reader

    def __exit__(self, *args):
        self.fd.close()


async def main():
    async with MongodbInterclubPreviousWriter() as writer:
        db = await get_mongodb()
        await db.interclubprevious.drop()
        with InterclubPreviousCsvReader() as reader:
            for record in reader:
                print(record)
                await writer.write(record)


if __name__ == "__main__":
    asyncio.run(main())
