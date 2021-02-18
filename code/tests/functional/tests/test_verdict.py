import pytest
from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables
from tests.functional.tests.constants import MODULE_NAME


@pytest.mark.parametrize(
    'observable,observable_type',
    (('5.79.66.145', 'ip'),
     ('greatsteal.kl.com.ua/dashboard/admin.php', 'url')))
def test_positive_verdict(module_headers, observable, observable_type):
    """Perform testing for enrich observe observables endpoint to get
    verdicts for observable from CyberCrime Tracker

    ID: CCTRI-813-700a7520-6454-485c-8daf-f876c6e57602

    Steps:
        1. Send request to enrich deliberate observable endpoint

    Expectedresults:
        1. Check that data in response body contains expected verdicts for
            observable from CyberCrime Tracker

    Importance: Critical
    """
    observables = [{'type': observable_type, 'value': observable}]
    response_from_all_modules = enrich_observe_observables(
        payload=observables,
        **{'headers': module_headers}
    )

    response_from_cybercrime_module = get_observables(
        response_from_all_modules, MODULE_NAME)

    assert response_from_cybercrime_module['module'] == MODULE_NAME
    assert response_from_cybercrime_module['module_instance_id']
    assert response_from_cybercrime_module['module_type_id']

    verdicts = response_from_cybercrime_module['data']['verdicts']
    assert verdicts['count'] == 1

    for verdict in verdicts['docs']:
        assert verdict['type'] == 'verdict'
        assert verdict['disposition'] == 2
        assert verdict['observable'] == observables[0]
        assert verdict['valid_time']['start_time']
        assert verdict['valid_time']['end_time']


def test_positive_verdict_for_unknown_observable(module_headers):
    """Perform testing for enrich observe observables endpoint to get
    verdicts for unknown observable from CyberCrime Tracker

    ID: CCTRI-813-2d309620-e9ee-4fce-874a-f9a5fd810f50

    Steps:
        1. Send request to enrich deliberate observable endpoint

    Expectedresults:
        1. Check that data in response body is empty for observable from
            CyberCrime Tracker

    Importance: Critical
    """
    observable = [{'type': 'ip', 'value': '123.223.23.13'}]

    response_from_all_modules = enrich_observe_observables(
        payload=observable,
        **{'headers': module_headers}
    )

    verdicts = get_observables(
        response_from_all_modules, MODULE_NAME)['data']
    assert verdicts == {}
