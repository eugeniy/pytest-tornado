import functools
import pytest
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello, world')


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/f00', MainHandler),
])


@pytest.fixture(scope='module')
def app():
    return application


def _fetch(async_client, url):
    return async_client.io_loop.run_sync(
        functools.partial(async_client.fetch, url))


def test_http_server(http_server):
    status = {'done': False}

    def _done():
        status['done'] = True
        http_server.io_loop.stop()

    http_server.io_loop.add_callback(_done)
    http_server.io_loop.start()

    assert status['done']


def test_async_client(async_client, base_url):
    request = async_client.fetch(base_url)
    request.add_done_callback(lambda future: async_client.io_loop.stop())
    async_client.io_loop.start()

    response = request.result()
    assert response.code == 200


def test_async_client_with_fetch_helper(async_client, base_url):
    response = _fetch(async_client, base_url)
    assert response.code == 200


@pytest.gen_test
def test_async_client_with_gen_test(async_client, base_url):
    response = yield async_client.fetch(base_url)
    assert response.code == 200


@pytest.gen_test
def test_get_url_with_path(async_client, base_url):
    response = yield async_client.fetch('%s/f00' % base_url)
    assert response.code == 200


@pytest.gen_test
def test_client_raises_on_404(async_client, base_url):
    with pytest.raises(tornado.httpclient.HTTPError):
        yield async_client.fetch('%s/bar' % base_url)
