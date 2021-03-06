INVALID_ARGUMENT = 'invalid argument'
UNKNOWN = 'unknown'
NOT_FOUND = 'not found'
SERVER_UNAVAILABLE = 'service unavailable'
HEALTH_CHECK_ERROR = 'health check failed'


class TRError(Exception):
    def __init__(self, code, message, type_='fatal'):
        super().__init__()
        self.code = code or UNKNOWN
        self.message = message or 'Something went wrong.'
        self.type_ = type_

    @property
    def json(self):
        return {'type': self.type_,
                'code': self.code,
                'message': self.message}


class CybercrimetNotFoundError(TRError):
    def __init__(self):

        super().__init__(
            code=NOT_FOUND,
            message='The CyberCrime not found'
        )


class CybercrimeUnexpectedError(TRError):
    def __init__(self, payload):
        error_payload = payload.get('error', 'unexpected error')

        super().__init__(
            code=UNKNOWN,
            message=error_payload
        )


class CybercrimeUnavailableError(TRError):
    def __init__(self):

        super().__init__(
            SERVER_UNAVAILABLE,
            'The CyberCrime is unavailable. Please, try again later.'
        )


class BadRequestError(TRError):
    def __init__(self, error_message):
        super().__init__(
            INVALID_ARGUMENT,
            error_message
        )


class CybercrimeSSLError(TRError):
    def __init__(self, error):
        error = error.args[0].reason.args[0]
        message = getattr(error, 'verify_message', error.args[0]).capitalize()
        super().__init__(
            UNKNOWN,
            f'Unable to verify SSL certificate: {message}'
        )


class CybercrimeWatchdogError(TRError):
    def __init__(self):
        super().__init__(
            HEALTH_CHECK_ERROR,
            'Invalid Health Check'
        )
