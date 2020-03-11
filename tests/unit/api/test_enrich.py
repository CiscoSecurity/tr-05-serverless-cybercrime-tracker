from http import HTTPStatus

from pytest import fixture


def routes():
    yield '/deliberate/observables'


@fixture(scope='module', params=routes(), ids=lambda route: f'POST {route}')
def route(request):
    return request.param


@fixture(scope='module')
def valid_json():
    return [{'type': 'ip', 'value': '104.24.123.62'}]


def test_enrich_call_success(route, client, valid_json):
    response = client.post(route, json=valid_json)
    assert response.status_code == HTTPStatus.OK
    assert \
        response.get_json()['data']['verdicts']['docs'][0]['disposition'] == 2
