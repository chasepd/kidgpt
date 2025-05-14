from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, session
import logging
from app.core.auth.decorators import authorize_any, authorize
from app.core.auth.auth import auth_service
from app.core.model.user import User
from app.core.settings.settings import Settings
import bcrypt
from app.core.model.api_key import ApiKey
from app.core.model.banned_word import BannedWord
from app.core.model.conversation import Conversation
from app.core.model.message import Message

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    # Redirect to setup if no users exist
    if not auth_service.has_users():
        return redirect(url_for('main.show_setup'))
        
    if 'user_id' not in session:
        return redirect(url_for('main.show_login'))
    
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('main.show_login'))
        
    from app.core.settings.settings import Settings
    personas = Settings().get_personas(None)
    return render_template("index.html", user=user, personas=personas)

@bp.route("/setup")
def show_setup():
    # If users already exist, redirect to login
    if auth_service.has_users():
        return redirect(url_for('main.show_login'))
    return render_template("setup.html")

@bp.route("/auth/setup", methods=["POST"])
def setup():
    # If users already exist, return error
    if auth_service.has_users():
        return jsonify({"error": "Setup has already been completed"}), 403
        
    data = request.json
    username = data.get("username")
    password = data.get("password")
    text_name = data.get("text_name")
    
    if not all([username, password, text_name]):
        missing = [field for field, value in {'username': username, 'password': password, 'text_name': text_name}.items() if not value]
        error_msg = f"Missing required fields: {', '.join(missing)}"
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 400
    
    # Validate password before creating user
    valid, message = auth_service.validate_password(password)
    if not valid:
        logging.error(f"Password validation failed: {message}")
        return jsonify({"error": message}), 400
        
    logging.info("Creating user with validated password")
    success, message = auth_service.create_user(
        username=username,
        password=password,
        text_name=text_name,
        role="admin-parent"  # First user is always admin
    )
    
    if not success:
        logging.error(f"User creation failed: {message}")
    else:
        logging.info("User created successfully")
    
    return jsonify({"message": message})

@bp.route("/login")
def show_login():
    # Redirect to setup if no users exist
    if not auth_service.has_users():
        return redirect(url_for('main.show_setup'))
        
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    return render_template("login.html")

@authorize_any()
@bp.route("/chat", methods=["POST"])
def chat():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    msg = data.get("message", "").strip()
    persona_id = data.get("persona_id")
    conversation_id = data.get("conversation_id")
    user_id = session['user_id']
    if not persona_id:
        return jsonify({"error": "Missing persona selection"}), 400
    # Conversation logic
    if not conversation_id:
        conv = Conversation(id=None, user_id=user_id)
        conv.save()
        conversation_id = conv.id
        # Save summary for new conversation
        if msg:
            summary = current_app.ai_client.summarize_text(msg)
            conv.summary = summary
            conv.save()
    else:
        conv = Conversation.get_by_id(conversation_id)
        if not conv or conv.user_id != user_id:
            return jsonify({"error": "Invalid conversation"}), 400
        # If this is the first user message, save summary
        messages = Message.get_by_conversation_id(conversation_id)
        user_msgs = [m for m in messages if m.sender == 'user']
        if len(user_msgs) == 0 and msg:
            summary = current_app.ai_client.summarize_text(msg)
            conv.summary = summary
            conv.save()
    # Save user message
    user_msg = Message(id=None, conversation_id=conversation_id, sender='user', content=msg)
    user_msg.save()
    # Get bot response
    response = current_app.ai_client.get_chat_response(msg, int(user_id), int(persona_id), int(conversation_id) if conversation_id else None)
    # Save bot message
    bot_msg = Message(id=None, conversation_id=conversation_id, sender='assistant', content=response)
    bot_msg.save()
    user = User.get_by_id(user_id)
    username = user.get_username() if user else 'unknown'
    logging.info(f"{username} - persona:{persona_id}: {msg} => {response}")
    return jsonify({"response": response, "conversation_id": conversation_id})

@bp.route("/auth/login", methods=["POST"])
def login():
    # Redirect to setup if no users exist
    if not auth_service.has_users():
        return jsonify({"error": "Please complete initial setup"}), 403
        
    data = request.json
    username = data.get("username")
    password = data.get("password")
    remember = data.get("remember", False)
    
    success, message = auth_service.authenticate(username, password, remember)
    
    if success:
        return jsonify({"message": message})
    else:
        return jsonify({"error": message}), 401

