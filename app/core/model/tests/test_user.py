import pytest
from unittest.mock import patch, MagicMock
from app.core.model.user import User
import mysql.connector

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect')
def test_get_by_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {
        'id': 1, 'username': 'alice', 'text_name': 'Alice', 'password_hash': 'hash',
        'role': 'child', 'failed_login_attempts': 0, 'locked_until': None
    }
    obj = User.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.username == 'alice'
    assert obj.role == 'child'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = User.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = User.get_by_id(1)
    assert obj is None

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect')
def test_get_by_username_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {
        'id': 2, 'username': 'bob', 'text_name': 'Bob', 'password_hash': 'hash2',
        'role': 'admin-parent', 'failed_login_attempts': 1, 'locked_until': None
    }
    obj = User.get_by_username('bob')
    assert obj is not None
    assert obj.username == 'bob'
    assert obj.role == 'admin-parent'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect')
def test_get_by_username_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = User.get_by_username('bob')
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_username_db_error(mock_connect, mock_db):
    obj = User.get_by_username('bob')
    assert obj is None

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect')
def test_get_all_children_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'username': 'alice', 'text_name': 'Alice', 'password_hash': 'hash',
         'role': 'child', 'failed_login_attempts': 0, 'locked_until': None},
        {'id': 2, 'username': 'bob', 'text_name': 'Bob', 'password_hash': 'hash2',
         'role': 'child', 'failed_login_attempts': 1, 'locked_until': None}
    ]
    objs = User.get_all_children()
    assert isinstance(objs, list)
    assert len(objs) == 2
    assert objs[0].username == 'alice'
    assert objs[1].role == 'child'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_all_children_db_error(mock_connect, mock_db):
    objs = User.get_all_children()
    assert objs == []

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect')
def test_save_insert(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = User(id=None, username='alice', password_hash='hash', text_name='Alice', role='child')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect')
def test_save_update(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = User(id=5, username='alice', password_hash='hash', text_name='Alice', role='child')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.core.model.user.get_db_config', return_value={})
@patch('app.core.model.user.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = User(id=None, username='alice', password_hash='hash', text_name='Alice', role='child')
    result = obj.save()
    assert result is False 