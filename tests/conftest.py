import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    #tempfile.mkstemp() creates and opens a temporary file, returning the file descriptor and the path to it
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        #The DATABASE path is overridden so it points to this temporary path instead of the instance folder. 
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    #The client fixture calls app.test_client() with the application object created by the app fixture.
    return app.test_client()


@pytest.fixture
def runner(app):
    #The runner fixture is similar to client. app.test_cli_runner() creates a runner that can call the Click commands registered with the application.
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)