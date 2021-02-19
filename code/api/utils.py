import json
from flask import request, jsonify, g


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


def format_docs(docs):
    return {'count': len(docs), 'docs': docs}


def jsonify_data(data):
    return jsonify({'data': data})


def jsonify_errors(error):
    data = {
        'errors': [error],
        'data': {}
    }

    if g.get('verdicts'):
        data['data'].update({'verdicts': format_docs(g.verdicts)})

    if g.get('judgements'):
        data['data'].update({'judgements': format_docs(g.judgements)})

    if g.get('errors'):
        data['errors'].extend(g.errors)

    if not data['data']:
        data.pop('data')

    return jsonify(data)
