import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', '')

    API_URL = "http://cybercrime-tracker.net/"
    API_PATH = "query.php?url={observable}"
    API_SOURCE = "index.php?search={observable}"

    # Supported types of verdict
    DISPOSITIONS = {
        'Malicious': 2
    }

    # Supported types with rules
    CCT_OBSERVABLE_TYPES = {
        'url': {'sep': '://'},
        'ip': {}
    }
