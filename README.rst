pytest-tornado
==============

.. image:: https://travis-ci.org/eugeniy/pytest-tornado.svg?branch=master
    :target: https://travis-ci.org/eugeniy/pytest-tornado

A py.test_ plugin providing fixtures and markers to simplify testing
of asynchronous tornado applications.

Installation
------------

::

    pip install pytest-tornado


Example
-------

.. code-block:: python

    import pytest
    import tornado.web

    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            self.write("Hello, world")

    application = tornado.web.Application([
        (r"/", MainHandler),
    ])

    @pytest.fixture
    def app():
        return application

    def test_hello_world(http_client, base_url):
        response = yield http_client.fetch(base_url)
        assert response.code == 200


Running tests
-------------

::

    py.test


Fixtures
--------

io_loop
    creates an instance of the `tornado.ioloop.IOLoop`_ for each test case

http_port
    get a port used by the test server

base_url
    get an absolute base url for the test server,
    for example, ``http://localhost:59828``

http_server
    start a tornado HTTP server, you must create an ``app`` fixture,
    which returns the `tornado.web.Application`_ to be tested

http_client
    get an asynchronous HTTP client


Show fixtures provided by the plugin::

    py.test --fixtures


Markers
-------

A ``gen_test`` marker lets you write a coroutine-style tests used with the
`tornado.gen`_ module:

.. code-block:: python

    @pytest.mark.gen_test
    def test_tornado(http_client):
        response = yield http_client.fetch('http://www.tornadoweb.org/')
        assert response.code == 200


Marked tests will time out after 5 seconds. The timeout can be modified by
setting an ``ASYNC_TEST_TIMEOUT`` environment variable,
``--async-test-timeout`` command line argument or a marker argument.

.. code-block:: python

    @pytest.mark.gen_test(timeout=5)
    def test_tornado(http_client):
        yield http_client.fetch('http://www.tornadoweb.org/')


By default, all generator tests are automatically marked and are executed
using tornado's event loop created by the ``io_loop`` fixture. Implicit
marking can be disabled with a ``--no-gen-test`` command line argument.
It can also be disabled for individual tests by settings a ``disabled=True``
argument on the marker.

.. code-block:: python

    # equivalent to the test above
    def test_tornado(http_client):
        response = yield http_client.fetch('http://www.tornadoweb.org/')
        assert response.code == 200

    # disable asynchronous testing, in py.test generators are used to
    # collect additional tests
    @pytest.mark.gen_test(disabled=True)
    def test_default_behavior():
        yield _test_one
        yield _test_two


Show markers provided by the plugin::

    py.test --markers


.. _py.test: http://pytest.org/
.. _`tornado.ioloop.IOLoop`: http://tornado.readthedocs.org/en/latest/ioloop.html#ioloop-objects
.. _`tornado.web.Application`: http://tornado.readthedocs.org/en/latest/web.html#application-configuration
.. _`tornado.gen`: http://tornado.readthedocs.org/en/latest/gen.html
