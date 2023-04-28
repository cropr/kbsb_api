EMAIL = {
    "backend": "SMTP",
    "host": "localhost",
    "port": "1025",
    "sender": "ruben.decrop@frbe-kbsb-ksb.be",
}

FILESTORE = {
    "manager": "local",
    "basedir": "../filestore",
}

GOOGLE_CLIENT_ID = (
    "658290412135-v6ah768urdv83dn76ra4mkiovdalal2k.apps.googleusercontent.com",
    # "1027257161616-9n0mh0sl9jifkrkbqb1cqiu8554rgtrb.apps.googleusercontent.com"
)

SECRETS = {
    "mongodb": {
        "name": "kbsb-mongodb-prod",
        "manager": "filejson",
    },
    "mysql": {
        "name": "kbsb-mysql-local",
        "manager": "filejson",
    },
    "gdrive": {
        "name": "kbsb-gdrive-test",
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

MODE = "local"
