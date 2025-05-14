import pytest
from app.core.auth.auth import AuthService
from unittest.mock import patch, MagicMock
from flask import session as flask_session

@pytest.fixture
def auth_service():
    return AuthService()

def test_hash_and_verify_password(auth_service):
    password = "TestPassword123!"
    hashed = auth_service.hash_password(password)
    assert hashed != password
    assert auth_service.verify_password(password, hashed)
    assert not auth_service.verify_password("WrongPassword", hashed)

def test_validate_password(auth_service):
    valid, msg = auth_service.validate_password("TestPassword123!")
    assert valid
    assert msg == "Password meets requirements"
    # Too short
    valid, msg = auth_service.validate_password("Short1!")
    assert not valid
    # No uppercase
    valid, msg = auth_service.validate_password("testpassword123!")
    assert not valid
    # No lowercase
    valid, msg = auth_service.validate_password("TESTPASSWORD123!")
    assert not valid
    # No number
    valid, msg = auth_service.validate_password("TestPassword!!")
    assert not valid
    # No special char
    valid, msg = auth_service.validate_password("TestPassword123")
    assert not valid

@patch("app.core.auth.auth.User")
@patch("app.core.auth.auth.Settings")
def test_create_user_success(mock_settings, mock_user, auth_service):
    mock_user.get_by_username.return_value = None
    instance = MagicMock()
    instance.save.return_value = True
    instance.get_id.return_value = 1
    mock_user.return_value = instance
    mock_settings.return_value.create_blank_instructions.return_value = None
    success, msg = auth_service.create_user("newuser", "TestPassword123!", "Test User", "child")
    assert success
    assert msg == "User created successfully"

@patch("app.core.auth.auth.User")
def test_create_user_already_exists(mock_user, auth_service):
    mock_user.get_by_username.return_value = True
    success, msg = auth_service.create_user("existinguser", "TestPassword123!", "Test User", "child")
    assert not success
    assert msg == "Username already exists"

@patch("mysql.connector.connect")
def test_has_users_true(mock_connect, auth_service):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = [1]
    mock_conn.is_connected.return_value = True
    assert auth_service.has_users() is True
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("mysql.connector.connect")
def test_has_users_false(mock_connect, auth_service):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = [0]
    mock_conn.is_connected.return_value = True
    assert auth_service.has_users() is False

@patch("mysql.connector.connect", side_effect=Exception("DB error"))
def test_has_users_db_error(mock_connect, auth_service):
    assert auth_service.has_users() is True  # Should return True on error for security

@patch("mysql.connector.connect")
@patch("secrets.token_urlsafe", return_value="token123")
def test_create_session_success(mock_token, mock_connect, auth_service):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    session_token = auth_service.create_session(1, remember=True)
    assert session_token == "token123"
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("mysql.connector.connect", side_effect=Exception("DB error"))
def test_create_session_db_error(mock_connect, auth_service):
    assert auth_service.create_session(1) is None

@patch("app.core.auth.auth.User")
@patch("app.core.auth.auth.AuthService.create_session", return_value="token123")
def test_authenticate_success(mock_create_session, mock_user, auth_service, monkeypatch):
    user = MagicMock()
    user.get_password_hash.return_value = auth_service.hash_password("TestPassword123!")
    user.failed_login_attempts = 0
    user.locked_until = None
    user.get_id.return_value = 1
    user.save.return_value = True
    mock_user.get_by_username.return_value = user

    class MockSession(dict):
        def __init__(self):
            super().__init__()
            self.permanent = False

    fake_session = MockSession()
    monkeypatch.setattr("app.core.auth.auth.session", fake_session)

    success, msg = auth_service.authenticate("user", "TestPassword123!", remember=True)
    assert success
    assert msg == "Login successful"
    assert fake_session["user_id"] == 1
    assert fake_session["session_token"] == "token123"
    assert fake_session.permanent is True

@patch("app.core.auth.auth.User")
def test_authenticate_user_not_found(mock_user, auth_service):
    mock_user.get_by_username.return_value = None
    success, msg = auth_service.authenticate("nouser", "pass")
    assert not success
    assert msg == "Invalid username or password"

@patch("app.core.auth.auth.User")
def test_authenticate_locked_account(mock_user, auth_service):
    user = MagicMock()
    user.locked_until = MagicMock()
    user.locked_until.__gt__.return_value = True
    mock_user.get_by_username.return_value = user
    success, msg = auth_service.authenticate("user", "pass")
    assert not success
    assert "Account is locked" in msg

@patch("app.core.auth.auth.User")
def test_authenticate_wrong_password_and_lock(mock_user, auth_service):
    user = MagicMock()
    user.get_password_hash.return_value = auth_service.hash_password("rightpass")
    user.failed_login_attempts = 4
    user.locked_until = None
    user.save.return_value = True
    user.get_id.return_value = 1
    mock_user.get_by_username.return_value = user
    # Wrong password triggers lock
    success, msg = auth_service.authenticate("user", "wrongpass")
    assert not success
    assert "Account locked" in msg or "attempts remaining" in msg

@patch("mysql.connector.connect")
def test_validate_session_valid(mock_connect, auth_service):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.is_connected.return_value = True
    assert auth_service.validate_session("token123") is True
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("mysql.connector.connect")
def test_validate_session_invalid(mock_connect, auth_service):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_conn.is_connected.return_value = True
    assert auth_service.validate_session("token123") is False

@patch("mysql.connector.connect", side_effect=Exception("DB error"))
def test_validate_session_db_error(mock_connect, auth_service):
    assert auth_service.validate_session("token123") is False

@patch("mysql.connector.connect")
def test_logout_success(mock_connect, auth_service, monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 1
    mock_conn.is_connected.return_value = True
    fake_session = {}
    monkeypatch.setattr("app.core.auth.auth.session", fake_session)
    result = auth_service.logout("token123")
    assert result is True
    assert fake_session == {}
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("mysql.connector.connect")
def test_logout_no_rows(mock_connect, auth_service, monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.rowcount = 0
    mock_conn.is_connected.return_value = True
    fake_session = {}
    monkeypatch.setattr("app.core.auth.auth.session", fake_session)
    result = auth_service.logout("token123")
    assert result is False
    assert fake_session == {}

@patch("mysql.connector.connect", side_effect=Exception("DB error"))
def test_logout_db_error(mock_connect, auth_service, monkeypatch):
    fake_session = {}
    monkeypatch.setattr("app.core.auth.auth.session", fake_session)
    result = auth_service.logout("token123")
    assert result is False 