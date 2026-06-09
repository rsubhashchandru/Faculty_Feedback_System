import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_123')
    
    # This string routes your app straight to your live Railway cloud database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'mysql+pymysql://root:GtSSbCXDZMAgesroYPppmYeymexpxPHA@acela.proxy.rlwy.net:18523/railway'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False