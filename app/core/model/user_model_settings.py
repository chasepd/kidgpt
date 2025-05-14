import mysql.connector
from typing import Optional, List
from mysql.connector import Error
from app.core.config import get_db_config

class UserModelSettings:
    def __init__(self, id: Optional[int], user_id: int, system_instructions: str, created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.user_id = user_id
        self.system_instructions = system_instructions
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def get_by_id(cls, id: int) -> Optional['UserModelSettings']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_model_settings WHERE id = %s", (id,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading user model settings: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional['UserModelSettings']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_model_settings WHERE user_id = %s", (user_id,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading user model settings: {e}")
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
                    "INSERT INTO user_model_settings (user_id, system_instructions) VALUES (%s, %s)",
                    (self.user_id, self.system_instructions)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE user_model_settings SET user_id = %s, system_instructions = %s WHERE id = %s",
                    (self.user_id, self.system_instructions, self.id)
                )
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving user model settings: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close() 