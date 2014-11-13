import pytest
from pytest_tornado.main import app as _app


@pytest.fixture(scope='module')
def app():
    return _app
