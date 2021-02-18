from pytest import fixture

from app import app


@fixture(scope='session')
def client():
    app.testing = True

    with app.test_client() as client:
        yield client
