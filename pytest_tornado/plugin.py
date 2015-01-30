import os
import functools
import pytest
import tornado
import tornado.gen
import tornado.testing
import tornado.httpserver
import tornado.httpclient


def _get_async_test_timeout():
    try:
        return float(os.environ.get('ASYNC_TEST_TIMEOUT'))
    except (ValueError, TypeError):
        return 5


def _gen_test(func=None, timeout=None):
    if timeout is None:
        timeout = pytest.config.option.async_test_timeout

    def wrap(f):

        coro = tornado.gen.coroutine(f)

        @functools.wraps(coro)
        def post_coroutine(io_loop, *args, **kwargs):
            return io_loop.run_sync(
                functools.partial(coro, io_loop, *args, **kwargs))

        return post_coroutine

    if func is not None:
        # Used like:
        #     @gen_test
        #     def f(self):
        #         pass
        return wrap(func)
    else:
        # Used like @gen_test(timeout=10)
        return wrap


def pytest_addoption(parser):
    parser.addoption('--async-test-timeout', type='int',
                     default=_get_async_test_timeout(),
                     help='timeout in seconds before failing the test')


def pytest_namespace():
    return {'gen_test': _gen_test}


@pytest.fixture
def io_loop(request):
    io_loop = tornado.ioloop.IOLoop()
    io_loop.make_current()

    def _stop():
        io_loop.clear_current()
        if (not tornado.ioloop.IOLoop.initialized() or
                io_loop is not tornado.ioloop.IOLoop.instance()):
            io_loop.close(all_fds=True)

    request.addfinalizer(_stop)
    return io_loop


@pytest.fixture
def _unused_port():
    return tornado.testing.bind_unused_port()


@pytest.fixture
def http_port(_unused_port):
    return _unused_port[1]


@pytest.fixture
def http_url(http_port):
    return 'http://localhost:%s' % http_port


@pytest.fixture
def http_server(request, io_loop, _unused_port, app):
    server = tornado.httpserver.HTTPServer(app, io_loop=io_loop)
    server.add_socket(_unused_port[0])

    def _stop():
        server.stop()
        io_loop.run_sync(server.close_all_connections,
                         timeout=request.config.option.async_test_timeout)

    request.addfinalizer(_stop)
    return server


@pytest.fixture
def http_client(request, http_server):
    client = tornado.httpclient.AsyncHTTPClient(io_loop=http_server.io_loop)

    def _stop():
        if (not tornado.ioloop.IOLoop.initialized() or
                client.io_loop is not tornado.ioloop.IOLoop.instance()):
            client.close()

    request.addfinalizer(_stop)
    return client
