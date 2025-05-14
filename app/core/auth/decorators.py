from functools import wraps
from flask import request, jsonify, redirect, url_for, session
from app.core.model.user import User

def authorize(roles):
    """
    Decorator to check that there is a user in session and that
    user.role is one of the allowed roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return redirect(url_for('main.show_login'))

            user = User.get_by_id(user_id)
            if not user:
                session.clear()
                return redirect(url_for('main.show_login'))

            allowed = [roles] if isinstance(roles, str) else roles
            if user.role not in allowed:
                return jsonify({
                    'error': f'Insufficient permissions. Required role(s): {allowed}'
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def authorize_any():
    """
    Decorator to verify that there is a user_id in session.
    - If it's an AJAX/API call, return JSON 401 on failure.
    - Otherwise redirect to login.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            is_api = (
                request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                or request.is_json
                or request.path.startswith(('/conversations', '/chat'))
            )

            if not user_id:
                session.clear()
                if is_api:
                    return jsonify({'error': 'Not authenticated'}), 401
                return redirect(url_for('main.show_login'))

            # extra safety: make sure that user still exists
            if not User.get_by_id(user_id):
                session.clear()
                if is_api:
                    return jsonify({'error': 'Not authenticated'}), 401
                return redirect(url_for('main.show_login'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
