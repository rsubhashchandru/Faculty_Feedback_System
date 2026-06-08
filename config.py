import os

class Config:
    # Secret key for signing session cookies securely
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-dev-key-12345'
    
    # Database configuration parameters
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'subhash8296424069'  # <-- Change this to your local MySQL password
    MYSQL_HOST = 'localhost'
    MYSQL_DB = 'faculty_feedback_db'
    
    # SQLAlchemy Connection String mapping
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False