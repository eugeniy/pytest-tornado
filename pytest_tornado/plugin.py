import os
import inspect
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


def pytest_addoption(parser):
    parser.addoption('--async-test-timeout', type=float,
                     default=_get_async_test_timeout(),
                     help='timeout in seconds before failing the test')
    parser.addoption('--app-fixture', default='app',
                     help='fixture name returning a tornado application')
    parser.addoption('--no-gen-test', dest='gen_test', action='store_false',
                     help='disable implicit marking of generator test '
                     'functions with the "gen_test" marker')


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "gen_test(timeout=None, disabled=False): "
                            "mark the test as asynchronous, it will be "
                            "run using tornado's event loop")


def _argnames(func):
    spec = inspect.getargspec(func)
    if spec.defaults:
        return spec.args[:-len(spec.defaults)]
    return spec.args


def _is_async_test(item):
    gen_test = item.get_marker('gen_test')
    if gen_test and not gen_test.kwargs.get('disabled', False):
        return True
    return False


def _timeout(item):
    default_timeout = item.config.getoption('async_test_timeout')
    gen_test = item.get_marker('gen_test')
    if gen_test:
        return gen_test.kwargs.get('timeout', default_timeout)
    return default_timeout


def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name) and inspect.isgeneratorfunction(obj):
        item = pytest.Function(name, parent=collector)

        if pytest.config.option.gen_test and 'gen_test' not in item.keywords:
            item.add_marker('gen_test')

        # convert to a test function unless explicitly disabled
        if _is_async_test(item):
            return item


def pytest_runtest_setup(item):
    if _is_async_test(item) and 'io_loop' not in item.fixturenames:
        # inject an event loop fixture for all async tests
        item.fixturenames.append('io_loop')


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    if _is_async_test(pyfuncitem):
        io_loop = pyfuncitem.funcargs.get('io_loop')

        funcargs = dict((arg, pyfuncitem.funcargs[arg])
                        for arg in _argnames(pyfuncitem.obj))

        coroutine = tornado.gen.coroutine(pyfuncitem.obj)
        io_loop.run_sync(functools.partial(coroutine, **funcargs),
                         timeout=_timeout(pyfuncitem))

        # prevent other pyfunc calls from executing
        return True


@pytest.fixture
def io_loop(request):
    """Create an instance of the `tornado.ioloop.IOLoop` for each test case.
    """
    io_loop = tornado.ioloop.IOLoop()
    io_loop.make_current()

    def _close():
        io_loop.clear_current()
        if (not tornado.ioloop.IOLoop.initialized() or
                io_loop is not tornado.ioloop.IOLoop.instance()):
            io_loop.close(all_fds=True)

    request.addfinalizer(_close)
    return io_loop


@pytest.fixture
def _unused_port():
    return tornado.testing.bind_unused_port()


@pytest.fixture
def http_port(_unused_port):
    """Get a port used by the test server.
    """
    return _unused_port[1]


@pytest.fixture
def base_url(http_port):
    """Create an absolute base url (scheme://host:port)
    """
    return 'http://localhost:%s' % http_port


@pytest.fixture
def http_server(request, io_loop, _unused_port):
    """Start a tornado HTTP server.

    You must create an `app` fixture, which returns the `tornado.web.Application` to be tested.
    """
    try:
        http_app = request.getfuncargvalue(request.config.option.app_fixture)
    except Exception:
        pytest.skip('tornado application fixture not found')

    server = tornado.httpserver.HTTPServer(http_app, io_loop=io_loop)
    server.add_socket(_unused_port[0])

    def _stop():
        server.stop()

        if hasattr(server, 'close_all_connections'):
            io_loop.run_sync(server.close_all_connections,
                             timeout=request.config.option.async_test_timeout)

    request.addfinalizer(_stop)
    return server


@pytest.fixture
def http_client(request, http_server):
    """Get an asynchronous HTTP client.
    """
    client = tornado.httpclient.AsyncHTTPClient(io_loop=http_server.io_loop)

    def _close():
        if (not tornado.ioloop.IOLoop.initialized() or
                client.io_loop is not tornado.ioloop.IOLoop.instance()):
            client.close()

    request.addfinalizer(_close)
    return client
