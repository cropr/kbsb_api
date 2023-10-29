EMAIL = {
    "backend": "SMTP",
    "host": "maildev.decrop.net",
    "port": "1025",
    "sender": "noreply@frbe-kbsb-ksb.be",
    "blindcopy": "ruben.kbsb@gmail.com",
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
        "name": "kbsb-mongodb-schaken",
        "manager": "filejson",
    },
    "mysql": {
        # "name": "kbsb-mysql-local",
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
            "format": "%(levelname)s: %(name)s - %(message)s",
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

MODE = "staging"

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan,jangtvierkantmeklootnuut",
    "algorithm": "HS256",
    "nocheck": False,
}
