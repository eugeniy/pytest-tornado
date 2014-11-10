import functools
from pytest_tornado.coroutine import fetch_coroutine


def test_explicit_start_and_stop(io_loop):
    f = fetch_coroutine('http://google.com')
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200


def test_coroutines(io_loop):

    fetch = functools.partial(fetch_coroutine, 'http://google.com')
    response = io_loop.run_sync(fetch)

    '''
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200
    '''
    assert response == 200
