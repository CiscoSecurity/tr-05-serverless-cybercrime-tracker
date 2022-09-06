import requests
from flask import Blueprint, current_app

from api.enrich import EXPECTED_RESPONSE_ERRORS
from api.utils import jsonify_data
from api.errors import CybercrimeSSLError, CybercrimeUnexpectedError

health_api = Blueprint('health', __name__)


@health_api.route('/health', methods=['POST'])
def health():
    try:
        response = requests.get(current_app.config['API_URL'],
                                headers=current_app.config['CTR_HEADERS'])
    except requests.exceptions.SSLError as ex:
        raise CybercrimeSSLError(ex)

    if response.ok:
        return jsonify_data({'status': 'ok'})
    elif response.status_code in EXPECTED_RESPONSE_ERRORS:
        raise EXPECTED_RESPONSE_ERRORS[response.status_code]
    else:
        raise CybercrimeUnexpectedError(response.json())
