import logging
import mysql.connector
from typing import Optional, Tuple, Literal
from mysql.connector import Error
from app.core.config import get_db_config
from app.core.settings.settings import Settings

# Define valid role types
UserRole = Literal['admin-parent', 'user-parent', 'child']

class User:
    def __init__(self, id: Optional[int], username: str, password_hash: str, text_name: str = "", 
                 role: UserRole = 'child'):
        self.id = id
        self.username = username
        self.text_name = text_name
        if role not in ('admin-parent', 'user-parent', 'child'):
            raise ValueError("Role must be one of: admin-parent, user-parent, child")
        self.role = role
        self.password_hash = password_hash
        self.failed_login_attempts = 0
        self.locked_until = None

    def get_id(self) -> Optional[int]:
        return self.id

    def get_username(self) -> str:
        return self.username
    
    def get_text_name(self) -> str:
        return self.text_name
    
    def get_role(self) -> UserRole:
        return self.role

    def get_password_hash(self) -> Optional[str]:
        return self.password_hash

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """Load a user from the database by ID."""
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            
            # Get user details
            cursor.execute("""
                SELECT u.id, u.username, u.text_name, u.password_hash, ur.role,
                       u.failed_login_attempts, u.locked_until
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                WHERE u.id = %s
                ORDER BY ur.created_at DESC
                LIMIT 1
            """, (user_id,))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
                
            user = cls(
                id=user_data['id'],
                username=user_data['username'],
                text_name=user_data['text_name'],
                role=user_data['role'],
                password_hash=user_data['password_hash']
            )
            user.failed_login_attempts = user_data['failed_login_attempts']
            user.locked_until = user_data['locked_until']
            return user
            
        except Error as e:
            print(f"Error loading user: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        connection = None
        cursor = None
        """Load a user from the database by username."""
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            
            # Get user details
            cursor.execute("""
                SELECT u.id, u.username, u.text_name, u.password_hash, ur.role,
                       u.failed_login_attempts, u.locked_until
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                WHERE u.username = %s
                ORDER BY ur.created_at DESC
                LIMIT 1
            """, (username,))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
                
            user = cls(
                id=user_data['id'],
                username=user_data['username'],
                text_name=user_data['text_name'],
                role=user_data['role'],
                password_hash=user_data['password_hash']
            )
            user.failed_login_attempts = user_data['failed_login_attempts']
            user.locked_until = user_data['locked_until']
            return user
            
        except Error as e:
            print(f"Error loading user: {e}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    def save(self) -> bool:
        """Save the user to the database."""
        connection = None
        cursor = None
        try:
            logging.info(f"Saving user: {self.username}, {self.text_name}, {self.role}")
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            logging.info(f"Saving user: database connection successful")

            if self.id is None:
                logging.info(f"Saving user: new user, inserting into users table")
                # Insert new user
                cursor.execute("""
                    INSERT INTO users (username, text_name, password_hash, 
                                     failed_login_attempts, locked_until)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.username, self.text_name, self.password_hash,
                      self.failed_login_attempts, self.locked_until))
                logging.info(f"Saving user: new user, inserted into users table successfully")
                
                self.id = cursor.lastrowid
                
                # For new users, always insert the role
                logging.info(f"Saving user: new user, inserting into user_roles table")
                if self.role:
                    cursor.execute("""
                        INSERT INTO user_roles (user_id, role)
                        VALUES (%s, %s)
                    """, (self.id, self.role))
                logging.info(f"Saving user: new user, inserted into user_roles table successfully")
            else:
                # Update existing user
                logging.info(f"Saving user: existing user, updating users table")
                cursor.execute("""
                    UPDATE users 
                    SET username = %s, text_name = %s, password_hash = %s,
                        failed_login_attempts = %s, locked_until = %s
                    WHERE id = %s
                """, (self.username, self.text_name, self.password_hash,
                      self.failed_login_attempts, self.locked_until, self.id))
                logging.info(f"Saving user: existing user, updated users table successfully")
                # Update role if provided
                if self.role:
                    # First check if user has any role
                    logging.info(f"Saving user: existing user, checking for existing role")
                    cursor.execute("SELECT role FROM user_roles WHERE user_id = %s", (self.id,))
                    existing_role = cursor.fetchone()
                    logging.info(f"Saving user: existing user, checked for existing role")
                    if existing_role:
                        # Update existing role
                        logging.info(f"Saving user: existing user, updating existing role")
                        cursor.execute("""
                            UPDATE user_roles 
                            SET role = %s
                            WHERE user_id = %s
                        """, (self.role, self.id))
                        logging.info(f"Saving user: existing user, updated existing role successfully")
                    else:
                        # Insert new role
                        logging.info(f"Saving user: existing user, inserting new role")
                        cursor.execute("""
                            INSERT INTO user_roles (user_id, role)
                            VALUES (%s, %s)
                        """, (self.id, self.role))
                        logging.info(f"Saving user: existing user, inserted new role successfully")
            
            connection.commit()
            logging.info(f"Saving user: all operations committed successfully")
            return True
            
        except Error as e:
            logging.error(f"Saving user: error committing operations: {e}")
            if connection is not None and connection.is_connected():
                connection.rollback()
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()   

    @classmethod
    def get_all_children(cls):
        """Return all users with role 'child'."""
        connection = None
        cursor = None
        try:
            db_config = get_db_config()
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT u.id, u.username, u.text_name, u.password_hash, ur.role,
                       u.failed_login_attempts, u.locked_until
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                WHERE ur.role = 'child'
                ORDER BY u.text_name ASC
            ''')
            users = []
            for user_data in cursor.fetchall():
                user = cls(
                    id=user_data['id'],
                    username=user_data['username'],
                    text_name=user_data['text_name'],
                    role=user_data['role'],
                    password_hash=user_data['password_hash']
                )
                user.failed_login_attempts = user_data['failed_login_attempts']
                user.locked_until = user_data['locked_until']
                users.append(user)
            return users
        except Error as e:
            print(f"Error loading children: {e}")
            return []
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()   