import pytest
from unittest.mock import patch, MagicMock
from app.core.model.api_key import ApiKey
import mysql.connector

@pytest.fixture
def fake_fernet():
    class FakeFernet:
        def encrypt(self, data):
            return b'encrypted_' + data
        def decrypt(self, token):
            if token.startswith(b'encrypted_'):
                return token[len(b'encrypted_'):]
            raise ValueError('Invalid token')
    return FakeFernet()

@patch('app.core.model.api_key.fernet', new_callable=lambda: None)
def test_encrypt_key_no_fernet(mock_fernet):
    with pytest.raises(RuntimeError):
        ApiKey.encrypt_key('secret')

@patch('app.core.model.api_key.fernet', new_callable=lambda: None)
def test_decrypt_key_no_fernet(mock_fernet):
    with pytest.raises(RuntimeError):
        ApiKey.decrypt_key('token')

@patch('app.core.model.api_key.fernet')
def test_encrypt_and_decrypt_key(mock_fernet, fake_fernet):
    mock_fernet.encrypt.side_effect = fake_fernet.encrypt
    mock_fernet.decrypt.side_effect = fake_fernet.decrypt
    encrypted = ApiKey.encrypt_key('mykey')
    assert encrypted == 'encrypted_mykey'
    decrypted = ApiKey.decrypt_key('encrypted_mykey')
    assert decrypted == 'mykey'

@patch('app.core.model.api_key.get_db_config', return_value={})
@patch('app.core.model.api_key.mysql.connector.connect')
@patch('app.core.model.api_key.fernet')
def test_get_by_id_found(mock_fernet, mock_connect, mock_db, fake_fernet):
    mock_fernet.decrypt.side_effect = fake_fernet.decrypt
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {
        'id': 1, 'model_vendor': 'openai', 'api_key': 'encrypted_test', 'created_at': None, 'updated_at': None
    }
    obj = ApiKey.get_by_id(1)
    assert obj is not None
    assert obj.id == 1
    assert obj.api_key == 'test'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.api_key.get_db_config', return_value={})
@patch('app.core.model.api_key.mysql.connector.connect')
def test_get_by_id_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = ApiKey.get_by_id(1)
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.api_key.get_db_config', return_value={})
@patch('app.core.model.api_key.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_id_db_error(mock_connect, mock_db):
    obj = ApiKey.get_by_id(1)
    assert obj is None

@patch('app.core.model.api_key.get_db_config', return_value={})
@patch('app.core.model.api_key.mysql.connector.connect')
@patch('app.core.model.api_key.fernet')
def test_get_by_model_vendor_found(mock_fernet, mock_connect, mock_db, fake_fernet):
    mock_fernet.decrypt.side_effect = fake_fernet.decrypt
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = {
        'id': 2, 'model_vendor': 'anthropic', 'api_key': 'encrypted_key', 'created_at': None, 'updated_at': None
    }
    obj = ApiKey.get_by_model_vendor('anthropic')
    assert obj is not None
    assert obj.model_vendor == 'anthropic'
    assert obj.api_key == 'key'
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.api_key.get_db_config', return_value={})
@patch('app.core.model.api_key.mysql.connector.connect')
def test_get_by_model_vendor_not_found(mock_connect, mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.fetchone.return_value = None
    obj = ApiKey.get_by_model_vendor('none')
    assert obj is None
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.api_key.get_db_config', return_value={})
@patch('app.core.model.api_key.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_get_by_model_vendor_db_error(mock_connect, mock_db):
    obj = ApiKey.get_by_model_vendor('none')
    assert obj is None

@patch.object(ApiKey, 'get_by_model_vendor')
def test_get_openai_key(mock_get_by_vendor):
    mock_obj = MagicMock()
    mock_obj.api_key = 'openai_key'
    mock_get_by_vendor.return_value = mock_obj
    assert ApiKey.get_openai_key() == 'openai_key'
    mock_get_by_vendor.return_value = None
    assert ApiKey.get_openai_key() is None

@patch.object(ApiKey, 'get_by_model_vendor')
@patch.object(ApiKey, 'save', return_value=True)
@patch('app.core.model.api_key.fernet')
def test_set_openai_key_update(mock_fernet, mock_save, mock_get_by_vendor, fake_fernet):
    mock_fernet.encrypt.side_effect = fake_fernet.encrypt
    obj = MagicMock()
    obj.save.return_value = True
    mock_get_by_vendor.return_value = obj
    result = ApiKey.set_openai_key('newkey')
    assert result is True
    obj.save.assert_called_once_with(encrypted=True)
    assert obj.api_key == 'encrypted_newkey'

@patch.object(ApiKey, 'get_by_model_vendor', return_value=None)
@patch.object(ApiKey, 'save', return_value=True)
@patch('app.core.model.api_key.fernet')
def test_set_openai_key_new(mock_fernet, mock_save, mock_get_by_vendor, fake_fernet):
    mock_fernet.encrypt.side_effect = fake_fernet.encrypt
    result = ApiKey.set_openai_key('brandnew')
    assert result is True
    mock_save.assert_called_once_with(encrypted=True)

@patch('app.core.model.api_key.get_db_config', return_value={})
@patch('app.core.model.api_key.mysql.connector.connect')
@patch('app.core.model.api_key.fernet')
def test_save_insert(mock_fernet, mock_connect, mock_db, fake_fernet):
    mock_fernet.encrypt.side_effect = fake_fernet.encrypt
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    mock_cursor.lastrowid = 42
    obj = ApiKey(id=None, model_vendor='openai', api_key='mykey')
    result = obj.save()
    assert result is True
    assert obj.id == 42
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.api_key.get_db_config', return_value={})
@patch('app.core.model.api_key.mysql.connector.connect')
@patch('app.core.model.api_key.fernet')
def test_save_update(mock_fernet, mock_connect, mock_db, fake_fernet):
    mock_fernet.encrypt.side_effect = fake_fernet.encrypt
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.is_connected.return_value = True
    obj = ApiKey(id=5, model_vendor='openai', api_key='mykey')
    result = obj.save()
    assert result is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('app.core.model.api_key.get_db_config', return_value={})
@patch('app.core.model.api_key.mysql.connector.connect', side_effect=mysql.connector.Error('DB error'))
def test_save_db_error(mock_connect, mock_db):
    obj = ApiKey(id=None, model_vendor='openai', api_key='mykey')
    result = obj.save()
    assert result is False 