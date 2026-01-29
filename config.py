import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    DEBUG = True
    
    # JWT Configuration
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
