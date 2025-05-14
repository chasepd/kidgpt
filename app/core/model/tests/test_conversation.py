import pytest
from unittest.mock import patch, MagicMock
from app.core.model.conversation import Conversation
import mysql.connector

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect')
def test_get_by_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 1, 'user_id': 2, 'started_at': '2024-01-01', 'summary': 'test'}
    obj = Conversation.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.user_id == 2
    assert obj.summary == 'test'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = Conversation.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = Conversation.get_by_id(1)
    assert obj is None

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect')
def test_get_by_user_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'user_id': 2, 'started_at': '2024-01-01', 'summary': 'test'},
        {'id': 2, 'user_id': 2, 'started_at': '2024-01-02', 'summary': 'test2'}
    ]
    conversations = Conversation.get_by_user_id(2)
    assert isinstance(conversations, list)
    assert len(conversations) == 2
    assert conversations[0].id == 1
    assert conversations[1].id == 2
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_user_id_db_error(mock_connect, mock_db):
    conversations = Conversation.get_by_user_id(2)
    assert conversations == []

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect')
def test_save_insert(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = Conversation(id=None, user_id=2, summary='test')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect')
def test_save_update(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = Conversation(id=5, user_id=2, summary='test')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = Conversation(id=None, user_id=2, summary='test')
    result = obj.save()
    assert result is False

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect')
def test_delete_success(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = Conversation(id=5, user_id=2, summary='test')
    result = obj.delete()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect')
def test_delete_no_id(mock_connect, mock_db):
    obj = Conversation(id=None, user_id=2, summary='test')
    result = obj.delete()
    assert result is False

@patch('app.core.model.conversation.get_db_config', return_value={})
@patch('app.core.model.conversation.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_delete_db_error(mock_connect, mock_db):
    obj = Conversation(id=5, user_id=2, summary='test')
    result = obj.delete()
    assert result is False 