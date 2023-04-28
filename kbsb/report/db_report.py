# copyright Ruben Decrop 2012 - 2022
# copyright Chessdevil Consulting BVBA 2015 - 2022

# all database request come in here, but we do not use dataclasess
# if needed we define extra models an do marshalling functions at the service level
# All _id are translatesd to stringified id on output
# All functions expect stringified id as input

import logging
from datetime import datetime, date, timezone
from typing import Dict, List, Any, Optional
from reddevil.core import DbBase

log = logging.getLogger(__name__)


class DbFile(DbBase):
    COLLECTION = "rd_file"
    DOCUMENTTYPE = "File"
    SIMPLEFIELDS = [
        "archived",
        "created_by",
        "filelength",
        "locale",
        "mimetype",
        "name",
        "topic",
        "topicdate",
        "url",
        "_creationtime",
        "_modificationtime",
    ]
    VERSION = 2
    IDGENERATOR = "uuid"
