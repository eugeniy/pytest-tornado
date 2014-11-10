import functools
import tornado.gen
from pytest_tornado.coroutine import fetch_coroutine


def gen_test(func=None, timeout=None):
    def wrap(f):

        coro = tornado.gen.coroutine(f)

        @functools.wraps(coro)
        def post_coroutine(io_loop, *args, **kwargs):
            return io_loop.run_sync(
                functools.partial(coro, io_loop, *args, **kwargs))

        return post_coroutine

    return wrap(func)


def test_explicit_start_and_stop(io_loop):
    f = fetch_coroutine('http://google.com')
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200


@gen_test
def test_coroutines(io_loop):

    response = yield fetch_coroutine('http://google.com')

    #fetch = functools.partial(fetch_coroutine, 'http://google.com')
    #response = io_loop.run_sync(fetch)

    '''
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200
    '''
    assert response == 200
