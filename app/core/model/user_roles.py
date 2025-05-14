import mysql.connector
from typing import Optional, List
from mysql.connector import Error
from app.core.config import get_db_config

class UserRole:
    def __init__(self, id: Optional[int], user_id: int, role: str, created_at: Optional[str] = None):
        self.id = id
        self.user_id = user_id
        self.role = role
        self.created_at = created_at

    @classmethod
    def get_by_id(cls, id: int) -> Optional['UserRole']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_roles WHERE id = %s", (id,))
            data = cursor.fetchone()
            if not data:
                return None
            return cls(**data)
        except Error as e:
            print(f"Error loading user role: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_by_user_id(cls, user_id: int) -> List['UserRole']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_roles WHERE user_id = %s", (user_id,))
            roles = [cls(**row) for row in cursor.fetchall()]
            return roles
        except Error as e:
            print(f"Error loading user roles: {e}")
            return []
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_all(cls) -> List['UserRole']:
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_roles ORDER BY id ASC")
            return [cls(**row) for row in cursor.fetchall()]
        except Error as e:
            print(f"Error loading user roles: {e}")
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
                    "INSERT INTO user_roles (user_id, role) VALUES (%s, %s)",
                    (self.user_id, self.role)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE user_roles SET user_id = %s, role = %s WHERE id = %s",
                    (self.user_id, self.role, self.id)
                )
            connection.commit()
            return True
        except Error as e:
            print(f"Error saving user role: {e}")
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
            cursor.execute("DELETE FROM user_roles WHERE id = %s", (self.id,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error deleting user role: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close() 