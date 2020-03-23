import requests
from flask import Blueprint, current_app

from api.utils import jsonify_errors, jsonify_data

health_api = Blueprint('health', __name__)


@health_api.route('/health', methods=['POST'])
def health():
    response = requests.get(current_app.config['API_URL'])

    if response.ok:
        return jsonify_data({'status': 'ok'})

    error = {
        'code': 'invalid_health_check',
        'message': f'Invalid 3rd party API connect.',
    }
    return jsonify_errors(error)