@bp.route("/auth/logout", methods=["POST"])
def logout():
    # Get session token before clearing
    session_token = session.get('session_token')
    if session_token:
        auth_service.logout(session_token)
    else:
        session.clear()
    # If AJAX/fetch, return JSON, else redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json'] > request.accept_mimetypes['text/html']:
        return jsonify({"success": True, "redirect": url_for('main.show_login')})
    return redirect(url_for('main.show_login'))

@bp.route("/admin", methods=["GET", "POST"])
@authorize(['admin-parent'])
def admin():
    settings = Settings()
    message = None
    error = None
    censored_openai_key = ''
    openai_key = ApiKey.get_openai_key()
    if openai_key:
        censored_openai_key = openai_key[:12] + '*' * (max(0, len(openai_key) - 12))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_user":
            username = request.form.get("username")
            text_name = request.form.get("text_name")
            password = request.form.get("password")
            role = request.form.get("role")
            if not all([username, text_name, password, role]):
                error = "All user fields are required."
            else:
                password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                user = User(id=None, username=username, password_hash=password_hash, text_name=text_name, role=role)
                if user.save():
                    message = f"User '{username}' created successfully."
                else:
                    error = f"Failed to create user '{username}'."
        elif action == "set_instructions":
            instructions = request.form.get("system_instructions", "")
            settings.set_global_system_instructions(instructions)
            message = "Global system instructions updated."
        elif action == "set_openai_key":
            new_key = request.form.get("new_openai_api_key", "").strip()
            logging.info(f"Setting new OpenAI API starting with {new_key[:12]}")
            if new_key:
                if ApiKey.set_openai_key(new_key):
                    # Reload OpenAIClient with the new key
                    from app.core.ai_clients.openai_client import OpenAIClient
                    current_app.ai_client = OpenAIClient(banned_keywords=[])
                    message = "OpenAI API key updated."
                    censored_openai_key = new_key[:12] + '*' * (max(0, len(new_key) - 12))
                else:
                    error = "Failed to update OpenAI API key."
            else:
                error = "Please enter a new OpenAI API key."
    current_instructions = settings.get_global_system_instructions()
    return render_template("admin.html", user=User.get_by_id(session['user_id']), message=message, error=error, system_instructions=current_instructions, censored_openai_key=censored_openai_key)

@bp.route("/settings", methods=["GET", "POST"])
@authorize_any()
def settings_page():
    user = User.get_by_id(session['user_id'])
    if user.role not in ('admin-parent', 'user-parent'):
        return redirect(url_for('main.index'))
    settings = Settings()
    message = None
    error = None
    # Handle POST actions
    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_instructions":
            instructions = request.form.get("system_instructions", "")
            target_user_id = int(request.form.get("target_user_id", user.id))
            settings.set_child_instructions(target_user_id, instructions)
            message = "System instructions updated."
        elif action == "add_persona":
            name = request.form.get("persona_name")
            prompt = request.form.get("persona_prompt")
            if name and prompt:
                settings.add_persona(name, prompt)
                message = "Persona added."
            else:
                error = "Persona name and prompt required."
        elif action == "delete_persona":
            persona_id = int(request.form.get("persona_id"))
            settings.delete_persona(persona_id)
            message = "Persona deleted."
        elif action == "edit_persona":
            persona_id = int(request.form.get("persona_id"))
            name = request.form.get("persona_name")
            prompt = request.form.get("persona_prompt")
            if name and prompt:
                settings.edit_persona(persona_id, name, prompt)
                message = "Persona updated."
            else:
                error = "Persona name and prompt required."
        elif action == "add_banned_word":
            word = request.form.get("banned_word", "").strip()
            if word:
                if settings.add_banned_word(word):
                    message = f"Banned word '{word}' added."
                else:
                    error = f"Failed to add banned word '{word}'."
            else:
                error = "Please enter a word to ban."
        elif action == "delete_banned_word":
            banned_word_id = int(request.form.get("banned_word_id"))
            if settings.delete_banned_word(banned_word_id):
                message = "Banned word deleted."
            else:
                error = "Failed to delete banned word."
        elif action == "change_password":
            logging.info(f"Changing password for user: {user.username}")
            old_password = request.form.get("old_password")
            new_password = request.form.get("new_password") 
            new_password_confirm = request.form.get("new_password_confirm")
            if new_password != new_password_confirm:
                error = "Change Password Failed: New passwords do not match."
                logging.info(f"Change password failed, new passwords do not match")
            elif not bcrypt.checkpw(old_password.encode(), user.password_hash.encode()):
                error = "Change Password Failed: Old password is incorrect."
                logging.info(f"Change password failed, old password is incorrect")
            else:
                password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                user.password_hash = password_hash
                user.save()
                message = "Password changed successfully."
                logging.info(f"Password changed for user: {user.username}")
    # Load data for rendering
    system_instructions = settings.get_child_instructions(user.id)
    personas = settings.get_personas(None)  # global personas
    banned_words = BannedWord.get_all()
    # Get all children and their instructions
    children = []
    from app.core.model.user import User as UserModel
    for child in UserModel.get_all_children():
        children.append({
            'id': child.id,
            'username': child.username,
            'text_name': child.text_name,
            'system_instructions': settings.get_child_instructions(child.id)
        })
    return render_template("settings.html", user=user, system_instructions=system_instructions, personas=personas, children=children, banned_words=banned_words, message=message, error=error)

