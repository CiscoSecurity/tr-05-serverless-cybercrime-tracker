import os

from version import VERSION


class Config:
    VERSION = VERSION

    SECRET_KEY = os.environ.get('SECRET_KEY', '')

    API_URL = "http://cybercrime-tracker.net"
    API_PATH = "query.php?url={observable}"
    API_SOURCE = "index.php?search={observable}"

    # Supported types of verdict
    DISPOSITIONS = {
        'Clean': 1,
        'Malicious': 2,
        'Suspicious': 3,
        'Common': 4,
        'Unknown': 5
    }

    # Supported types with rules
    CCT_OBSERVABLE_TYPES = {
        'url': {'sep': '://'},
        'ip': {}
    }
