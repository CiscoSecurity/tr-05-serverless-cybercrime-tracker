CYBERCRIME_RESPONSE_MOCK = {
    'success': True,
    'message': 'Malicious: Keitaro'
}

CYBERCRIME_ERROR_RESPONSE_MOCK = {
    'error': 'Server unavailable'
}


EXPECTED_DELIBERATE_RESPONSE = {
    'data': {
        'verdicts': {
            'count': 1,
            'docs': [
                {
                    'disposition': 2,
                    'observable': {
                        'type': 'ip',
                        'value': '104.24.123.62'
                    },
                    'type': 'verdict'
                }
            ]
        }
    }
}

EXPECTED_OBSERVE_RESPONSE = {
    'data': {
        'judgements': {
            'count': 1,
            'docs': [
                {
                    'confidence': 'Low',
                    'disposition': 2,
                    'disposition_name': 'Malicious',
                    'observable': {
                        'type': 'ip',
                        'value': '104.24.123.62'
                    },
                    'priority': 90,
                    'schema_version': '1.0.16',
                    'severity': 'Medium',
                    'source': 'Cybercrime Tracker',
                    'source_uri': 'http://cybercrime-tracker.net/'
                                  'index.php?search=104.24.123.62',
                    'type': 'judgement'
                }
            ]
        },
        'verdicts': {
            'count': 1,
            'docs': [
                {
                    'disposition': 2,
                    'observable': {
                        'type': 'ip',
                        'value': '104.24.123.62'
                    },
                    'type': 'verdict'
                }
            ]
        }
    }
}

EXPECTED_RESPONSE_500_ERROR = {
    'errors': [
        {
            'code': 'service unavailable',
            'message': 'The CyberCrime is unavailable. Please, try again '
                       'later.',
            'type': 'fatal'
        }
    ]
}

EXPECTED_RESPONSE_404_ERROR = {
    'errors': [
        {
            'code': 'not found',
            'message': 'The CyberCrime not found',
            'type': 'fatal'
        }
    ]
}
