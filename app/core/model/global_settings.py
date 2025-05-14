import mysql.connector
from typing import Optional
from mysql.connector import Error
from app.core.config import get_db_config

class GlobalSetting:
    def __init__(self, id: Optional[int], setting_key: str, setting_value: str, updated_at: Optional[str] = None):
        self.id = id
        self.setting_key = setting_key
        self.setting_value = setting_value
        self.updated_at = updated_at

    @classmethod
    def get_by_id(cls, id: int) -> Optional['GlobalSetting']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM global_settings WHERE id = %s", (id,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading global setting: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_by_key(cls, setting_key: str) -> Optional['GlobalSetting']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM global_settings WHERE setting_key = %s", (setting_key,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading global setting: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    def save(self) -> bool:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            if self.id is None:
                cursor.execute(
                    "INSERT INTO global_settings (setting_key, setting_value) VALUES (%s, %s)",
                    (self.setting_key, self.setting_value)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE global_settings SET setting_key = %s, setting_value = %s WHERE id = %s",
                    (self.setting_key, self.setting_value, self.id)
                )
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving global setting: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close() 