from reddevil.core.dbbase import DbBase
from reddevil.core.mongodb import get_mongodb


class DbICSeries(DbBase):
    COLLECTION = "interclub2324series"
    DOCUMENTTYPE = "InterclubSeries"
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICVenue(DbBase):
    COLLECTION = "interclub2324venues"
    DOCUMENTTYPE = "InterclubVenues"
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


class DbICClub(DbBase):
    COLLECTION = "interclub2324club"
    DOCUMENTTYPE = "ICClub"
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


class DbICEnrollment(DbBase):
    COLLECTION = "interclub2324enrollment"
    DOCUMENTTYPE = "InterclubEnrollment"
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


async def empty_icclubs():
    # TDOD
    pass
