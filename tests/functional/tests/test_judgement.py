import pytest
from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables
from tests.functional.tests.constants import (
    MODULE_NAME,
    CYBER_CRIME_URL,
    CTR_ENTITIES_LIMIT
)


@pytest.mark.parametrize(
    'observable,observable_type',
    (('5.79.66.145', 'ip'),
     ('greatsteal.kl.com.ua/dashboard/admin.php', 'url')))
def test_positive_judgement(module_headers, observable, observable_type):
    """Perform testing for enrich observe observables endpoint to get
    judgement for observable from CyberCrime Tracker

    ID: CCTRI-844-4e53f335-d803-4c3e-a582-af02c94cf727

    Steps:
        1. Send request to enrich deliberate observable endpoint

    Expectedresults:
        1. Check that data in response body contains expected judgement for
            observable from CyberCrime Tracker

    Importance: Critical
    """
    observables = [{'type': observable_type, 'value': observable}]

    response_from_all_modules = enrich_observe_observables(
        payload=observables,
        **{'headers': module_headers}
    )['data']
    response_from_cybercrime_module = get_observables(
        response_from_all_modules, MODULE_NAME)

    assert response_from_cybercrime_module['module'] == MODULE_NAME
    assert response_from_cybercrime_module['module_instance_id']
    assert response_from_cybercrime_module['module_type_id']

    judgements = response_from_cybercrime_module['data']['judgements']
    assert len(judgements['docs']) > 0

    for judgement in judgements['docs']:
        assert judgement['valid_time']['start_time']
        assert judgement['valid_time']['end_time']
        assert judgement['type'] == 'judgement'
        assert judgement['schema_version']
        assert judgement['source'] == MODULE_NAME
        assert judgement['disposition'] == 2
        assert judgement['observable'] == observables[0]
        assert judgement['source_uri'] == (f'{CYBER_CRIME_URL}'
                                           f'/index.php?search={observable}')
        assert judgement['disposition_name']
        assert judgement['priority'] == 90
        assert judgement['id'].startswith('transient:judgement-')
        assert judgement['severity'] == 'Medium'
        assert judgement['confidence'] == 'Low'

    assert judgements['count'] == len(judgements['docs']) <= CTR_ENTITIES_LIMIT
