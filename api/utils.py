import json
from flask import request, jsonify


def get_json(schema):
    """
    Parse the incoming request's data as JSON.
    Validate it against the specified schema.
    """

    data = request.get_json(force=True, silent=True, cache=False)

    error = schema.validate(data) or None

    if error:
        data = None
        error = {
            'code': 'invalid_payload',
            'message': f'Invalid JSON payload received. {json.dumps(error)}.',
        }

    return data, error


def jsonify_data(data):
    return jsonify({'data': data})


def jsonify_errors(error):
    # According to the official documentation, an error here means that the
    # corresponding TR module is in an incorrect state and needs to be
    # reconfigured:
    # https://visibility.amp.cisco.com/help/alerts-errors-warnings.
    error['type'] = 'fatal'
    error['code'] = error.pop('code').lower().replace('_', ' ')

    return jsonify({'errors': [error]})
