import os

# Get the database URL — use cloud DB on Vercel, local MySQL for development
db_url = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:subhash8296424069@localhost:3306/faculty_feedback_db'
)

# Fix: some cloud providers (Railway) give mysql:// instead of mysql+pymysql://
if db_url.startswith('mysql://'):
    db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_123')
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Connection pool settings — important for serverless (Vercel)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,   # Test connection before using it
        'pool_recycle': 280,     # Recycle connections every 280s (prevents timeouts)
        'pool_size': 1,          # Serverless: keep only 1 connection
        'max_overflow': 0,       # No extra connections
    }