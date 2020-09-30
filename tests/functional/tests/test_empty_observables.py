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
    (('1.1.1.4', 'ip'),
     ('google.com', 'url')))


def test_positive_judgement(module_headers, observable, observable_type):
    """Perform testing for enrich observe observables endpoint to
    check that observable, on which CyberCrime Tracker doesn't have information,
    will return empty data

    ID: CCTRI-1707-07e734d0-1dcc-4f6a-b169-b8f1b4f53d3d

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
    )
    response_from_cybercrime_module = get_observables(
        response_from_all_modules['data'], MODULE_NAME)

    assert response_from_cybercrime_module['module'] == MODULE_NAME
    assert response_from_cybercrime_module['module_instance_id']
    assert response_from_cybercrime_module['module_type_id']

    assert response_from_cybercrime_module['data'] == {}
