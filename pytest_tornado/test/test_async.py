import functools
from tornado import gen
from tornado.httpclient import AsyncHTTPClient


@gen.coroutine
def fetch_coroutine(url):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    raise gen.Return(response.code)


def test_explicit_start_and_stop(io_loop):
    f = fetch_coroutine('http://google.com')
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200


def test_run_sync(io_loop):
    fetch = functools.partial(fetch_coroutine, 'http://google.com')
    response = io_loop.run_sync(fetch)
    assert response == 200
