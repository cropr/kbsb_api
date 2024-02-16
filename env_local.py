# settings to run everything on the deployment machine
#   - we need to have maildev running locally in docker
#   - we are still reading from the Google Cloud Bucket for the common files
#   - mongodb is running in local odcker container
#   - mysql is reffring to the Infomaniak server

EMAIL = {
    "backend": "SMTP",
    "host": "localhost",
    "port": "1025",
    "sender": "ruben.decrop@frbe-kbsb-ksb.be",
}

FILESTORE = {
    "manager": "google",
    "bucket": "website-kbsb-prod.appspot.com",
}

GOOGLE_CLIENT_ID = (
    "658290412135-v6ah768urdv83dn76ra4mkiovdalal2k.apps.googleusercontent.com",
)

SECRETS = {
    "mongodb": {
        "name": "kbsb-mongodb-local",
        "manager": "filejson",
    },
    "mysql": {
        "name": "kbsb-mysql-infomaniak",
        "manager": "filejson",
    },
    "gdrive": {
        "name": "kbsb-gdrive-staging",
        "manager": "filejson",
    },
}

LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(asctime)s - %(name)s - %(message)s",
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
            "formatter": "color",
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "kbsb": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "reddevil": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
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

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan,jangtvierkantmeklootnuut",
    "algorithm": "HS256",
    "nocheck": False,
}
