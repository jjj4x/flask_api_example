from flask import url_for, testing
from pytest import mark


@mark.usefixtures('client_class')
class TestAuthViews:

    def test_auth_login(self):
        client: testing.FlaskClient = self.client

        res = client.post(
            url_for('auth.login'),
            json={
                'username': 'me',
                'password': 'me',
            },
        )

        assert res.status_code == 401
