import socket
import pytest
import tornado
import tornado.httpserver
import tornado.httpclient


@pytest.fixture
def bound_socket():
    [sock] = tornado.netutil.bind_sockets(
        None, 'localhost', family=socket.AF_INET)
    return sock


@pytest.fixture
def port(bound_socket):
    return bound_socket.getsockname()[1]


@pytest.fixture
def root_url(port):
    return 'http://localhost:%s' % port


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
def http_server(request, io_loop, bound_socket, app):
    server = tornado.httpserver.HTTPServer(app, io_loop=io_loop)
    server.add_socket(bound_socket)

    def _stop():
        server.stop()
        io_loop.run_sync(server.close_all_connections)

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
