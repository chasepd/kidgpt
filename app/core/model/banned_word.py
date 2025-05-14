import mysql.connector
from typing import Optional, List
from mysql.connector import Error
from app.core.config import get_db_config

class BannedWord:
    def __init__(self, id: Optional[int], word: str, created_at: Optional[str] = None):
        self.id = id
        self.word = word
        self.created_at = created_at

    @classmethod
    def get_by_id(cls, id: int) -> Optional['BannedWord']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM banned_words WHERE id = %s", (id,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading banned word: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_all(cls) -> List['BannedWord']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM banned_words")
            words = [cls(**row) for row in cursor.fetchall()]
            return words
        except Error as e:
            print(f"Error loading banned words: {e}")
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
                    "INSERT INTO banned_words (word) VALUES (%s)",
                    (self.word,)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE banned_words SET word = %s WHERE id = %s",
                    (self.word, self.id)
                )
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving banned word: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close() 