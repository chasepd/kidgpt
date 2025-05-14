import pytest
from unittest.mock import patch, MagicMock
from app.core.model.session import Session
import mysql.connector

@patch('app.core.model.session.get_db_config', return_value={})
@patch('app.core.model.session.mysql.connector.connect')
def test_get_by_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 1, 'user_id': 2, 'session_token': 'abc', 'expires_at': '2024-01-01', 'created_at': None}
    obj = Session.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.user_id == 2
    assert obj.session_token == 'abc'
    assert obj.expires_at == '2024-01-01'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.session.get_db_config', return_value={})
@patch('app.core.model.session.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = Session.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.session.get_db_config', return_value={})
@patch('app.core.model.session.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = Session.get_by_id(1)
    assert obj is None

@patch('app.core.model.session.get_db_config', return_value={})
@patch('app.core.model.session.mysql.connector.connect')
def test_get_by_session_token_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 2, 'user_id': 3, 'session_token': 'def', 'expires_at': '2024-01-02', 'created_at': None}
    obj = Session.get_by_session_token('def')
    assert obj is not None
    assert obj.session_token == 'def'
    assert obj.user_id == 3
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.session.get_db_config', return_value={})
@patch('app.core.model.session.mysql.connector.connect')
def test_get_by_session_token_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = Session.get_by_session_token('def')
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.session.get_db_config', return_value={})
@patch('app.core.model.session.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_session_token_db_error(mock_connect, mock_db):
    obj = Session.get_by_session_token('def')
    assert obj is None

@patch('app.core.model.session.get_db_config', return_value={})
@patch('app.core.model.session.mysql.connector.connect')
def test_save_insert(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = Session(id=None, user_id=2, session_token='abc', expires_at='2024-01-01')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.session.get_db_config', return_value={})
@patch('app.core.model.session.mysql.connector.connect')
def test_save_update(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = Session(id=5, user_id=2, session_token='abc', expires_at='2024-01-01')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.session.get_db_config', return_value={})
@patch('app.core.model.session.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = Session(id=None, user_id=2, session_token='abc', expires_at='2024-01-01')
    result = obj.save()
    assert result is False 