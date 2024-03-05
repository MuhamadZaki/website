from flask import Flask
#from flask_migrate import Migrate
from config import Config
from models import db, init_db
from flask_oauthlib.client import OAuth
#import os

# Inisialisasi aplikasi Flask
app = Flask(__name__, static_folder='resources/static', template_folder='resources/templates')


# Mengatur konfigurasi aplikasi dari objek Config yang telah dibuat sebelumnya
app.config.from_object(Config)

# Menginisialisasi aplikasi dengan ekstensi SQLAlchemy
init_db(app)

# Integrasi Flask-Migrate di sini
#migrate = Migrate(app, db)

# Membuat tabel-tabel di database jika belum ada
with app.app_context():
    db.create_all()

# Menetapkan kunci rahasia
app.secret_key = Config.SECRET_KEY

# Konfigurasi OAuth
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


# Mengimpor model dan routes setelah inisialisasi database
from routes import *

# Menjalankan aplikasi Flask dalam mode debug
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))