import os
import io
from setuptools import setup, find_packages


cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, 'README.rst'), encoding='utf-8') as fd:
    long_description = fd.read()


setup(
    name='pytest-tornado',
    version='0.8.0',
    description=('A py.test plugin providing fixtures and markers '
                 'to simplify testing of asynchronous tornado applications.'),
    long_description=long_description,
    url='https://github.com/eugeniy/pytest-tornado',
    author='Eugeniy Kalinin',
    author_email='burump@gmail.com',
    maintainer='Vidar Tonaas Fauske',
    maintainer_email='vidartf@gmail.com',
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
    ],
    keywords=('pytest py.test tornado async asynchronous '
              'testing unit tests plugin'),
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=['pytest>=3.6', 'tornado>=4.1'],
    entry_points={
        'pytest11': ['tornado = pytest_tornado.plugin'],
    },
)
