from flask import request, jsonify
from werkzeug.exceptions import BadRequest


def get_json(schema):
    """
    Parse the incoming request's data as JSON.
    Validate it against the specified schema.

    Note. This function is just an example of how one can read and check
    anything before passing to an API endpoint, and thus it may be modified in
    any way, replaced by another function, or even removed from the module.
    """

    data = request.get_json(force=True, silent=True, cache=False)

    message = schema.validate(data)

    if message:
        raise BadRequest(message)

    return data


def jsonify_data(data):
    return jsonify({'data': data})


def jsonify_errors(error):
    # Make the actual error payload compatible with the expected TR error
    # payload in order to fix the following types of possible UI alerts, e.g.:
    # :code (not (instance? java.lang.String 40x)),
    # :details disallowed-key,
    # :status disallowed-key,
    # etc.
    error['code'] = error.pop('status').lower()
    error.pop('details', None)

    # According to the official documentation, an error here means that the
    # corresponding TR module is in an incorrect state and needs to be
    # reconfigured:
    # https://visibility.amp.cisco.com/help/alerts-errors-warnings.
    error['type'] = 'fatal'

    return jsonify({'errors': [error]})
