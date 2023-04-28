# copyright Ruben Decrop 2012 - 2022

import os
import yaml
import logging

API_BASE_URL = "/api"

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
    "bucket": os.environ.get("FILESTORE_BUCKET", "webite-kbsb-prod.appspot.com"),
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


MODE = "production"

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
SECRETS_PATH = ""

# relatively to backend path
TEMPLATES_PATH = os.environ.get("TEMPLATES_PATH", "./kbsb/templates")

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan,jangtvierkantmeklootnuut",
    "algorithm": "HS256",
    "nocheck": False,
}

try:
    from local_settings import *

    ls = "local settings loaded"
except ImportError:
    ls = "No local settings found"


if COLORLOG:
    LOG_CONFIG["handlers"]["console"]["formatter"] = "color"
if DEBUG:
    LOG_CONFIG["handlers"]["console"]["level"] = "DEBUG"
    LOG_CONFIG["loggers"]["kbsb"]["level"] = "DEBUG"
    LOG_CONFIG["loggers"]["reddevil"]["level"] = "DEBUG"

with open(BOARDROLES_PATH) as file:
    BOARDROLES = yaml.load(file, Loader=yaml.FullLoader)["boardroles"]
