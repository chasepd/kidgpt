"""
Application configuration settings
"""
import os

# Flask configuration
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "your-secret-key-here-please-change-in-production")

# OpenAI API configuration
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here") 