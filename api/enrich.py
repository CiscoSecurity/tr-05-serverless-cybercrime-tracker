from functools import partial
from uuid import uuid4

import requests
from datetime import datetime, timedelta
from flask import Blueprint, current_app

from api.schemas import ObservableSchema
from api.utils import get_json, get_jwt, jsonify_data, jsonify_errors

enrich_api = Blueprint('enrich', __name__)


get_observables = partial(get_json, schema=ObservableSchema(many=True))


def get_judgement(observable_value, observable_type,
                  disposition_name, valid_time):

    source_uri = current_app.config['API_SOURCE_URL']\
        .format(observable=observable_value)

    return {
        'id': f'transient:{uuid4()}',
        'observable': {'value': observable_value, 'type': observable_type},
        'disposition': 2,
        'disposition_name': disposition_name,
        'type': 'judgement',
        'schema_version': '1.0.14',
        'source': 'Cybercrime Tracker',
        'confidence': 'Low',
        'priority': 90,
        'severity': 'Medium',
        'valid_time': valid_time,
        'source_uri': source_uri
    }


def get_verdict(observable_value, observable_type,
                disposition_name, valid_time):

    return {
        'type': 'verdict',
        'observable': {'type': observable_type, 'value': observable_value},
        'disposition': 2,
        'disposition_name': disposition_name,
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


def format_docs(docs):
    return {'count': len(docs), 'docs': docs}


def call_api(observables):
    result = {}
    verdicts = []
    judgements = []

    for observable in observables:
        o_value = observable['value']
        o_type = observable['type'].lower()

        if current_app.config['CCT_OBSERVABLE_TYPES'][o_type].get('sep'):
            o_value = o_value.split(
                current_app.config['CCT_OBSERVABLE_TYPES'][o_type]['sep'])[-1]

        response = requests.get(
            current_app.config['API_URL'].format(observable=o_value)
        )
        if not response.ok:
            return jsonify_errors(response.json()['error'])

        verdict = response.json()['message']
        if verdict == "Unknown url":
            continue

        disposition_name, disposition_type = verdict.split(': ')

        start_time = datetime.utcnow()
        end_time = start_time + timedelta(weeks=1)
        valid_time = {
            'start_time': start_time.isoformat() + 'Z',
            'end_time': end_time.isoformat() + 'Z',
        }

        verdicts.append(
            get_verdict(o_value, o_type, disposition_name, valid_time))

        judgements.append(
            get_judgement(o_value, o_type, disposition_name, valid_time))

    if verdicts:
        result['verdicts'] = format_docs(verdicts)
    if judgements:
        result['judgements'] = format_docs(judgements)

    return result


@enrich_api.route('/deliberate/observables', methods=['POST'])
def deliberate_observables():
    observables = get_observables()
    observables = group_observables(observables)
    result = call_api(observables)

    return jsonify_data(result)


@enrich_api.route('/observe/observables', methods=['POST'])
def observe_observables():
    _ = get_jwt()
    _ = get_observables()
    return jsonify_data({})


@enrich_api.route('/refer/observables', methods=['POST'])
def refer_observables():
    _ = get_jwt()
    _ = get_observables()
    return jsonify_data([])
