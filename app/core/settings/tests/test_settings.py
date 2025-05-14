import pytest
from unittest.mock import patch, MagicMock
from app.core.settings.settings import Settings
import mysql.connector

# --- get_global_system_instructions ---
@patch('app.core.settings.settings.mysql.connector.connect')
@patch('app.core.settings.settings.get_db_config', return_value={})
def test_get_global_system_instructions_found(mock_db, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ('hello',)
    s = Settings()
    result = s.get_global_system_instructions()
    assert result == 'hello'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.mysql.connector.connect')
@patch('app.core.settings.settings.get_db_config', return_value={})
def test_get_global_system_instructions_empty(mock_db, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    s = Settings()
    result = s.get_global_system_instructions()
    assert result == ''
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
@patch('app.core.settings.settings.get_db_config', return_value={})
def test_get_global_system_instructions_db_error(mock_db, mock_connect):
    s = Settings()
    with pytest.raises(mysql.connector.Error):
        s.get_global_system_instructions()

# --- set_global_system_instructions ---
@patch('app.core.settings.settings.mysql.connector.connect')
@patch('app.core.settings.settings.get_db_config', return_value={})
def test_set_global_system_instructions_success(mock_db, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    s = Settings()
    s.set_global_system_instructions('foo')
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
@patch('app.core.settings.settings.get_db_config', return_value={})
def test_set_global_system_instructions_db_error(mock_db, mock_connect):
    s = Settings()
    with pytest.raises(mysql.connector.Error):
        s.set_global_system_instructions('foo')

# --- get_personas ---
@patch('app.core.settings.settings.Persona')
def test_get_personas_success(mock_persona):
    mock_persona.get_all.return_value = [MagicMock(id=1, name='A', system_prompt='x')]
    s = Settings()
    result = s.get_personas(None)
    assert isinstance(result, list)
    assert result[0]['id'] == 1
    mock_persona.get_all.assert_called_once()

@patch('app.core.settings.settings.Persona')
def test_get_personas_error(mock_persona):
    mock_persona.get_all.side_effect = Exception('fail')
    s = Settings()
    with pytest.raises(Exception):
        s.get_personas(None)

# --- add_persona ---
@patch('app.core.settings.settings.Persona')
def test_add_persona_success(mock_persona):
    mock_obj = MagicMock()
    mock_obj.save.return_value = True
    mock_persona.return_value = mock_obj
    s = Settings()
    result = s.add_persona('A', 'x')
    assert result is True
    mock_obj.save.assert_called_once()

@patch('app.core.settings.settings.Persona')
def test_add_persona_save_false(mock_persona):
    mock_obj = MagicMock()
    mock_obj.save.return_value = False
    mock_persona.return_value = mock_obj
    s = Settings()
    result = s.add_persona('A', 'x')
    assert result is False
    mock_obj.save.assert_called_once()

# --- delete_persona ---
@patch('app.core.settings.settings.Persona')
def test_delete_persona_success(mock_persona):
    mock_obj = MagicMock()
    mock_obj.delete.return_value = True
    mock_persona.get_by_id.return_value = mock_obj
    s = Settings()
    result = s.delete_persona(1)
    assert result is True
    mock_obj.delete.assert_called_once()

@patch('app.core.settings.settings.Persona')
def test_delete_persona_not_found(mock_persona):
    mock_persona.get_by_id.return_value = None
    s = Settings()
    result = s.delete_persona(1)
    assert result is False

# --- edit_persona ---
@patch('app.core.settings.settings.Persona')
def test_edit_persona_success(mock_persona):
    mock_obj = MagicMock()
    mock_obj.save.return_value = True
    mock_persona.get_by_id.return_value = mock_obj
    s = Settings()
    result = s.edit_persona(1, 'B', 'y')
    assert result is True
    assert mock_obj.name == 'B'
    assert mock_obj.system_prompt == 'y'
    mock_obj.save.assert_called_once()

@patch('app.core.settings.settings.Persona')
def test_edit_persona_not_found(mock_persona):
    mock_persona.get_by_id.return_value = None
    s = Settings()
    result = s.edit_persona(1, 'B', 'y')
    assert result is False

# --- get_banned_words ---
@patch('app.core.settings.settings.BannedWord')
def test_get_banned_words_success(mock_bw):
    mock_bw.get_all.return_value = [MagicMock(id=1, word='bad')]
    s = Settings()
    result = s.get_banned_words()
    assert isinstance(result, list)
    assert result[0]['id'] == 1
    mock_bw.get_all.assert_called_once()

@patch('app.core.settings.settings.BannedWord')
def test_get_banned_words_error(mock_bw):
    mock_bw.get_all.side_effect = Exception('fail')
    s = Settings()
    with pytest.raises(Exception):
        s.get_banned_words()

# --- add_banned_word ---
@patch('app.core.settings.settings.BannedWord')
def test_add_banned_word_success(mock_bw):
    mock_obj = MagicMock()
    mock_obj.save.return_value = True
    mock_bw.return_value = mock_obj
    s = Settings()
    result = s.add_banned_word('bad')
    assert result is True
    mock_obj.save.assert_called_once()

@patch('app.core.settings.settings.BannedWord')
def test_add_banned_word_save_false(mock_bw):
    mock_obj = MagicMock()
    mock_obj.save.return_value = False
    mock_bw.return_value = mock_obj
    s = Settings()
    result = s.add_banned_word('bad')
    assert result is False
    mock_obj.save.assert_called_once()

# --- delete_banned_word ---
@patch('app.core.settings.settings.BannedWord')
@patch('app.core.settings.settings.mysql.connector.connect')
def test_delete_banned_word_success(mock_connect, mock_bw):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_bw.get_by_id.return_value = MagicMock(id=1, word='bad')
    s = Settings()
    result = s.delete_banned_word(1)
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.BannedWord')
def test_delete_banned_word_not_found(mock_bw):
    mock_bw.get_by_id.return_value = None
    s = Settings()
    result = s.delete_banned_word(1)
    assert result is False

@patch('app.core.settings.settings.BannedWord')
@patch('app.core.settings.settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_delete_banned_word_db_error(mock_connect, mock_bw):
    mock_bw.get_by_id.return_value = MagicMock(id=1, word='bad')
    s = Settings()
    result = s.delete_banned_word(1)
    assert result is False

# --- get_child_instructions ---
@patch('app.core.settings.settings.mysql.connector.connect')
def test_get_child_instructions_found(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = ('inst',)
    s = Settings()
    result = s.get_child_instructions(1)
    assert result == 'inst'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.mysql.connector.connect')
def test_get_child_instructions_empty(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    s = Settings()
    result = s.get_child_instructions(1)
    assert result == ''
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_child_instructions_db_error(mock_connect):
    s = Settings()
    with pytest.raises(mysql.connector.Error):
        s.get_child_instructions(1)

# --- set_child_instructions ---
@patch('app.core.settings.settings.mysql.connector.connect')
def test_set_child_instructions_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    s = Settings()
    s.set_child_instructions(1, 'foo')
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_set_child_instructions_db_error(mock_connect):
    s = Settings()
    with pytest.raises(mysql.connector.Error):
        s.set_child_instructions(1, 'foo')

# --- get_child_persona_ids ---
@patch('app.core.settings.settings.mysql.connector.connect')
def test_get_child_persona_ids_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1,), (2,)]
    s = Settings()
    result = s.get_child_persona_ids(1)
    assert result == [1, 2]
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_child_persona_ids_db_error(mock_connect):
    s = Settings()
    with pytest.raises(mysql.connector.Error):
        s.get_child_persona_ids(1)

# --- set_child_personas ---
@patch('app.core.settings.settings.mysql.connector.connect')
def test_set_child_personas_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    s = Settings()
    s.set_child_personas(1, [1, 2])
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_set_child_personas_db_error(mock_connect):
    s = Settings()
    with pytest.raises(mysql.connector.Error):
        s.set_child_personas(1, [1, 2])

# --- create_blank_instructions ---
@patch('app.core.settings.settings.mysql.connector.connect')
def test_create_blank_instructions_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    s = Settings()
    s.create_blank_instructions(1)
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.settings.settings.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_create_blank_instructions_db_error(mock_connect):
    s = Settings()
    with pytest.raises(mysql.connector.Error):
        s.create_blank_instructions(1) 