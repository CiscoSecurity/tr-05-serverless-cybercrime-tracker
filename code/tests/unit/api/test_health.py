from http import HTTPStatus
from requests.exceptions import SSLError

from pytest import fixture
from unittest import mock

from tests.unit.mock_for_tests import EXPECTED_RESPONSE_SSL_ERROR


def routes():
    yield '/health'


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
        payload = {}

    else:
        mock_response.status_code = status_error

    mock_response.json = lambda: payload

    return mock_response


def test_health_call_success(route, client, cybercrime_api_request):
    cybercrime_api_request.return_value = cybercrime_api_response(ok=True)

    response = client.post(route)

    assert response.status_code == HTTPStatus.OK


def test_health_call_error(route, client, cybercrime_api_request):
    cybercrime_api_request.return_value = cybercrime_api_response(
        ok=False,
        payload={'error': 'Cybercrime error message'})

    response = client.post(route)

    assert response.status_code == HTTPStatus.OK


def test_health_call_with_ssl_error(route, client, cybercrime_api_request):

    mock_exc = mock.MagicMock()
    mock_exc.reason.args.__getitem__().verify_message \
        = 'self signed certificate'
    cybercrime_api_request.side_effect = SSLError(mock_exc)

    response = client.post(route)

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == EXPECTED_RESPONSE_SSL_ERROR
