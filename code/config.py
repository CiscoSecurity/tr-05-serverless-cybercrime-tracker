import json


class Config:
    settings = json.load(open('container_settings.json', 'r'))
    VERSION = settings['VERSION']

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

    CTR_HEADERS = {
        'User-Agent': ('SecureX Threat Response Integrations '
                       '<tr-integrations-support@cisco.com>')
    }
