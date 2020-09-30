import pytest
from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_observe_observables
from tests.functional.tests.constants import MODULE_NAME


@pytest.mark.parametrize(
    'observable,observable_type',
    (('1.1.1.4', 'ip'),
     ('google.com', 'url'))
)
def test_positive_smoke_empty_observable(module_headers, observable,
                                         observable_type):
    """Perform testing for enrich observe observables endpoint to check that
     observable, on which CyberCrime Tracker doesn't have information, will
     return empty data

    ID: CCTRI-1707-07e734d0-1dcc-4f6a-b169-b8f1b4f53d3d

    Steps:
        1. Send request to enrich observe observables endpoint

    Expectedresults:
        1. Response body contains empty data dict from CyberCrime Tracker
         module

    Importance: Critical
    """
    observables = [{'type': observable_type, 'value': observable}]
    response_from_all_modules = enrich_observe_observables(
        payload=observables,
        **{'headers': module_headers}
    )

    cyber_crime_data = response_from_all_modules['data']

    response_from_cybercrime_module = get_observables(
        cyber_crime_data, MODULE_NAME)

    assert response_from_cybercrime_module['module'] == MODULE_NAME
    assert response_from_cybercrime_module['module_instance_id']
    assert response_from_cybercrime_module['module_type_id']

    assert response_from_cybercrime_module['data'] == {}
