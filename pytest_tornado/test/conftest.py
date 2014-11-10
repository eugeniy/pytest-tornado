import pytest
import tornado


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
def http_server(request, io_loop):
    pass
