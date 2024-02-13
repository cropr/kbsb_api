# copyright Ruben Decrop 2012 - 2022

import os
import yaml
import logging

logger = logging.getLogger(__name__)

API_BASE_URL = "/api"

API_KEY = os.environ.get("API_KEY", "dikkevette")

BOOKS_CC = "ruben@kosk.be"
BOARDROLES_PATH = os.environ.get("BOARDROLES", "./boardroles.yaml")
COLORLOG = False
DEBUG = os.environ.get("DEBUG_KBSB", False)

EMAIL = {
    "backend": "GMAIL",
    "serviceaccountfile": "kbsb-gmail.json",
    "sender": "ruben.decrop@frbe-kbsb-ksb.be",
    "account": "ruben.decrop@frbe-kbsb-ksb.be",
    "blindcopy": "ruben.kbsb@gmail.com",
}

EXTRASALT = "Zugzwang"

FILESTORE = {
    "manager": "google",
    "bucket": os.environ.get("FILESTORE_BUCKET", "website-kbsb-prod.appspot.com"),
}

JWT_ALGORITHM = "HS256"
JWT_SECRET = "levedetorrevanostende"

LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {
            "formaCOMMONt": "%(levelname)s: %(name)s - %(message)s",
        },
        "color": {
            "format": "%(log_color)s%(levelname)s%(reset)s: %(asctime)s %(bold)s%(name)s%(reset)s %(message)s",
            "()": "reddevil.core.colorlogfactory.c_factory",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "kbsb": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "reddevil": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "fastapi": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# login details
GOOGLE_CLIENT_ID = os.environ.get(
    "GOOGLE_CLIENT_ID",
    "658290412135-v6ah768urdv83dn76ra4mkiovdalal2k.apps.googleusercontent.com",
)
GOOGLE_LOGIN_DOMAINS = ["frbe-kbsb-ksb.be"]
GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID", "")
GOOGLEDRIVE_TRANSLATIONID = "1sLMHvI9nM_EmT3kqqxQRz59b42zGjfbOdlzoFEStbD0"


INTERCLUBS_CC_EMAIL = "interclubs@frbe-kbsb-ksb.be"

KBSB_MODE = os.environ.get("KBSB_MODE", "production")

#
SECRETS = {
    "mongodb": {
        "name": "kbsb-mongodb",
        "manager": "googlejson",
    },
    "mysql": {
        "name": "kbsb-mysql",
        "manager": "googlejson",
    },
    "gmail": {
        "name": "kbsb-gmail",
        "manager": "googlejson",
    },
}
SECRETS_PATH = os.environ.get("SECRETS_PATH", "")

# relatively to backend path
TEMPLATES_PATH = os.environ.get("TEMPLATES_PATH", "./kbsb/templates")

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan,jangtvierkantmeklootnuut",
    "algorithm": "HS256",
    "nocheck": False,
}

MEMBERDB = "oldmysql"

ls = None

if KBSB_MODE == "local":
    ls = "importing local settings"
    from env_local import *


if KBSB_MODE == "prodtest":
    ls = "importing prodtest settings"
    from env_prodtest import *


if KBSB_MODE == "testing":
    ls = "importing testing settings"
    from env_testing import *


if COLORLOG:
    LOG_CONFIG["handlers"]["console"]["formatter"] = "color"
if DEBUG:
    LOG_CONFIG["handlers"]["console"]["level"] = "DEBUG"
    LOG_CONFIG["loggers"]["kbsb"]["level"] = "DEBUG"
    LOG_CONFIG["loggers"]["reddevil"]["level"] = "DEBUG"

if ls:
    logger.info(ls)

# with open(BOARDROLES_PATH) as file:
#     BOARDROLES = yaml.load(file, Loader=yaml.FullLoader)["boardroles"]
