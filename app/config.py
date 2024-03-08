class Config:
    """KUNCI RAHASIA APLIKASI"""
    SECRET_KEY = ''

    """KONFIGURASI DATABASE"""
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/webapp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    """MODE DEBUG AKTIF"""
    DEBUG = True