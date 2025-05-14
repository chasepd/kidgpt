import mysql.connector
from typing import Optional
from mysql.connector import Error
from app.core.config import get_db_config

class Session:
    def __init__(self, id: Optional[int], user_id: int, session_token: str, expires_at: str, created_at: Optional[str] = None):
        self.id = id
        self.user_id = user_id
        self.session_token = session_token
        self.expires_at = expires_at
        self.created_at = created_at

    @classmethod
    def get_by_id(cls, id: int) -> Optional['Session']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM sessions WHERE id = %s", (id,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading session: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_by_session_token(cls, session_token: str) -> Optional['Session']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM sessions WHERE session_token = %s", (session_token,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading session: {e}")
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
                    "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (%s, %s, %s)",
                    (self.user_id, self.session_token, self.expires_at)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE sessions SET user_id = %s, session_token = %s, expires_at = %s WHERE id = %s",
                    (self.user_id, self.session_token, self.expires_at, self.id)
                )
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving session: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close() 