import os

from version import VERSION


class Config:
    VERSION = VERSION

    SECRET_KEY = os.environ.get('SECRET_KEY', '')

    API_URL = "http://cybercrime-tracker.net/"
    API_PATH = "query.php?url={observable}"
    API_SOURCE = "index.php?search={observable}"

    # Supported types of verdict
    DISPOSITIONS = {
        'clean': (1, 'Clean'),
        'malicious': (2, 'Malicious'),
        'suspicious': (3, 'Suspicious'),
        'common': (4, 'Common'),
        'unknown': (5, 'Unknown')
    }


    # Supported types with rules
    CCT_OBSERVABLE_TYPES = {
        'url': {'sep': '://'},
        'ip': {}
    }
