from functools import partial
from uuid import uuid4
from http import HTTPStatus

import requests
from datetime import datetime, timedelta
from flask import Blueprint, current_app, jsonify, g

from api.schemas import ObservableSchema
from api.utils import get_json, jsonify_data, jsonify_errors, format_docs
from api.errors import (
    CybercrimeUnexpectedError,
    CybercrimetNotFoundError,
    CybercrimeUnavailableError,
    CybercrimeSSLError
)

enrich_api = Blueprint('enrich', __name__)


get_observables = partial(get_json, schema=ObservableSchema(many=True))


EXPECTED_RESPONSE_ERRORS = {
    HTTPStatus.NOT_FOUND: CybercrimetNotFoundError,
    HTTPStatus.SERVICE_UNAVAILABLE: CybercrimeUnavailableError,
    HTTPStatus.BAD_GATEWAY: CybercrimeUnavailableError,
    HTTPStatus.INTERNAL_SERVER_ERROR: CybercrimeUnavailableError,
    HTTPStatus.GATEWAY_TIMEOUT: CybercrimeUnavailableError
}


def get_judgement(observable_value, observable_type,
                  disposition, valid_time):

    source_uri = current_app.config['API_URL'] \
                 + current_app.config['API_SOURCE'].format(
        observable=observable_value)

    return {
        'id': f'transient:judgement-{uuid4()}',
        'observable': {'value': observable_value, 'type': observable_type},
        'disposition': disposition[0],
        'disposition_name': disposition[1],
        'type': 'judgement',
        'schema_version': '1.0.16',
        'source': 'CyberCrime Tracker',
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


def call_api(value):
    try:
        response = requests.get(
            f"{current_app.config['API_URL']}"
            f"{current_app.config['API_PATH'].format(observable=value)}",
            headers=current_app.config['CTR_HEADERS']
        )
    except requests.exceptions.SSLError as ex:
        raise CybercrimeSSLError(ex)
    if response.status_code in EXPECTED_RESPONSE_ERRORS:
        raise EXPECTED_RESPONSE_ERRORS[response.status_code]
    else:
        if not response.ok:
            raise CybercrimeUnexpectedError(response.json()['error'])
        return response.json()


def get_disposition(res):
    # Return tuple with (disposition, disposition_name)
    if res.startswith('Malicious'):
        return current_app.config['DISPOSITIONS']['malicious']


def key_error():
    return {
        'type': 'fatal',
        'code': 'key error',
        'message': 'The data structure of CyberCrime Tracker '
                   'has changed. The module is broken.'
    }


@enrich_api.route('/deliberate/observables', methods=['POST'])
def deliberate_observables():
    observables, error = get_observables()
    if error:
        return jsonify_errors(error)

    observables = group_observables(observables)

    if not observables:
        return jsonify_data({})

    data = {}
    g.verdicts = []
    g.errors = []

    observables = build_input_api(observables)

    try:
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

            g.verdicts.append(
                get_verdict(o_value, o_type, disposition_tuple, valid_time))
    except KeyError:
        g.errors.append(key_error())

    if g.verdicts:
        data['verdicts'] = format_docs(g.verdicts)

    result = {'data': data}
    if g.errors:
        result['errors'] = g.errors

    return jsonify(result)


@enrich_api.route('/observe/observables', methods=['POST'])
def observe_observables():
    observables, error = get_observables()
    if error:
        return jsonify_errors(error)

    observables = group_observables(observables)

    if not observables:
        return jsonify_data({})

    data = {}
    g.verdicts = []
    g.judgements = []
    g.errors = []

    observables = build_input_api(observables)

    try:
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

            g.verdicts.append(
                get_verdict(o_value, o_type, disposition_tuple, valid_time))

            g.judgements.append(
                get_judgement(o_value, o_type, disposition_tuple, valid_time))
    except KeyError:
        g.errors.append(key_error())

    if g.verdicts:
        data['verdicts'] = format_docs(g.verdicts)
    if g.judgements:
        data['judgements'] = format_docs(g.judgements)

    result = {'data': data}
    if g.errors:
        result['errors'] = g.errors

    return jsonify(result)


@enrich_api.route('/refer/observables', methods=['POST'])
def refer_observables():
    # Not supported or implemented
    return jsonify_data([])
