import bcrypt
import logging
import mysql.connector
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from flask import session
from app.core.model.user import User
from app.core.config import get_db_config
from app.core.settings.settings import Settings

class AuthService:
    """
    Unified service for handling authentication, authorization, and user management
    """
    
    def __init__(self):
        """
        Initialize the AuthService with configuration
        """
        self.db_config = get_db_config()
        # Rate limiting settings
        self.max_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.attempt_reset_after = timedelta(hours=1)
        self.session_duration = timedelta(hours=24)

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def validate_password(self, password: str) -> tuple[bool, str]:
        """
        Validate password meets requirements:
        - At least 8 characters
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one number
        - Contains at least one special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
            
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
            
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
            
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
            
        return True, "Password meets requirements"
        
    def has_users(self) -> bool:
        """Check if any users exist in the database."""
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            logging.error(f"Error checking users: {e}")
            return True  # Assume users exist on error for security
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    def create_user(self, username: str, password: str, text_name: str, role: str) -> Tuple[bool, str]:
        """Create a new user."""
        try:
            logging.info(f"Creating user: {username}, {text_name}, {role}") 
            # Check if user exists
            if User.get_by_username(username):
                logging.warning(f"User already exists: {username}")
                return False, "Username already exists"

            # Create new user
            hashed_password = self.hash_password(password)
            user = User(id=None, username=username, password_hash=hashed_password, text_name=text_name, role=role)

            logging.info(f"Created user: {user.get_id()}, proceeding to save")
            
            if not user.save():
                logging.error(f"Failed to save user: {username}")
                return False, "Failed to save user"
            # Create blank system instructions after user is saved
            Settings().create_blank_instructions(user.get_id())
            return True, "User created successfully"
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return False, "Failed to create user"

    def create_session(self, user_id: int, remember: bool = False) -> Optional[str]:
        """Create a new session for a user"""
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            session_token = secrets.token_urlsafe(32)
            # Set expiration based on remember flag
            expires_at = datetime.now() + (timedelta(days=30) if remember else self.session_duration)
            query = """
                INSERT INTO sessions (user_id, session_token, expires_at)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (user_id, session_token, expires_at))
            conn.commit()
            return session_token
        except Exception as e:
            logging.error(f"Session creation error: {str(e)}")
            return None
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def authenticate(self, username: str, password: str, remember: bool = False) -> Tuple[bool, str]:
        """
        Authenticate a user with rate limiting and session creation
        Returns (success, message)
        """
        try:
            logging.info(f"Authentication attempt for username: {username}")
            user = User.get_by_username(username)
            
            if not user:
                logging.warning(f"Failed login attempt - user not found: {username}")
                return False, "Invalid username or password"

            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.now():
                remaining = (user.locked_until - datetime.now()).seconds // 60
                logging.warning(f"Login attempt for locked account: {username}, remaining lockout time: {remaining} minutes")
                return False, f"Account is locked. Try again in {remaining} minutes"

            # Reset failed attempts if enough time has passed
            if user.failed_login_attempts > 0 and user.locked_until and \
               datetime.now() > user.locked_until + self.attempt_reset_after:
                logging.info(f"Resetting failed login attempts for user: {username}")
                user.failed_login_attempts = 0

            # Check password
            if not self.verify_password(password, user.get_password_hash()):
                user.failed_login_attempts += 1
                
                # Lock account if too many failed attempts
                if user.failed_login_attempts >= self.max_attempts:
                    user.locked_until = datetime.now() + self.lockout_duration
                    user.save()
                    logging.warning(f"Account locked due to too many failed attempts: {username}, lockout duration: {self.lockout_duration.seconds // 60} minutes")
                    return False, f"Too many failed attempts. Account locked for {self.lockout_duration.seconds // 60} minutes"
                
                user.save()
                logging.warning(f"Failed login attempt for user: {username}, attempts remaining: {self.max_attempts - user.failed_login_attempts}")
                return False, f"Invalid username or password. {self.max_attempts - user.failed_login_attempts} attempts remaining"

            # Successful login
            user.failed_login_attempts = 0
            user.locked_until = None
            user.save()
            
            # Create session
            session_token = self.create_session(user.get_id(), remember)
            if not session_token:
                logging.error(f"Failed to create session for user: {username}")
                return False, "Failed to create session"

            # Set session data
            session["user_id"] = user.get_id()
            session["session_token"] = session_token
            if remember:
                session.permanent = True
            
            logging.info(f"Successful login for user: {username}, remember me: {remember}")
            return True, "Login successful"
            
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            return False, "Authentication failed"

    def validate_session(self, session_token: str) -> bool:
        """Validate if a session token is valid and not expired"""
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            query = """
                SELECT 1 FROM sessions 
                WHERE session_token = %s 
                AND expires_at > NOW()
            """
            cursor.execute(query, (session_token,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logging.error(f"Session validation error: {str(e)}")
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
            
    def logout(self, session_token: str) -> bool:
        """Invalidate a session and clear session data"""
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            query = "DELETE FROM sessions WHERE session_token = %s"
            cursor.execute(query, (session_token,))
            conn.commit()
            # Clear session data
            session.clear()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Logout error: {str(e)}")
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
            

# Global auth service instance
auth_service = AuthService()



