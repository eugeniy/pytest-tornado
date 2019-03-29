import pytest
import sys
from tornado import gen

_used_fixture = False


@gen.coroutine
def dummy(io_loop):
    yield gen.sleep(0)
    raise gen.Return(True)


@pytest.fixture(scope='module')
def preparations():
    global _used_fixture
    _used_fixture = True


pytestmark = pytest.mark.usefixtures('preparations')


@pytest.mark.xfail(pytest.__version__ < '2.7.0',
                   reason='py.test 2.7 adds hookwrapper, fixes collection')
@pytest.mark.gen_test
def test_uses_pytestmark_fixtures(io_loop):
    assert (yield dummy(io_loop))
    assert _used_fixture

class TestClass:
    def beforeEach(self):
        global _used_fixture
        _used_fixture = False

    @pytest.mark.gen_test
    def test_uses_pytestmark_fixtures(self, io_loop):
        assert (yield dummy(io_loop))
        assert _used_fixture


@pytest.mark.xfail(sys.version_info < (3, 5),
                   reason='Type hints added in Python 3.5')
def test_type_annotation(testdir):

    testdir.makepyfile(
        test_type_annotation="""
            import pytest
            from tornado.ioloop import IOLoop

            @pytest.mark.gen_test
            def test_type_attrib(io_loop: IOLoop):
                pass  # Only check that gen_test works
        """,
    )

    # Run tests
    result = testdir.runpytest_inprocess()

    # Check tests went off as they should:
    assert result.ret == 0
