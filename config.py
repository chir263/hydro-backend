import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    API_TITLE = 'Flask API Template'
    API_VERSION = '1.0'