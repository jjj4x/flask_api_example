from pytest import fixture


@fixture(scope='module', name='some')
def setup_some():
    return {'connection_id': 'postgres'}
