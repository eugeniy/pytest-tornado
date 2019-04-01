import os
import ssl
import pytest
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


@pytest.fixture
def ssl_options():
    cert_file = os.path.join(os.path.dirname(__file__), 'testcert.pem')
    if not os.path.exists(cert_file):
        pytest.skip("Missing cert file {!r}")
    key_file = os.path.join(os.path.dirname(__file__), 'testcert.pem')
    if not os.path.exists(key_file):
        pytest.skip("Missing key file {!r}")

    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile=None, capath=None, cadata=None)
    ssl_context.load_cert_chain(cert_file, keyfile=key_file)
    return ssl_context


@pytest.fixture
def app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


@pytest.mark.gen_test
def test_hello_world(https_client, secure_base_url):
    response = yield https_client.fetch(secure_base_url, validate_cert=False)
    assert response.code == 200
