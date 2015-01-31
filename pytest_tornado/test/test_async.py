import functools
import pytest
from tornado import gen
from tornado.ioloop import TimeoutError
from decorator import decorator


@decorator
def _assert_raises(func, *args, **kwargs):
    with pytest.raises(ZeroDivisionError):
        func(*args, **kwargs)


@decorator
def _assert_times_out(func, *args, **kwargs):
    with pytest.raises(TimeoutError):
        func(*args, **kwargs)


@gen.coroutine
def dummy_coroutine(io_loop):
    yield gen.Task(io_loop.add_callback)
    raise gen.Return(True)


def test_explicit_start_and_stop(io_loop):
    future = dummy_coroutine(io_loop)
    future.add_done_callback(lambda *args: io_loop.stop())
    io_loop.start()
    assert future.result()


def test_run_sync(io_loop):
    dummy = functools.partial(dummy_coroutine, io_loop)
    finished = io_loop.run_sync(dummy)
    assert finished


@pytest.gen_test
def test_gen_test(io_loop):
    result = yield dummy_coroutine(io_loop)
    assert result


@_assert_raises
@pytest.gen_test
def test_gen_test_swallows_exceptions(io_loop):
    1 / 0


@_assert_raises
@pytest.gen_test
def test_gen_test_yields_forever(io_loop):
    yield dummy_coroutine(io_loop)
    # pytest uses generators to collect tests, so it will never make it here
    1 / 0


@pytest.gen_test()
def test_gen_test_callable(io_loop):
    result = yield dummy_coroutine(io_loop)
    assert result


@_assert_times_out
@pytest.gen_test(timeout=0.1)
def test_gen_test_with_timeout(io_loop):
    yield gen.Task(io_loop.add_timeout, io_loop.time() + 1)
