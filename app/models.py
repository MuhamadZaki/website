"""IMPORT MODUL SQLALCHEMY UNTUK INTERAKSI DENGAN DATABASE"""
from flask_sqlalchemy import SQLAlchemy
"""IMPORT FUNGSI HASH DARI WERKZEUG UNTUK MENGHASILKAN HASH DARI KATA SANDI"""
from werkzeug.security import generate_password_hash, check_password_hash
"""IMPORT MODUL HASH DARI PASSLIB UNTUK PENGGUNAAN ALGORITMA HASH KHUSUS SCRYPT"""
from passlib.hash import scrypt

from datetime import datetime

"""MEMBUAT OBJEK SQLALCHEMY"""
db = SQLAlchemy()

"""FUNGSI UNTUK MENGINISIALISASI OBJEK DB DENGAN APLIKASI FLASK"""
def init_db(app):
    db.init_app(app)

"""DEFINISI MODEL USER"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(100), unique=True, nullable=False)  
    password_hash = db.Column(db.String(128)) 
    oauth_provider = db.Column(db.String(50))
    oauth_token = db.Column(db.String(200))
    activation_code = db.Column(db.String(10)) # Hapus aja

    """METODE UNTUK MENGATUR PASSWORD PENGGUNA DENGAN OPSI KONFIGURASI SCRYPT"""
    def set_password(self, password, scrypt_config=None):
        if scrypt_config:
            """GUNAKAN ALGORITMA HASH SCRYPT JIKA KONFIGURASI DISEDIAKAN"""
            self.password_hash = scrypt.hash(password, **scrypt_config)
        else:
            pass
            """GUNAKAN ALGORITMA HASH BAWAAN WERKZEUG JIKA TIDAK ADA KONFIGURASI SCRYPT"""
            #self.password_hash = generate_password_hash(password)

    """METODE UNTUK MEMERIKSA KECOCOKAN PASSWORD PENGGUNA DENGAN OPSI KONFIGURASI SCRYPT"""
    def check_password(self, password, scrypt_config=None):
        if scrypt_config:
            """VERIFIKASI PASSWORD MENGGUNAKAN ALGORITMA HASH SCRYPT, JIKA KONFIGURASI DISEDIAKAN"""
            return scrypt.verify(password, self.password_hash)
        else:
            pass
        """VERIFIKASI PASSWORD MENGGUNAKAN ALGORITMA HASH BAWAAN WERKZEUG JIKA TIDAK ADA KONFIGURASI SCRYPT"""
            #return check_password_hash(self.password_hash, password)
        
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
        
    """REPRESENTASI STRING DARI OBJEK USER"""
    def __repr__(self):
        return '<User %r>' % self.email