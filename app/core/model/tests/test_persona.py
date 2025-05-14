import pytest
from unittest.mock import patch, MagicMock
from app.core.model.persona import Persona
import mysql.connector

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect')
def test_get_by_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 1, 'name': 'Alice', 'system_prompt': 'Hi', 'created_at': None}
    obj = Persona.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.name == 'Alice'
    assert obj.system_prompt == 'Hi'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = Persona.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = Persona.get_by_id(1)
    assert obj is None

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect')
def test_get_by_name_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 2, 'name': 'Bob', 'system_prompt': 'Hello', 'created_at': None}
    obj = Persona.get_by_name('Bob')
    assert obj is not None
    assert obj.name == 'Bob'
    assert obj.system_prompt == 'Hello'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect')
def test_get_by_name_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = Persona.get_by_name('Bob')
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_name_db_error(mock_connect, mock_db):
    obj = Persona.get_by_name('Bob')
    assert obj is None

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect')
def test_get_all_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'name': 'Alice', 'system_prompt': 'Hi', 'created_at': None},
        {'id': 2, 'name': 'Bob', 'system_prompt': 'Hello', 'created_at': None}
    ]
    objs = Persona.get_all()
    assert isinstance(objs, list)
    assert len(objs) == 2
    assert objs[0].name == 'Alice'
    assert objs[1].system_prompt == 'Hello'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_all_db_error(mock_connect, mock_db):
    objs = Persona.get_all()
    assert objs == []

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect')
def test_save_insert(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = Persona(id=None, name='Alice', system_prompt='Hi')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect')
def test_save_update(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = Persona(id=5, name='Alice', system_prompt='Hi')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = Persona(id=None, name='Alice', system_prompt='Hi')
    result = obj.save()
    assert result is False

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect')
def test_delete_success(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = Persona(id=5, name='Alice', system_prompt='Hi')
    result = obj.delete()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.persona.get_db_config', return_value={})
@patch('app.core.model.persona.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_delete_db_error(mock_connect, mock_db):
    obj = Persona(id=5, name='Alice', system_prompt='Hi')
    result = obj.delete()
    assert result is False 