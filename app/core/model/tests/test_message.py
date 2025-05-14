import pytest
from unittest.mock import patch, MagicMock
from app.core.model.message import Message
import mysql.connector

@patch('app.core.model.message.get_db_config', return_value={})
@patch('app.core.model.message.mysql.connector.connect')
def test_get_by_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 1, 'conversation_id': 2, 'sender': 'user', 'content': 'hi', 'created_at': None}
    obj = Message.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.conversation_id == 2
    assert obj.sender == 'user'
    assert obj.content == 'hi'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.message.get_db_config', return_value={})
@patch('app.core.model.message.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = Message.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.message.get_db_config', return_value={})
@patch('app.core.model.message.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = Message.get_by_id(1)
    assert obj is None

@patch('app.core.model.message.get_db_config', return_value={})
@patch('app.core.model.message.mysql.connector.connect')
def test_get_by_conversation_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'conversation_id': 2, 'sender': 'user', 'content': 'hi', 'created_at': None},
        {'id': 2, 'conversation_id': 2, 'sender': 'bot', 'content': 'hello', 'created_at': None}
    ]
    objs = Message.get_by_conversation_id(2)
    assert isinstance(objs, list)
    assert len(objs) == 2
    assert objs[0].id == 1
    assert objs[1].sender == 'bot'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.message.get_db_config', return_value={})
@patch('app.core.model.message.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_conversation_id_db_error(mock_connect, mock_db):
    objs = Message.get_by_conversation_id(2)
    assert objs == []

@patch('app.core.model.message.get_db_config', return_value={})
@patch('app.core.model.message.mysql.connector.connect')
def test_save_insert(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = Message(id=None, conversation_id=2, sender='user', content='hi')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.message.get_db_config', return_value={})
@patch('app.core.model.message.mysql.connector.connect')
def test_save_update(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = Message(id=5, conversation_id=2, sender='user', content='hi')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.message.get_db_config', return_value={})
@patch('app.core.model.message.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = Message(id=None, conversation_id=2, sender='user', content='hi')
    result = obj.save()
    assert result is False 