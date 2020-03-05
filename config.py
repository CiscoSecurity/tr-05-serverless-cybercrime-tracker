import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', '')

    API_URL = "http://cybercrime-tracker.net/query.php?url={observable}"
    API_SOURCE_URL = "http://cybercrime-tracker.net/index.php?" \
                     "search={observable}"

    # Supported types with rules
    CCT_OBSERVABLE_TYPES = {
        'url': {'sep': '://'},
        'ip': {}
    }
