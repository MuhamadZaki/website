"""IMPORT MODUL FLASK UNTUK MEMBUAT WEBAPP"""
from flask import Flask
#from flask_migrate import Migrate
"""IMPORT KONFIGURASI APLIKASI DARI FILE CONFIG"""
from config import Config
"""IMPORT OBJEK DATABASE DAN FUNGSI INISIALISASI DATABASE DARI MODELS"""
from models import db, init_db
"""IMPORT MODUL OAUTH DARI FLASK_OAUTHLIB UNTUK AUTENTIKASI OAUTH"""
from flask_oauthlib.client import OAuth
#import os

"""INISIALISASI OBJEK FLASK DENGAN MENYERTAKAN FOLDER STATIS DAN TEMPLATE"""
app = Flask(__name__, static_folder='resources/static', template_folder='resources/templates')

"""KONFIGURASI APLIKASI MENGGUNAKAN OBJEK CONFIG"""
app.config.from_object(Config)

"""INISIALISASI DATABASE DENGAN APLIKASI FLASK"""
init_db(app)


#migrate = Migrate(app, db)

"""BUAT TABEL-TABEL DATABASE JIKA BELUM ADA"""
with app.app_context():
    db.create_all()

"""SET KUNCI RAHASIA APLIKASI"""
app.secret_key = Config.SECRET_KEY

"""KONFIGURASI OAUTH UNTUK PENYEDIA GOOGLE"""
google_client_id = '1059324365498-4n4tkg58mi9ufl4gk1jfs0p71dfc6vqf.apps.googleusercontent.com'
google_client_secret = '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'
google_redirect_uri = 'https://127.0.0.1:5000/auth/callback'

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=google_client_id,
    consumer_secret=google_client_secret,
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',#'email'
    },
    base_url=None,
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth'
    
)


"""IMPORT ROUTES DARI FILE ROUTES"""
from routes import *

"""MENJALAKAN APLIKASI JIKA FILE INI DIJALANKAN SEBAGAI SCRIPT UTAMA"""
if __name__ == '__main__':
    """MENJALANKAN APLIKASI FLASK DENGAN MENGGUNAKAN SSL CONTEXT UNTUK HTTPS"""
    app.run(ssl_context=('cert.pem', 'key.pem'))