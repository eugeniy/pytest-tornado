from pytest_tornado.coroutine import fetch_coroutine


def test_explicit_start_and_stop(io_loop):
    f = fetch_coroutine('http://google.com')
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200


def test_coroutines(io_loop):
    f = fetch_coroutine('http://google.com')
    '''
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200
    '''
    assert f == 200
