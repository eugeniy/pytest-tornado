from setuptools import setup, find_packages

setup(
    name='pytest-tornado',
    version='0.1',
    packages=find_packages(),
    install_requires=['pytest', 'tornado'],
    entry_points={
        'pytest11': ['tornado = pytest_tornado.plugin'],
    },
)
