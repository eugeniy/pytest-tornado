import functools
import pytest
from tornado import gen
from tornado.ioloop import TimeoutError


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


@pytest.mark.gen_test
def test_gen_test_sync(io_loop):
    assert True


@pytest.mark.gen_test
def test_gen_test(io_loop):
    result = yield dummy_coroutine(io_loop)
    assert result


@pytest.mark.gen_test
def test_gen_test_swallows_exceptions(io_loop):
    with pytest.raises(ZeroDivisionError):
        1 / 0


def test_undecorated_generator(io_loop):
    with pytest.raises(ZeroDivisionError):
        yield gen.Task(io_loop.add_callback)
        1 / 0


def test_generators_implicitly_gen_test_marked(request, io_loop):
    yield gen.Task(io_loop.add_callback)
    assert 'gen_test' in request.keywords


@pytest.mark.gen_test
def test_explicit_gen_test_marker(request, io_loop):
    yield gen.Task(io_loop.add_callback)
    assert 'gen_test' in request.keywords


@pytest.mark.gen_test(timeout=2.1)
def test_gen_test_marker_with_params(request, io_loop):
    yield gen.Task(io_loop.add_callback)
    assert request.keywords['gen_test'].kwargs['timeout'] == 2.1


@pytest.mark.xfail(raises=TimeoutError)
@pytest.mark.gen_test(timeout=0.1)
def test_gen_test_with_timeout(io_loop):
    yield gen.Task(io_loop.add_timeout, io_loop.time() + 1)
