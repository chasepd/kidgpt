from openai import OpenAI
import logging
from typing import Dict, List
from app.core.settings.settings import Settings
from app.core.model.banned_word import BannedWord
from app.core.model.api_key import ApiKey
from app.core.model.message import Message

class OpenAIClient:
    def __init__(self, banned_keywords: List[str] = None):
        api_key = ApiKey.get_openai_key()
        if not api_key:
            self.client = None
            self.api_key_missing = True
        else:
            self.client = OpenAI(api_key=api_key)
            self.api_key_missing = False
        self.settings = Settings()

    def get_banned_words(self):
        return [w.word for w in BannedWord.get_all()]

    def contains_banned(self, text: str, banned_keywords: List[str]) -> bool:
        text_lower = text.lower()
        return any(word in text_lower for word in banned_keywords)

    def moderate_content(self, text: str) -> bool:
        if self.api_key_missing or not self.client:
            logging.error("OpenAI API key is not set in the database.")
            return False
        resp = self.client.moderations.create(input=text)
        return resp.results[0].flagged

    def get_persona_prompt(self, persona_id, user_id):
        personas = self.settings.get_personas(user_id)
        for p in personas:
            if p['id'] == persona_id:
                return p['system_prompt']
        return "You are a helpful assistant."

    def get_chat_response(self, message: str, user_id: int, persona_id: int, conversation_id: int = None) -> str:
        if self.api_key_missing or not self.client:
            return "OpenAI API key is not set. Please ask an admin to add it in the Admin panel."
        banned_keywords = self.get_banned_words()
        if self.contains_banned(message, banned_keywords):
            return "Uh oh! I can't help with that."

        user_instructions = self.settings.get_child_instructions(user_id)
        persona_prompt = self.get_persona_prompt(persona_id, user_id)
        system_prompt = f"{persona_prompt}\n{user_instructions}" if user_instructions else persona_prompt

        conv = [
            {"role": "system", "content": system_prompt}
        ]
        # If conversation_id is provided, load full history
        if conversation_id:
            messages = Message.get_by_conversation_id(conversation_id)
            for m in messages:
                if m.sender == 'user':
                    conv.append({"role": "user", "content": m.content})
                elif m.sender == 'assistant':
                    conv.append({"role": "assistant", "content": m.content})
        else:
            conv.append({"role": "user", "content": message})

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conv
            )
            output = resp.choices[0].message.content
            if self.contains_banned(output, banned_keywords):
                return "Oops, I can't help with that."
            return output
        except Exception as e:
            logging.error(f"Error getting chat response: {str(e)}")
            return "Sorry, I encountered an error. Please try again."

    def summarize_text(self, text: str) -> str:
        """
        Use OpenAI to summarize the given text in 5 words or less.
        """
        if self.api_key_missing or not self.client:
            return "(No summary)"
        prompt = (
            "Summarize the following user request in 5 words or less. "
            "Be concise and clear.\nRequest: " + text + "\nSummary:"
        )
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes user requests in 5 words or less."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=15,
                temperature=0.5
            )
            summary = resp.choices[0].message.content.strip()
            # Remove any leading/trailing quotes or punctuation
            summary = summary.strip('"\' .')
            return summary
        except Exception as e:
            logging.error(f"Error summarizing text: {str(e)}")
            return "(No summary)" 