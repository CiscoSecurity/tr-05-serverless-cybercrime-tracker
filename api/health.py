import requests
from flask import Blueprint, current_app

from api.utils import jsonify_errors, jsonify_data
from api.errors import CybercrimeSSLError

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

    error = {
        'code': 'invalid_health_check',
        'message': 'Invalid 3rd party API connect.',
    }
    return jsonify_errors(error)
