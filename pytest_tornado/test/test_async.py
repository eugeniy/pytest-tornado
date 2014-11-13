import functools
from pytest_tornado.coroutine import fetch_coroutine


def _fetch(http_client, url):
    return http_client.io_loop.run_sync(
        functools.partial(http_client.fetch, url))


def test_explicit_start_and_stop(io_loop):
    f = fetch_coroutine('http://google.com')
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200


def test_run_sync(io_loop):
    fetch = functools.partial(fetch_coroutine, 'http://google.com')
    response = io_loop.run_sync(fetch)
    assert response == 200


def test_http_server(http_server):
    status = {'done': False}

    def _done():
        status['done'] = True
        http_server.io_loop.stop()

    http_server.io_loop.add_callback(_done)
    http_server.io_loop.start()

    assert status['done']


def test_http_client(http_client, root_url):
    request = http_client.fetch(root_url)
    request.add_done_callback(lambda future: http_client.io_loop.stop())
    http_client.io_loop.start()

    response = request.result()
    assert response.code == 200


def test_http_client_with_fetch_helper(http_client, root_url):
    response = _fetch(http_client, root_url)
    assert response.code == 200
