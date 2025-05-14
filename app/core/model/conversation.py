import mysql.connector
from typing import Optional, List
from mysql.connector import Error
from app.core.config import get_db_config

class Conversation:
    def __init__(self, id: Optional[int], user_id: int, started_at: Optional[str] = None, summary: Optional[str] = None):
        self.id = id
        self.user_id = user_id
        self.started_at = started_at
        self.summary = summary

    @classmethod
    def get_by_id(cls, id: int) -> Optional['Conversation']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM conversations WHERE id = %s", (id,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading conversation: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_by_user_id(cls, user_id: int) -> List['Conversation']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM conversations WHERE user_id = %s ORDER BY started_at DESC", (user_id,))
            conversations = [cls(**row) for row in cursor.fetchall()]
            return conversations
        except Error as e:
            print(f"Error loading conversations: {e}")
            return []
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
                    "INSERT INTO conversations (user_id, summary) VALUES (%s, %s)",
                    (self.user_id, self.summary)
                )
                self.id = cursor.lastrowid
            else:
                # Only user_id and summary can be updated
                cursor.execute(
                    "UPDATE conversations SET user_id = %s, summary = %s WHERE id = %s",
                    (self.user_id, self.summary, self.id)
                )
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving conversation: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    def delete(self) -> bool:
        if not self.id:
            return False
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = %s", (self.id,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error deleting conversation: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close() 