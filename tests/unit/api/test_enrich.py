from http import HTTPStatus

from pytest import fixture
from unittest import mock

from tests.unit.mock_for_tests import (
    CYBERCRIME_RESPONSE_MOCK,
    EXPECTED_DELIBERATE_RESPONSE,
    EXPECTED_OBSERVE_RESPONSE,
    EXPECTED_RESPONSE_500_ERROR,
    EXPECTED_RESPONSE_404_ERROR,
    CYBERCRIME_ERROR_RESPONSE_MOCK
)


def routes():
    yield '/deliberate/observables'
    yield '/observe/observables'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


@fixture(scope='function')
def cybercrime_api_request():
    with mock.patch('requests.get') as mock_request:
        yield mock_request


def cybercrime_api_response(*, ok, payload=None, status_error=None):
    mock_response = mock.MagicMock()

    mock_response.ok = ok

    if ok and not payload:
        payload = CYBERCRIME_RESPONSE_MOCK

    else:
        mock_response.status_code = status_error

    mock_response.json = lambda: payload

    return mock_response


@fixture(scope='module')
def invalid_json():
    return [{'type': 'unknown', 'value': ''}]


def test_enrich_call_with_invalid_json_failure(route, client, invalid_json):
    response = client.post(route, json=invalid_json)
    assert response.status_code == HTTPStatus.OK


@fixture(scope='module')
def valid_json():
    return [{'type': 'ip', 'value': '104.24.123.62'}]


@fixture(scope='module')
def valid_json_multiple():
    return [
        {'type': 'ip', 'value': '104.24.123.62'},
        {'type': 'ip', 'value': '0.0.0.0'},
    ]


def test_enrich_call_success(route, client, valid_json,
                             cybercrime_api_request):
    cybercrime_api_request.return_value = cybercrime_api_response(ok=True)

    response = client.post(route, json=valid_json)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()

    if route == '/observe/observables':
        verdicts = data['data']['verdicts']
        assert verdicts['docs'][0].pop('valid_time')

        judgements = data['data']['judgements']
        assert judgements['docs'][0].pop('id')
        assert judgements['docs'][0].pop('valid_time')

        assert data == EXPECTED_OBSERVE_RESPONSE

    if route == '/deliberate/observables':
        verdicts = data['data']['verdicts']
        assert verdicts['docs'][0].pop('valid_time')

        assert data == EXPECTED_DELIBERATE_RESPONSE


def test_enrich_error_with_data(route, client, valid_json_multiple,
                                cybercrime_api_request):
    cybercrime_api_request.side_effect = (
        cybercrime_api_response(ok=True),
        cybercrime_api_response(
            ok=False,
            payload=CYBERCRIME_ERROR_RESPONSE_MOCK,
            status_error=HTTPStatus.INTERNAL_SERVER_ERROR)
    )

    response = client.post(route, json=valid_json_multiple)

    assert response.status_code == HTTPStatus.OK

    data = response.get_json()

    if route == '/observe/observables':
        verdicts = data['data']['verdicts']
        assert verdicts['docs'][0].pop('valid_time')

        judgements = data['data']['judgements']
        assert judgements['docs'][0].pop('id')
        assert judgements['docs'][0].pop('valid_time')

        expected_response = {}
        expected_response.update(EXPECTED_OBSERVE_RESPONSE)
        expected_response.update(EXPECTED_RESPONSE_500_ERROR)

        assert data == expected_response

    if route == '/deliberate/observables':
        verdicts = data['data']['verdicts']
        assert verdicts['docs'][0].pop('valid_time')

        expected_response = {}
        expected_response.update(EXPECTED_DELIBERATE_RESPONSE)
        expected_response.update(EXPECTED_RESPONSE_500_ERROR)

        assert data == expected_response


def test_enrich_call_404(route, client, valid_json, cybercrime_api_request):
    cybercrime_api_request.return_value = cybercrime_api_response(
        ok=False,
        payload=CYBERCRIME_ERROR_RESPONSE_MOCK,
        status_error=HTTPStatus.NOT_FOUND
    )
    response = client.post(route, json=valid_json)
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_404_ERROR


def test_enrich_call_500(route, client, valid_json, cybercrime_api_request):
    cybercrime_api_request.return_value = cybercrime_api_response(
        ok=False,
        payload=CYBERCRIME_ERROR_RESPONSE_MOCK,
        status_error=HTTPStatus.INTERNAL_SERVER_ERROR
    )
    response = client.post(route, json=valid_json)
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_500_ERROR
