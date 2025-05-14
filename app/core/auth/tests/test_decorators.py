import pytest
from flask import Flask, session, jsonify
from unittest.mock import patch, MagicMock
from app.core.auth.decorators import authorize, authorize_any

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'testkey'
    # Add dummy main.show_login endpoint
    @app.route('/login')
    def show_login():
        return 'Login Page', 200
    app.add_url_rule('/login', endpoint='main.show_login', view_func=show_login)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# Helper: register a route with a decorator for testing
def add_route(app, rule, decorator, endpoint_name, response_text='OK'):
    @app.route(rule)
    @decorator
    def endpoint():
        return response_text
    endpoint.__name__ = endpoint_name
    return endpoint

# --- authorize tests ---
def test_authorize_allows_correct_role(app, client):
    with patch('app.core.model.user.User.get_by_id') as mock_get_by_id:
        user = MagicMock()
        user.role = 'admin'
        mock_get_by_id.return_value = user
        add_route(app, '/admin', authorize('admin'), 'admin_endpoint')
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        resp = client.get('/admin')
        assert resp.status_code == 200
        assert b'OK' in resp.data

def test_authorize_denies_wrong_role(app, client):
    with patch('app.core.model.user.User.get_by_id') as mock_get_by_id:
        user = MagicMock()
        user.role = 'child'
        mock_get_by_id.return_value = user
        add_route(app, '/admin', authorize('admin'), 'admin_endpoint2')
        with client.session_transaction() as sess:
            sess['user_id'] = 2
        resp = client.get('/admin')
        assert resp.status_code == 403
        assert b'Insufficient permissions' in resp.data

def test_authorize_redirects_if_no_user_in_session(app, client):
    add_route(app, '/admin', authorize('admin'), 'admin_endpoint3')
    resp = client.get('/admin', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location'] or '/show_login' in resp.headers['Location']

def test_authorize_redirects_if_user_not_found(app, client):
    with patch('app.core.model.user.User.get_by_id', return_value=None):
        add_route(app, '/admin', authorize('admin'), 'admin_endpoint4')
        with client.session_transaction() as sess:
            sess['user_id'] = 999
        resp = client.get('/admin', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location'] or '/show_login' in resp.headers['Location']

# --- authorize_any tests ---
def test_authorize_any_allows_authenticated_user(app, client):
    with patch('app.core.model.user.User.get_by_id') as mock_get_by_id:
        mock_get_by_id.return_value = MagicMock()
        add_route(app, '/protected', authorize_any(), 'protected_endpoint')
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        resp = client.get('/protected')
        assert resp.status_code == 200
        assert b'OK' in resp.data

def test_authorize_any_redirects_if_not_authenticated_browser(app, client):
    add_route(app, '/protected', authorize_any(), 'protected_endpoint2')
    resp = client.get('/protected', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location'] or '/show_login' in resp.headers['Location']

def test_authorize_any_returns_401_for_api(app, client):
    add_route(app, '/api', authorize_any(), 'api_endpoint')
    resp = client.get('/api', headers={'X-Requested-With': 'XMLHttpRequest'})
    assert resp.status_code == 401
    assert b'Not authenticated' in resp.data

def test_authorize_any_returns_401_for_json_request(app, client):
    add_route(app, '/api2', authorize_any(), 'api_endpoint2')
    resp = client.get('/api2', headers={'Content-Type': 'application/json'}, json={})
    assert resp.status_code == 401
    assert b'Not authenticated' in resp.data

def test_authorize_any_redirects_if_user_not_found(app, client):
    with patch('app.core.model.user.User.get_by_id', return_value=None):
        add_route(app, '/protected2', authorize_any(), 'protected_endpoint3')
        with client.session_transaction() as sess:
            sess['user_id'] = 123
        resp = client.get('/protected2', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location'] or '/show_login' in resp.headers['Location']

def test_authorize_any_returns_401_for_api_if_user_not_found(app, client):
    with patch('app.core.model.user.User.get_by_id', return_value=None):
        add_route(app, '/api3', authorize_any(), 'api_endpoint3')
        with client.session_transaction() as sess:
            sess['user_id'] = 123
        resp = client.get('/api3', headers={'X-Requested-With': 'XMLHttpRequest'})
        assert resp.status_code == 401
        assert b'Not authenticated' in resp.data 