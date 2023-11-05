import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')  # Fallback to default if not set
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///getTrivvy.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False