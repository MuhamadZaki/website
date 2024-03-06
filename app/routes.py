"""IMPORT MODUL YANG DIPERLUKAN DARI FLASK"""
from flask import render_template, request, redirect, session, url_for, flash
"""IMPORT INSTANCE APP FLASK DAN KONFIGURASI GOOGLE OAuth"""
from app import app,google
"""IMPORT DATABASE DAN MODEL USER UNTUK INTERAKSI DENGAN DATABASE"""
from models import db,User
"""IMPORT MODUL UNTUK PENGIRIMAN EMAIL"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
"""IMPORT MODUL UNTUK STRING ACAK"""
import random, string, os

"""ROUTE UNTUK HALAMAN UTAMA"""
@app.route('/home')  
def home():
    return render_template('home.html')

@app.route('/post')
def post():
    return render_template('post.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


 
"""ROUTE UNTUK REGISTRASI PENGGUNA, MENDUKUNG METODE GET DAN POST"""
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        """AMBIL DATA DARI FORM YANG DISUBMIT"""
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        """PERIKSA APAKAH PASSWORD DAN KONFIRMASI PASSWORD YANG COCOK"""
        if password == confirm_password:

            """BUAT OBJEK USER BARU DAN ATUR PASSWORD"""
            new_user = User(email=email)
            scrypt_config = {'rounds': 16, 'block_size': 8, 'parallelism': 1}
            new_user.set_password(password, scrypt_config=scrypt_config)

            """TAMBAHKAN USER BARU KE SESI DATABASE DAN COMMIT"""
            db.session.add(new_user)
            db.session.commit()

            """HASILKAN KODE AKTIVASI ACAK"""
            activation_code = ''.join(random.choices('0123456789', k=6))

            """KIRIM EMAIL AKTIVASI"""
            if send_activation_email(email, activation_code):

                """JIKA EMASIL BERHASIL TERKIRIM, UPDATE USER DENGAN KODE AKTIVASI DAN COMMIT PERUBAHAN"""
                new_user.activation_code = activation_code
                db.session.commit()
                flash('Registrasi berhasil! Kode aktivasi telah dikirim ke email sobat!')
                return redirect(url_for('aktivasi_akun'))
            else:
                flash('Registrasi berhasil, tetapi gagal mengirim email aktivasi, coba lagi!')
                return redirect(url_for('register'))
        else:
            flash("Kata Sandi dan konfirmasi Kata sandi tidak cocok!")
            return redirect(url_for('register'))
    return render_template('register.html')

"""ROUTE UNTUK LOGIN PENGGUNA, MENDUKUNG METODE GET DAN POST"""    
@app.route('/login', methods=['GET', 'POST'])  
def login():
    if request.method == 'POST':

        """AMBIL DATA LOGIN DARI FORM"""
        email = request.form['email']
        password = request.form['password']

        """DEBUG DENGAN PRINT"""
        print("Email yang dimasukkan:", email)
        print("Password yang dimasukkan:", password)

        """QUERY DATABASE UNTUK MENCARI USER BERDASARKAN EMAIL"""
        user = User.query.filter_by(email=email).first()
        """DEBUG DENGAN PRINT"""
        print("User:", user)

        """PRIKSA APAKAH USER ADA DAN PASSWORD BENAR"""
        scrypt_config = {'rounds': 16, 'block_size': 8, 'parallelism': 1} 
        if user and user.check_password(password, scrypt_config=scrypt_config):
    
            """SET SESI USER DAN TAMPILAN PESAN SUKSES"""
            session['user_id'] = user.id
            flash('Login berhasil!')
            return redirect(url_for('home'))
        else:
            flash('Email atau kata sandi tidak valid! Silakan coba lagi!')
            return redirect(url_for('login'))
    return render_template('login.html')

"""ROUTE UNTUK RESET PASSWORD"""
@app.route('/reset_password')
def reset_password():
    return render_template('reset_password.html')

"""ROUT UNTUK MEMULAI ALUR OAUTH GOOGLE"""
@app.route('/auth/google')
def auth_google():
    return google.authorize(callback=url_for('authorized', _external=True))

"""FUNGSI UNTUK MENGHASILKAN KODE AKTIVASI ACAK"""
def generate_activation_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

"""ROUTE UNTUK MENANGANI CALLBACK DARI GOOGLE"""
@app.route('/auth/callback')
def authorized():
    if 'error' in request.args:

        """TANGANI KESALAHAN OAUTH"""
        return 'Otentikasi gagal: Alasan={} error={}'.format(request.args['error_reason'], request.args['error_description'])
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:

        """TANGANI KEGAGALAN DALAM MENDAPATKAN TOKEN OAUTH"""
        return 'Gagal mendapatkan token OAuth'
    session['google_token'] = resp['access_token']
    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
    if user_info.status != 200:

        """TANGANI KEGAGALAN DALAM MENDAPATKAN INFO PENGGUNA"""
        return 'Gagal mengambil informasi pengguna!'

    email = user_info.data.get('email')

    """PERIKSA APAKAH USER ADA, JIKA TIDAK MAKA BUAT USER BARU"""
    user = User.query.filter_by(email=email).first()
    if not user:
        activation_code = generate_activation_code()
        new_user = User(email=email, oauth_provider='google', oauth_token=session['google_token'], activation_code=activation_code)
        db.session.add(new_user)
        db.session.commit()
        send_activation_email(email, activation_code)

        flash('Silakan cek email Anda untuk kode aktivasi dan aktivasi akun Anda.')
        return render_template('aktivasi_akun.html', email=email)

    session['user_id'] = user.id
    return redirect(url_for('home'))

"""ROUTE UNTUK LOGOUT PENGGUNA, MENGHAPUS SESI"""
@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('home'))

"""FUNGSI GETTER UNTUK TOKEN OAUTH GOOGLE UNTUK FLASK-OAUTHLIB"""
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

"""ROUTE UNTUK AKTIVASI AKUN, MENDUKUNG METODE GET DAN POST"""
@app.route('/aktivasi_akun', methods=['GET', 'POST'])
def aktivasi_akun():
    if request.method == 'POST':

        """AMBIL DATA FORM UNTUK AKTIVASI"""
        email = request.form['email']  
        activation_code = request.form['otp']

        """QUERY DATABASE UNTUK MENCARI USER BERDASARKAN EMAIL""" 
        user = User.query.filter_by(email=email).first()

        """PERIKSA APAKAH USER ADA DAN KODE AKTIVASI COCOK"""
        if user and user.activation_code == activation_code:

            """JIKA COCOK, HAPUS KODE AKTIVASI DAN COMMIT PERUBAHAN"""
            user.activation_code = None
            db.session.commit()
            flash('Akun Anda telah berhasil diaktivasi, silahkan login!')
            return redirect(url_for('login'))
        else:
            flash('Kode aktivasi tidak valid. silahkan coba lagi!')
            return redirect(url_for('aktivasi_akun'))

    return render_template('aktivasi_akun.html')

"""FUNGSI UNTUK MENGIRIM EMAIL AKTIVASI"""
def send_activation_email(email, activation_code):
    smtp_host ='smtp.gmail.com'
    smtp_port =587
    smtp_username ='hellorandompedia@gmail.com'
    smtp_password ='ukkyxxgehonfsriy'
    
    """MEMBUAT OBJEK PESAN EMAIL"""
    msg = MIMEMultipart()
    msg['From'] = 'hellorandompedia@gmail.com'
    msg['To'] = email
    msg['Subject'] = 'Kode aktivasi untuk akun sobat!'
    
    """ISI PESAN EMAIL"""
    message = f'Your activation code is: {activation_code}'
    msg.attach(MIMEText(message, 'plain'))

    try:
        """MEMBUAT KONEKSI SMTP DAN MENGIRIM PESAN"""
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            return True
    except Exception as e:
        """TANGANI KESALAHAN SAAT MENGIRIM EMAIL"""
        print(f"Kesalahan pengiriman email!: {e}")
        return False