from flask import render_template, request, redirect, session, url_for, flash
from app import app,google
# Import objek db dan User dari file models.py
from models import db,User
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from dotenv import load_dotenv
import random
#import os
#from werkzeug.security import compare_digest


# Route untuk halaman home
@app.route('/home')  
def home():
    return render_template('index.html')  

@app.route('/blog')  
def blog():
    return render_template('blog.html')  

@app.route('/services')  
def services():
    return render_template('services.html')  

@app.route('/about')  
def about():
    return render_template('about.html') 
 
# Route untuk registrasi pengguna
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        if password == confirm_password:
            new_user = User(email=email)
            scrypt_config = {'rounds': 16, 'block_size': 8, 'parallelism': 1}
            new_user.set_password(password, scrypt_config=scrypt_config)
            db.session.add(new_user)
            db.session.commit()

            # Kirim email aktivasi
            activation_code = ''.join(random.choices('0123456789', k=6))
            if send_activation_email(email, activation_code):
                new_user.activation_code = activation_code
                db.session.commit()
                flash('Registrasi berhasil! Kode aktivasi telah dikirim ke email sobat')
                return redirect(url_for('aktivasi_akun'))
            else:
                flash('Registrasi berhasil, tetapi gagal mengirim email aktivasi, coba lagi!')
                return redirect(url_for('register'))
        else:
            flash("Kata Sandi dan konfirmasi Kata sandi tidak cocok!")
            return redirect(url_for('register'))
    return render_template('register.html')

    
# Route untuk login pengguna
@app.route('/login', methods=['GET', 'POST'])  
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print("Email yang dimasukkan:", email)
        print("Password yang dimasukkan:", password)
        user = User.query.filter_by(email=email).first()
        print("User:", user)
        scrypt_config = {'rounds': 16, 'block_size': 8, 'parallelism': 1} 
        if user and user.check_password(password, scrypt_config=scrypt_config):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Email atau kata sandi tidak valid! Silakan coba lagi!')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/reset_password')
def reset_password():
    return render_template('reset_password.html')


# Route untuk autentikasi dengan OAuth
@app.route('/auth/google')
def auth_google():
    return google.authorize(callback=url_for('authorized', _external=True))

# Callback route setelah autentikasi berhasil (register dan login)
@app.route('/auth/callback')
def authorized():
    # Cek jika ada kesalahan dalam otentikasi
    if 'error' in request.args:
        return 'Otentikasi gagal: Alasan={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    # Dapatkan token dari respons
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Gagal mendapatkan token OAuth'

    # Simpan token ke sesi
    session['google_token'] = resp['access_token']

    # Dapatkan informasi pengguna dari Google
    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
    if user_info.status != 200:
        return 'Gagal mengambil informasi pengguna'

    # Dapatkan email dari informasi pengguna
    email = user_info.data.get('email')

    # Cek apakah pengguna sudah ada dalam database
    user = User.query.filter_by(email=email).first()
    if not user:
        # Jika tidak, tambahkan pengguna baru ke database
        new_user = User(email=email, oauth_provider='google', oauth_token=session['google_token'])
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    # Setel sesi user_id dengan ID pengguna
    session['user_id'] = user.id

    # Redirect ke halaman utama
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('home'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

# Route untuk aktivasi akun dengan kode OTP yang dikirimkan ke email
@app.route('/aktivasi_akun', methods=['GET', 'POST'])
def aktivasi_akun():
    if request.method == 'POST':
        email = request.form['email']  
        activation_code = request.form['otp'] 

        # Mencari pengguna berdasarkan email
        user = User.query.filter_by(email=email).first()

        # Jika pengguna ditemukan dan kode aktivasi cocok
        if user and user.activation_code == activation_code:
            # Aktivasi akun pengguna dengan menghapus kode aktivasi
            user.activation_code = None
            db.session.commit()
            flash('Akun Anda telah berhasil diaktivasi, silahkan login!')
            return redirect(url_for('login'))
        else:
            flash('Kode aktivasi tidak valid. silahkan coba lagi!')
            return redirect(url_for('aktivasi_akun'))

    return render_template('aktivasi_akun.html')


def send_activation_email(email, activation_code):
    smtp_host ='smtp.gmail.com'
    smtp_port =587
    smtp_username ='hellorandompedia@gmail.com'
    smtp_password ='ukkyxxgehonfsriy'
    
    msg = MIMEMultipart()
    msg['From'] = 'hellorandompedia@gmail.com'
    msg['To'] = email
    msg['Subject'] = 'Activation Code for Your Account'
    
    message = f'Your activation code is: {activation_code}'
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False