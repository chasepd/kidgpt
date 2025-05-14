import pytest
from unittest.mock import patch, MagicMock
from app.core.model.user_model_settings import UserModelSettings
import mysql.connector

@patch('app.core.model.user_model_settings.get_db_config', return_value={})
@patch('app.core.model.user_model_settings.mysql.connector.connect')
def test_get_by_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 1, 'user_id': 2, 'system_instructions': 'foo', 'created_at': None, 'updated_at': None}
    obj = UserModelSettings.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.user_id == 2
    assert obj.system_instructions == 'foo'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_model_settings.get_db_config', return_value={})
@patch('app.core.model.user_model_settings.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = UserModelSettings.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_model_settings.get_db_config', return_value={})
@patch('app.core.model.user_model_settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = UserModelSettings.get_by_id(1)
    assert obj is None

@patch('app.core.model.user_model_settings.get_db_config', return_value={})
@patch('app.core.model.user_model_settings.mysql.connector.connect')
def test_get_by_user_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 2, 'user_id': 3, 'system_instructions': 'bar', 'created_at': None, 'updated_at': None}
    obj = UserModelSettings.get_by_user_id(3)
    assert obj is not None
    assert obj.user_id == 3
    assert obj.system_instructions == 'bar'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_model_settings.get_db_config', return_value={})
@patch('app.core.model.user_model_settings.mysql.connector.connect')
def test_get_by_user_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = UserModelSettings.get_by_user_id(3)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_model_settings.get_db_config', return_value={})
@patch('app.core.model.user_model_settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_user_id_db_error(mock_connect, mock_db):
    obj = UserModelSettings.get_by_user_id(3)
    assert obj is None

@patch('app.core.model.user_model_settings.get_db_config', return_value={})
@patch('app.core.model.user_model_settings.mysql.connector.connect')
def test_save_insert(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = UserModelSettings(id=None, user_id=2, system_instructions='foo')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_model_settings.get_db_config', return_value={})
@patch('app.core.model.user_model_settings.mysql.connector.connect')
def test_save_update(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = UserModelSettings(id=5, user_id=2, system_instructions='foo')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.user_model_settings.get_db_config', return_value={})
@patch('app.core.model.user_model_settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = UserModelSettings(id=None, user_id=2, system_instructions='foo')
    result = obj.save()
    assert result is False 