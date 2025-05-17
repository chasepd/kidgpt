import mysql.connector
from typing import Optional, List
from mysql.connector import Error
from app.core.config import get_db_config

class Persona:
    def __init__(self, id: Optional[int], name: str, system_prompt: str, created_at: Optional[str] = None):
        self.id = id
        self.name = name
        self.system_prompt = system_prompt
        self.created_at = created_at

    @classmethod
    def get_by_id(cls, id: int) -> Optional['Persona']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM personas WHERE id = %s", (id,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading persona: {e}")
            return None
        finally:
            if cursor is not None:  
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_by_name(cls, name: str) -> Optional['Persona']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM personas WHERE name = %s", (name,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading persona: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_all(cls) -> List['Persona']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM personas ORDER BY name ASC")
            return [cls(**row) for row in cursor.fetchall()]
        except Error as e:
            print(f"Error loading personas: {e}")
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
                    "INSERT INTO personas (name, system_prompt) VALUES (%s, %s)",
                    (self.name, self.system_prompt)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE personas SET name = %s, system_prompt = %s WHERE id = %s",
                    (self.name, self.system_prompt, self.id)
                )
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving persona: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    def delete(self) -> bool:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM personas WHERE id = %s", (self.id,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error deleting persona: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()
