from tornado import gen
from tornado.httpclient import AsyncHTTPClient


@gen.coroutine
def fetch_coroutine(url):
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(url)
    raise gen.Return(response.code)
