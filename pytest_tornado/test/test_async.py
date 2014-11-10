import functools
import types
import tornado.gen
from pytest_tornado.coroutine import fetch_coroutine


def gen_test(func=None, timeout=None):
    def wrap(f):
        @functools.wraps(f)
        def pre_coroutine(io_loop, *args, **kwargs):
            result = f(io_loop, *args, **kwargs)
            '''
            if isinstance(result, types.GeneratorType):
                self._test_generator = result
            else:
                self._test_generator = None
            '''
            return result

        coro = tornado.gen.coroutine(pre_coroutine)

        @functools.wraps(coro)
        def post_coroutine(io_loop, *args, **kwargs):
            try:
                return io_loop.run_sync(
                    functools.partial(coro, io_loop, *args, **kwargs))
            except Exception as e:
                # self._test_generator.throw(e)
                raise

        return post_coroutine

    if func is not None:
        return wrap(func)
    else:
        return wrap


def test_explicit_start_and_stop(io_loop):
    f = fetch_coroutine('http://google.com')
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200


@gen_test
def test_coroutines(io_loop):

    response = fetch_coroutine('http://google.com')

    #fetch = functools.partial(fetch_coroutine, 'http://google.com')
    #response = io_loop.run_sync(fetch)

    '''
    f.add_done_callback(lambda future: io_loop.stop())
    io_loop.start()
    assert f.result() == 200
    '''
    assert response == 200