@bp.route('/conversations', methods=['GET'])
@authorize_any()
def get_conversations():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    user_id = session['user_id']
    # Get all conversations, sorted by started_at DESC (most recent first)
    conversations = Conversation.get_by_user_id(user_id)
    # Identify the latest conversation (most recent by started_at)
    latest_conv_id = conversations[0].id if conversations else None
    # Delete all empty conversations except the latest one
    for conv in conversations:
        if conv.id == latest_conv_id:
            continue
        messages = Message.get_by_conversation_id(conv.id)
        if not messages:
            conv.delete()
    # Reload conversations after deletion
    conversations = Conversation.get_by_user_id(user_id)
    summaries = []
    for conv in conversations:
        summary = conv.summary
        if not summary:
            # Only fetch messages and generate summary if missing
            messages = Message.get_by_conversation_id(conv.id)
            first_user_msg = next((m.content for m in messages if m.sender == 'user'), '')
            if first_user_msg:
                summary = current_app.ai_client.summarize_text(first_user_msg)
            else:
                summary = 'New Conversation'
            # Save summary to conversation
            conv.summary = summary
            conv.save()
        summaries.append({
            'id': conv.id,
            'started_at': conv.started_at,
            'snippet': summary
        })
    return jsonify({'conversations': summaries})

@bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@authorize_any()
def get_conversation_messages(conversation_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    conv = Conversation.get_by_id(conversation_id)
    if not conv or conv.user_id != session['user_id']:
        return jsonify({'error': 'Not found'}), 404
    messages = Message.get_by_conversation_id(conversation_id)
    return jsonify({'messages': [
        {'id': m.id, 'sender': m.sender, 'content': m.content, 'created_at': m.created_at} for m in messages
    ]})

@bp.route('/conversations', methods=['POST'])
@authorize_any()
def start_conversation():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    conv = Conversation(id=None, user_id=session['user_id'])
    conv.save()
    return jsonify({'id': conv.id})

@bp.route('/conversations/<int:conversation_id>/message', methods=['POST'])
@authorize_any()
def add_message(conversation_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.json
    sender = data.get('sender')
    content = data.get('content')
    if not sender or not content:
        return jsonify({'error': 'Missing sender or content'}), 400
    conv = Conversation.get_by_id(conversation_id)
    if not conv or conv.user_id != session['user_id']:
        return jsonify({'error': 'Not found'}), 404
    msg = Message(id=None, conversation_id=conversation_id, sender=sender, content=content)
    msg.save()
    return jsonify({'success': True, 'id': msg.id})

@bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
@authorize_any()
def delete_conversation(conversation_id):
    if 'user_id' not in session:
        logging.error(f"Failed to delete conversation {conversation_id} - user not authenticated")
        return jsonify({'error': 'Not authenticated'}), 401
    conv = Conversation.get_by_id(conversation_id)
    if not conv or conv.user_id != session['user_id']:
        logging.error(f"Failed to delete conversation {conversation_id} - not found or not authorized")
        return jsonify({'error': 'Not found or not authorized'}), 404
    if conv.delete():
        logging.info(f"Deleted conversation {conversation_id}")
        return jsonify({'success': True})
    else:
        logging.error(f"Failed to delete conversation {conversation_id}, unknown error")
        return jsonify({'error': 'Failed to delete conversation'}), 500

