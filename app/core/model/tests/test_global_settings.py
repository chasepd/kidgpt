import pytest
from unittest.mock import patch, MagicMock
from app.core.model.global_settings import GlobalSetting
import mysql.connector

@patch('app.core.model.global_settings.get_db_config', return_value={})
@patch('app.core.model.global_settings.mysql.connector.connect')
def test_get_by_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 1, 'setting_key': 'foo', 'setting_value': 'bar', 'updated_at': None}
    obj = GlobalSetting.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.setting_key == 'foo'
    assert obj.setting_value == 'bar'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.global_settings.get_db_config', return_value={})
@patch('app.core.model.global_settings.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = GlobalSetting.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.global_settings.get_db_config', return_value={})
@patch('app.core.model.global_settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = GlobalSetting.get_by_id(1)
    assert obj is None

@patch('app.core.model.global_settings.get_db_config', return_value={})
@patch('app.core.model.global_settings.mysql.connector.connect')
def test_get_by_key_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 2, 'setting_key': 'baz', 'setting_value': 'qux', 'updated_at': None}
    obj = GlobalSetting.get_by_key('baz')
    assert obj is not None
    assert obj.setting_key == 'baz'
    assert obj.setting_value == 'qux'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.global_settings.get_db_config', return_value={})
@patch('app.core.model.global_settings.mysql.connector.connect')
def test_get_by_key_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = GlobalSetting.get_by_key('baz')
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.global_settings.get_db_config', return_value={})
@patch('app.core.model.global_settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_key_db_error(mock_connect, mock_db):
    obj = GlobalSetting.get_by_key('baz')
    assert obj is None

@patch('app.core.model.global_settings.get_db_config', return_value={})
@patch('app.core.model.global_settings.mysql.connector.connect')
def test_save_insert(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = GlobalSetting(id=None, setting_key='foo', setting_value='bar')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.global_settings.get_db_config', return_value={})
@patch('app.core.model.global_settings.mysql.connector.connect')
def test_save_update(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = GlobalSetting(id=5, setting_key='foo', setting_value='bar')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.global_settings.get_db_config', return_value={})
@patch('app.core.model.global_settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = GlobalSetting(id=None, setting_key='foo', setting_value='bar')
    result = obj.save()
    assert result is False 