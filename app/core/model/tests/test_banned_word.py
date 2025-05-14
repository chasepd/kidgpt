import pytest
from unittest.mock import patch, MagicMock
from app.core.model.banned_word import BannedWord
import mysql.connector

@patch('app.core.model.banned_word.get_db_config', return_value={})
@patch('app.core.model.banned_word.mysql.connector.connect')
def test_get_by_id_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {'id': 1, 'word': 'badword', 'created_at': None}
    obj = BannedWord.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.word == 'badword'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.banned_word.get_db_config', return_value={})
@patch('app.core.model.banned_word.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = BannedWord.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.banned_word.get_db_config', return_value={})
@patch('app.core.model.banned_word.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = BannedWord.get_by_id(1)
    assert obj is None

@patch('app.core.model.banned_word.get_db_config', return_value={})
@patch('app.core.model.banned_word.mysql.connector.connect')
def test_get_all_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'word': 'badword', 'created_at': None},
        {'id': 2, 'word': 'worseword', 'created_at': None}
    ]
    words = BannedWord.get_all()
    assert isinstance(words, list)
    assert len(words) == 2
    assert words[0].word == 'badword'
    assert words[1].word == 'worseword'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.banned_word.get_db_config', return_value={})
@patch('app.core.model.banned_word.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_all_db_error(mock_connect, mock_db):
    words = BannedWord.get_all()
    assert words == []

@patch('app.core.model.banned_word.get_db_config', return_value={})
@patch('app.core.model.banned_word.mysql.connector.connect')
def test_save_insert(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = BannedWord(id=None, word='badword')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.banned_word.get_db_config', return_value={})
@patch('app.core.model.banned_word.mysql.connector.connect')
def test_save_update(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = BannedWord(id=5, word='badword')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.banned_word.get_db_config', return_value={})
@patch('app.core.model.banned_word.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = BannedWord(id=None, word='badword')
    result = obj.save()
    assert result is False 