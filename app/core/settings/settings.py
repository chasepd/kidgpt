from app.core.config import get_db_config
import mysql.connector
from app.core.model.banned_word import BannedWord
from app.core.model.persona import Persona

class Settings:
    def __init__(self):
        self.db_config = get_db_config()

    def get_db_config(self) -> dict:
        return self.db_config

    def get_global_system_instructions(self) -> str:
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT setting_value FROM global_settings WHERE setting_key = %s", ("system_instructions",))
            row = cursor.fetchone()
            return row[0] if row else ""
        finally:
            cursor.close()
            connection.close()

    def set_global_system_instructions(self, instructions: str):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO global_settings (setting_key, setting_value)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
            """, ("system_instructions", instructions))
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    # --- Personas ---
    def get_personas(self, _):
        return [vars(p) for p in Persona.get_all()]

    def add_persona(self, name, system_prompt):
        p = Persona(id=None, name=name, system_prompt=system_prompt)
        return p.save()

    def delete_persona(self, persona_id):
        p = Persona.get_by_id(persona_id)
        if p:
            return p.delete()
        return False

    def edit_persona(self, persona_id, name, system_prompt):
        p = Persona.get_by_id(persona_id)
        if p:
            p.name = name
            p.system_prompt = system_prompt
            return p.save()
        return False

    # --- Banned Words ---
    def get_banned_words(self):
        return [vars(w) for w in BannedWord.get_all()]

    def add_banned_word(self, word):
        bw = BannedWord(id=None, word=word)
        return bw.save()

    def delete_banned_word(self, banned_word_id):
        connection = None
        cursor = None
        bw = BannedWord.get_by_id(banned_word_id)
        if bw:
            try:
                db_config = get_db_config()
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute("DELETE FROM banned_words WHERE id = %s", (banned_word_id,))
                connection.commit()
                return True
            except Exception as e:
                print(f"Error deleting banned word: {e}")
                return False
            finally:
                if cursor is not None:
                    cursor.close()
                if connection is not None and connection.is_connected():
                    connection.close()
        return False

    # --- Per-child system instructions ---
    def get_child_instructions(self, child_id):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT system_instructions FROM user_model_settings WHERE user_id = %s", (child_id,))
            row = cursor.fetchone()
            return row[0] if row else ""
        finally:
            cursor.close()
            connection.close()

    def set_child_instructions(self, child_id, instructions):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO user_model_settings (user_id, system_instructions)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE system_instructions = VALUES(system_instructions)
            """, (child_id, instructions))
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    # --- Child Personas Assignment ---
    def get_child_persona_ids(self, child_id):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT persona_id FROM child_personas WHERE child_user_id = %s", (child_id,))
            return [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()
            connection.close()

    def set_child_personas(self, child_id, persona_ids):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM child_personas WHERE child_user_id = %s", (child_id,))
            for persona_id in persona_ids:
                cursor.execute("INSERT INTO child_personas (child_user_id, persona_id) VALUES (%s, %s)", (child_id, persona_id))
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def create_blank_instructions(self, user_id):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT IGNORE INTO user_model_settings (user_id, system_instructions) VALUES (%s, '')", (user_id,))
            connection.commit()
        finally:
            cursor.close()
            connection.close()

