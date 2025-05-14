import pytest
from unittest.mock import patch, MagicMock
from app.core.model.user_roles import UserRole
import mysql.connector

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect')
def test_get_by_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 1, 'user_id': 2, 'role': 'admin', 'created_at': None}
    obj = UserRole.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.user_id == 2
    assert obj.role == 'admin'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = UserRole.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = UserRole.get_by_id(1)
    assert obj is None

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect')
def test_get_by_user_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'user_id': 2, 'role': 'admin', 'created_at': None},
        {'id': 2, 'user_id': 2, 'role': 'user', 'created_at': None}
    ]
    objs = UserRole.get_by_user_id(2)
    assert isinstance(objs, list)
    assert len(objs) == 2
    assert objs[0].role == 'admin'
    assert objs[1].role == 'user'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_user_id_db_error(mock_connect, mock_db):
    objs = UserRole.get_by_user_id(2)
    assert objs == []

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect')
def test_get_all_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'user_id': 2, 'role': 'admin', 'created_at': None},
        {'id': 2, 'user_id': 3, 'role': 'user', 'created_at': None}
    ]
    objs = UserRole.get_all()
    assert isinstance(objs, list)
    assert len(objs) == 2
    assert objs[0].user_id == 2
    assert objs[1].role == 'user'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_all_db_error(mock_connect, mock_db):
    objs = UserRole.get_all()
    assert objs == []

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect')
def test_save_insert(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = UserRole(id=None, user_id=2, role='admin')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect')
def test_save_update(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = UserRole(id=5, user_id=2, role='admin')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = UserRole(id=None, user_id=2, role='admin')
    result = obj.save()
    assert result is False

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect')
def test_delete_success(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = UserRole(id=5, user_id=2, role='admin')
    result = obj.delete()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_roles.get_db_config', return_value={})
@patch('app.core.model.user_roles.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_delete_db_error(mock_connect, mock_db):
    obj = UserRole(id=5, user_id=2, role='admin')
    result = obj.delete()
    assert result is False 