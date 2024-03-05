class Config:
    # Kunci rahasia untuk sesi
    SECRET_KEY = 'kumispenggoda'

    # Konfigurasi database
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/webapp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mode debug aktif
    DEBUG = True