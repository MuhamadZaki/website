from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import scrypt

# Membuat objek SQLAlchemy
db = SQLAlchemy()

# Fungsi untuk menginisialisasi objek db dengan aplikasi Flask
def init_db(app):
    db.init_app(app)

# Definisi model User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(100), unique=True, nullable=False)  
    password_hash = db.Column(db.String(128)) 
    oauth_provider = db.Column(db.String(50))
    oauth_token = db.Column(db.String(200))
    activation_code = db.Column(db.String(10))
    

    def set_password(self, password, scrypt_config=None):
        if scrypt_config:
            self.password_hash = scrypt.hash(password, **scrypt_config)
        else:
            pass
            #self.password_hash = generate_password_hash(password)

    def check_password(self, password, scrypt_config=None):
        if scrypt_config:
            return scrypt.verify(password, self.password_hash)
        else:
            pass
            #return check_password_hash(self.password_hash, password)
        
    # Representasi string dari objek User
    def __repr__(self):
        return '<User %r>' % self.email