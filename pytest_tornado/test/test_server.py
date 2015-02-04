import functools
import pytest
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello, world')


application = tornado.web.Application([
    (r'/', MainHandler),
])


@pytest.fixture(scope='module')
def http_app():
    return application


def _fetch(http_client, url):
    return http_client.io_loop.run_sync(
        functools.partial(http_client.fetch, url))


def test_http_server(http_server):
    status = {'done': False}

    def _done():
        status['done'] = True
        http_server.io_loop.stop()

    http_server.io_loop.add_callback(_done)
    http_server.io_loop.start()

    assert status['done']


def test_http_client(http_client, http_url):
    request = http_client.fetch(http_url)
    request.add_done_callback(lambda future: http_client.io_loop.stop())
    http_client.io_loop.start()

    response = request.result()
    assert response.code == 200


def test_http_client_with_fetch_helper(http_client, http_url):
    response = _fetch(http_client, http_url)
    assert response.code == 200


@pytest.gen_test
def test_http_client_with_gen_test(http_client, http_url):
    response = yield http_client.fetch(http_url)
    assert response.code == 200
