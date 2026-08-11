import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pickle-legends-admin-super-secret-key-2026'
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    DEBUG = True
