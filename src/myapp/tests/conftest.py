"""MYAPP tests configuration."""
from pytest import fixture

from myapp import create_app


@fixture(scope='module', name='some')
def setup_some():
    """
    Set up some fixture.

    :return: fixture.
    """
    return {'connection_id': 'postgres'}


@fixture(scope='session', name='app')
def setup_app():
    app = create_app()
    return app
