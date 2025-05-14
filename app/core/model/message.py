import mysql.connector
from typing import Optional, List
from mysql.connector import Error
from app.core.config import get_db_config

class Message:
    def __init__(self, id: Optional[int], conversation_id: int, sender: str, content: str, created_at: Optional[str] = None):
        self.id = id
        self.conversation_id = conversation_id
        self.sender = sender
        self.content = content
        self.created_at = created_at

    @classmethod
    def get_by_id(cls, id: int) -> Optional['Message']:
        connection = None
        cursor = None   
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM messages WHERE id = %s", (id,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading message: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_by_conversation_id(cls, conversation_id: int) -> List['Message']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM messages WHERE conversation_id = %s ORDER BY created_at ASC", (conversation_id,))
            messages = [cls(**row) for row in cursor.fetchall()]
            return messages
        except Error as e:
            print(f"Error loading messages: {e}")
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
                    "INSERT INTO messages (conversation_id, sender, content) VALUES (%s, %s, %s)",
                    (self.conversation_id, self.sender, self.content)
                )
                self.id = cursor.lastrowid
            else:
                # Only content can be updated
                cursor.execute(
                    "UPDATE messages SET content = %s WHERE id = %s",
                    (self.content, self.id)
                )
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving message: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close() 