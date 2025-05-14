import mysql.connector
from typing import Optional
from mysql.connector import Error
from app.core.config import get_db_config
import os
from cryptography.fernet import Fernet

FERNET_KEY = os.getenv('FERNET_KEY')
fernet = Fernet(FERNET_KEY) if FERNET_KEY else None

class ApiKey:
    def __init__(self, id: Optional[int], model_vendor: str, api_key: str, created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.model_vendor = model_vendor
        self.api_key = api_key
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def get_by_id(cls, id: int) -> Optional['ApiKey']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM api_keys WHERE id = %s", (id,))
            data = cursor.fetchone()
            if not data:
                return None
            data['api_key'] = cls.decrypt_key(data['api_key'])
            return cls(**data)
        except Error as e:
            print(f"Error loading API key: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_by_model_vendor(cls, model_vendor: str) -> Optional['ApiKey']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM api_keys WHERE model_vendor = %s", (model_vendor,))
            data = cursor.fetchone()
            if not data:
                return None
            data['api_key'] = cls.decrypt_key(data['api_key'])
            return cls(**data)
        except Error as e:
            print(f"Error loading API key: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @staticmethod
    def encrypt_key(key: str) -> str:
        if not fernet:
            raise RuntimeError('FERNET_KEY is not set')
        return fernet.encrypt(key.encode()).decode()

    @staticmethod
    def decrypt_key(token: str) -> str:
        if not fernet:
            raise RuntimeError('FERNET_KEY is not set')
        return fernet.decrypt(token.encode()).decode()

    @classmethod
    def get_openai_key(cls) -> Optional[str]:
        obj = cls.get_by_model_vendor('openai')
        return obj.api_key if obj else None

    @classmethod
    def set_openai_key(cls, key: str) -> bool:
        encrypted = cls.encrypt_key(key)
        obj = cls.get_by_model_vendor('openai')
        if obj:
            obj.api_key = encrypted
            return obj.save(encrypted=True)
        else:
            new_obj = cls(id=None, model_vendor='openai', api_key=encrypted)
            return new_obj.save(encrypted=True)

    def save(self, encrypted=False) -> bool:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            key_to_store = self.api_key if encrypted else self.encrypt_key(self.api_key)
            if self.id is None:
                cursor.execute(
                    "INSERT INTO api_keys (model_vendor, api_key) VALUES (%s, %s)",
                    (self.model_vendor, key_to_store)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE api_keys SET model_vendor = %s, api_key = %s WHERE id = %s",
                    (self.model_vendor, key_to_store, self.id)
                )
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving API key: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close() 