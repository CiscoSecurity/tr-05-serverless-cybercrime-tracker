from http import HTTPStatus
from pytest import fixture
from unittest import mock


def routes():
    yield '/health'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


def test_health_call_success(route, client):
    response = client.post(route)
    assert response.status_code == HTTPStatus.OK


@mock.patch('requests.get')
def test_health_call_error(response_mock, client):
    exp_response = {'errors': [
        {
            'code': 'invalid_health_check',
            'message': 'Invalid 3rd party API connect.',
        },
    ]}

    response_mock.return_value.ok = False

    response = client.post('/health')

    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == exp_response
