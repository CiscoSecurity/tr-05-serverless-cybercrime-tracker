from functools import partial
from uuid import uuid4

import requests
from datetime import datetime, timedelta
from flask import Blueprint, current_app

from api.schemas import ObservableSchema
from api.utils import get_json, jsonify_data, jsonify_errors

enrich_api = Blueprint('enrich', __name__)


get_observables = partial(get_json, schema=ObservableSchema(many=True))


def get_judgement(observable_value, observable_type,
                  disposition, valid_time):

    source_uri = current_app.config['API_URL'] \
                 + current_app.config['API_SOURCE'].format(
        observable=observable_value)

    return {
        'id': f'transient:{uuid4()}',
        'observable': {'value': observable_value, 'type': observable_type},
        'disposition': disposition[0],
        'disposition_name': disposition[1],
        'type': 'judgement',
        'schema_version': '1.0.16',
        'source': 'Cybercrime Tracker',
        'confidence': 'Low',
        'priority': 90,
        'severity': 'Medium',
        'valid_time': valid_time,
        'source_uri': source_uri
    }


def get_verdict(observable_value, observable_type,
                disposition, valid_time):

    return {
        'type': 'verdict',
        'observable': {'type': observable_type, 'value': observable_value},
        'disposition': disposition[0],
        'valid_time': valid_time
    }


def group_observables(relay_input):
    # Leave only unique observables

    result = []
    for observable in relay_input:
        o_value = observable['value']
        o_type = observable['type'].lower()

        # Get only supported types.
        if o_type in current_app.config['CCT_OBSERVABLE_TYPES']:
            obj = {'type': o_type, 'value': o_value}
            if obj in result:
                continue
            result.append(obj)

    return result


def build_input_api(observables):

    for observable in observables:
        o_value = observable['value']
        o_type = observable['type'].lower()

        if current_app.config['CCT_OBSERVABLE_TYPES'][o_type].get('sep'):
            o_value = o_value.split(
                current_app.config['CCT_OBSERVABLE_TYPES'][o_type]['sep'])[-1]
            observable['value'] = o_value
    return observables


def format_docs(docs):
    return {'count': len(docs), 'docs': docs}


def call_api(value):
    response = requests.get(
        f"{current_app.config['API_URL']}"
        f"{current_app.config['API_PATH'].format(observable=value)}",
        headers=current_app.config['CTR_HEADERS']
    )
    if not response.ok:
        return jsonify_errors(response.json()['error'])

    return response.json()


def get_disposition(res):
    # Return tuple with (disposition, disposition_name)
    if res.startswith('Malicious'):
        return current_app.config['DISPOSITIONS']['malicious']


@enrich_api.route('/deliberate/observables', methods=['POST'])
def deliberate_observables():
    observables, error = get_observables()
    if error:
        return jsonify_errors(error)

    observables = group_observables(observables)

    if not observables:
        return jsonify_data({})

    data = {}
    verdicts = []

    observables = build_input_api(observables)

    for observable in observables:
        o_value = observable['value']
        o_type = observable['type'].lower()

        response = call_api(o_value)

        disposition_tuple = get_disposition(response['message'])
        if not disposition_tuple:
            continue

        start_time = datetime.utcnow()
        end_time = start_time + timedelta(weeks=1)
        valid_time = {
            'start_time': start_time.isoformat() + 'Z',
            'end_time': end_time.isoformat() + 'Z',
        }

        verdicts.append(
            get_verdict(o_value, o_type, disposition_tuple, valid_time))

    if verdicts:
        data['verdicts'] = format_docs(verdicts)

    return jsonify_data(data)


@enrich_api.route('/observe/observables', methods=['POST'])
def observe_observables():
    observables, error = get_observables()
    if error:
        return jsonify_errors(error)

    observables = group_observables(observables)

    if not observables:
        return jsonify_data({})

    data = {}
    verdicts = []
    judgements = []

    observables = build_input_api(observables)

    for observable in observables:
        o_value = observable['value']
        o_type = observable['type'].lower()

        response = call_api(o_value)

        disposition_tuple = get_disposition(response['message'])
        if not disposition_tuple:
            continue

        start_time = datetime.utcnow()
        end_time = start_time + timedelta(weeks=1)
        valid_time = {
            'start_time': start_time.isoformat() + 'Z',
            'end_time': end_time.isoformat() + 'Z',
        }

        verdicts.append(
            get_verdict(o_value, o_type, disposition_tuple, valid_time))

        judgements.append(
            get_judgement(o_value, o_type, disposition_tuple, valid_time))

    if verdicts:
        data['verdicts'] = format_docs(verdicts)

    if judgements:
        data['judgements'] = format_docs(judgements)

    return jsonify_data(data)


@enrich_api.route('/refer/observables', methods=['POST'])
def refer_observables():
    # Not supported or implemented
    return jsonify_data([])
