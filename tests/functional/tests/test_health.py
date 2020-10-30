from ctrlibrary.core.utils import get_observables
from ctrlibrary.threatresponse.enrich import enrich_post_health
from tests.functional.tests.constants import MODULE_NAME


def test_positive_smoke_enrich_health(module_headers):
    """Perform testing for enrich health endpoint to check status of CyberCrime
    Tracker module

    ID: CCTRI-844-2774693e-f297-11ea-adc1-0242ac120002

    Steps:
        1. Send request to enrich health endpoint

    Expectedresults:
        1. Check that data in response body contains status Ok from CyberCrime
        Tracker module

    Importance: Critical
    """
    response_from_all_modules = enrich_post_health(
        **{'headers': module_headers}
    )

    response_from_cybercrime = get_observables(response_from_all_modules,
                                               MODULE_NAME)

    assert response_from_cybercrime['module'] == MODULE_NAME
    assert response_from_cybercrime['module_instance_id']
    assert response_from_cybercrime['module_type_id']

    assert response_from_cybercrime['data'] == {'status': 'ok'}
