import functools, os, uuid, re, pyotp, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    render_template_string, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from apu_blog.db import get_database

# Login Page Vulnerability - OTP Email Sender -> Specify the address and password here
otp_email = "PLACEHOLDER"
otp_email_password = "PLACEHOLDER"

blueprint = Blueprint('auth', __name__, url_prefix='/auth')

# @blueprint.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         profile_picture = "default.png"
#         database = get_database()
#         error = None
#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'
#         if error is None:
#             try:
#                 database.execute(
#                     'INSERT INTO user (username, password, profile_picture)'
#                     ' VALUES (?, ?, ?)',
#                     (username, password, profile_picture)
#                 )
#                 database.commit()
#             except database.IntegrityError:
#                 error = f'User {username} is already registered.'
#             else:
#                 return redirect(url_for('auth.login'))
#         flash(error)
#     return render_template('auth/register.html')

# Simple Implementation of Username Checks
def check_username_validity(username):
    error = None
    # 1. Only ASCII and Non-Space Characters are Allowed
    if not re.search(r'[a-zA-Z0-9\._]', username):
        error = "Only numbers, underscores, fullstops, and uppercase and lowercase characters allowed."
    # 2. Ensure username is 10 characters or more
    elif not len(username) >= 6:
        error = ("Your Username should have atleast 6 characters.")
    return error
    

# Simple Implementation of Password Checks
def check_password_complexity(password):
    error = None
    # 1. Only ASCII and Non-Space Characters are Allowed
    if re.search(r'[^!-~]', password):
        error = "Only Printable ASCII and Non-Space characters allowed."
    # 2. Ensure user password is 10 characters or more
    elif not len(password) >= 10:
        error = ("Your password must use 10 or more characters with a mix of"
            " uppercase and lowercase letters, numbers, and symbols."
            " Please ensure your password is more than 10 characters.")
    # 2. Ensure user include numbers
    elif not re.search(r'[0-9]', password):
        error = ("Your password must use 10 or more characters with a mix of"
            " uppercase and lowercase letters, numbers, and symbols."
            " Please ensure your password include numbers.")
    # 3. Ensure user include lowercase letters
    elif not re.search(r'[a-z]', password):
        error = ("Your password must use 10 or more characters with a mix of"
            " uppercase and lowercase letters, numbers, and symbols."
            " Please ensure your password include lowercase letters.")
    # 4. Ensure user include uppercase letters
    elif not re.search(r'[A-Z]', password):
        error = ("Your password must use 10 or more characters with a mix of"
            " uppercase and lowercase letters, numbers, and symbols."
            " Please ensure your password include uppercase letters.")
    # 5. Ensure user include Symbols
    elif not re.search(r'[^a-zA-Z0-9]', password):
        error = ("Your password must use 10 or more characters with a mix of"
            " uppercase and lowercase letters, numbers, and symbols."
            " Please ensure your password include symbols.")
    return error


@blueprint.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # 1. Get Username/Password/Database
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        profile_picture = "default.png"
        database = get_database()
        error = None
        # 2. Missing Username / Password
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        # 3. Check Username Validity
        if error is None:
            error = check_username_validity(username)
        # 4. Check Password Complexity
        if error is None:
            error = check_password_complexity(password)
        # 5. No error encountered, so save the user's account.
        if error is None:
            try:
                database.execute(
                    'INSERT INTO user (email_address, username, password, profile_picture)'
                    ' VALUES (?, ?, ?, ?)',
                    (email, username, generate_password_hash(password), profile_picture)
                )
                database.commit()
            except database.IntegrityError:
                error = f'User {username} is already registered.'
            else:
                return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')

# Login Page Vulnerability (SQLi + No Password Complexity Policy + Insecure Logic + Weak Authentication Mechanism)
# @blueprint.route('/login', methods=('GET', 'POST'))
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         database = get_database()
#         error = None
#         user = database.execute(
#             'SELECT * FROM user WHERE username = "{}" AND password = "{}"'.format(
#                 username, password
#             )
#         ).fetchone()
#         # Invalid Username/Password
#         if user is None:
#             error = 'Incorrect Credentials.'
#         # No Error, User can Log In
#         if error is None:
#             session.clear()
#             session['user_id'] = user['id']
#             return redirect(url_for('blog.index'))
#         flash(error)
#     return render_template('auth/login.html')

# Generate OTP Code - Login Page Vulnerability
def generate_otp(user):
    # Generate OTP
    totp = pyotp.TOTP(pyotp.random_base32())
    otp_code = totp.now()
    # Save to Database
    database = get_database()
    database.execute(
        'UPDATE user SET otp_code = ? WHERE id = ?',
        (otp_code, user['id'])
    )
    database.commit()
    # Send OTP to the person email
    print(otp_code)
    send_otp(otp_code, user)

# Send OTP Email  - Login Page Vulnerability
def send_otp(otp_code, user):
    sender_address = otp_email
    sender_password = otp_email_password
    receiver_address = user['email_address']
    mail_content = 'Your OTP Code is {}.'.format(str(otp_code))
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'APU Confession Page OTP Code'
    message.attach(MIMEText(mail_content,'plain'))
    session = smtplib.SMTP('smtp-mail.outlook.com', 587)
    session.starttls()
    session.login(sender_address, sender_password)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()

# Function to Update Database when user fail to authenticate with a Valid Username - Login Page Vulnerability
def fail_authentication(user_id):
    database = get_database()
    database.execute(
        'UPDATE user SET auth_attempt = auth_attempt + 1 WHERE id = ?', (user_id,)
    )
    database.commit()

# Sanitized Login Function - Login Page Vulnerability
@blueprint.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # 1. Get Username/Password/Database
        username = request.form['username']
        password = request.form['password']
        database = get_database()
        error = None
        # 2. Parameterized Database Query + Fixing the Logic
        user = database.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        # 3. Check number of fail attempts; More than 5 = Account Lockdown
        if user and user['auth_attempt'] > 5:
            error = 'Account is locked. Please wait around 20 minutes before retrying.'
        else:
            # 4. Wrong Username
            if not user:
                error = 'Invalid Username.'
            # 5. Wrong Password
            elif not check_password_hash(user['password'], password):
                error = 'Invalid Password.'
                fail_authentication(user['id'])
            # 6. Successful Authentication
            if error is None:
                session.clear()
                generate_otp(user)
                session['temp_user_id'] = user['id']
                return redirect(url_for('auth.two_factor_auth'))
        flash(error)
    return render_template('auth/login.html')

# Login Page Vulnerability - Add 2FA Mechanism
@blueprint.route('/two_factor_auth', methods=('GET', 'POST'))
def two_factor_auth():
    if request.method == 'POST':
        otp_code = "{}{}{}{}{}{}".format(
            request.form['first_otp'], request.form['second_otp'],
            request.form['third_otp'], request.form['fourth_otp'],
            request.form['fifth_otp'], request.form['sixth_otp']
        )
        user_id = session['temp_user_id']
        database = get_database()
        stored_otp_code = database.execute(
            'SELECT otp_code FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        if str(otp_code) == str(stored_otp_code['otp_code']):
            print('Pass')
            session.clear()
            session['user_id'] = user_id
            return redirect(url_for('blog.index'))
        else: 
            print('Fail')
            session.clear()
            flash('Incorrect OTP Code. Please relogin again.')
            return redirect(url_for('auth.login'))
    return render_template('auth/two_factor_auth.html')

@blueprint.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_database().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('blog.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@blueprint.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    if request.method == 'POST':
        password = request.form['password']
        error = None
        if not password:
            error = 'Password is required.'
        if password == g.user['password']:
            error = 'Old and new password cannot be the same.'
        if error is None:
            database = get_database()
            print(password)
            database.execute(
                'UPDATE user SET password = ? WHERE id = ?',
                (password, g.user['id'])
            )
            database.commit()
            session.clear()
            flash('Successfully changed your password. Please re-login to your account.')
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/profile.html')

# Unrestricted File Upload Vulnerability
# @blueprint.route('/profile_picture', methods=('GET', 'POST'))
# @login_required
# def profile_picture():
#     if request.method == "POST":
#         if 'file' not in request.files:
#             flash('No image selected.')
#             return redirect('profile.html')
#         file = request.files['file']
#         if file.filename == '':
#             flash('No selected image.')
#             return redirect(request.url)
#         if file:
#             filename = file.filename
#             print(filename)
#             print(current_app.config['PROFILE_PICTURE_FOLDER'])
#             file.save(os.path.join(current_app.config['PROFILE_PICTURE_FOLDER'], filename))
#             database = get_database()
#             # Update the User Profile Database
#             database.execute(
#                 'UPDATE user SET profile_picture = ? WHERE id = ?',
#                 (filename, g.user['id'])
#             )
#             database.commit()
#         return redirect(url_for('auth.profile'))
#     return render_template('auth/profile_picture.html')

# Sanitized for Unrestricted File Upload
@blueprint.route('/profile_picture', methods=('GET', 'POST'))
@login_required
def profile_picture():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No image selected.')
            return redirect('profile.html')
        file = request.files['file']
        if file.filename == '':
            flash('No selected image.')
            return redirect(request.url)
        if file:
            filename = file.filename
            file_extension = filename.rsplit('.', 1)[1].lower()
            if file_extension not in current_app.config['ALLOWED_PROFILE_PICTURE_FORMAT']:
                flash('Invalid File Format.')
                return redirect(request.url)
            # Remove Unsafe Character (Non-ASCII Chars and ..\ or ../)
            safe_filename = secure_filename(filename)
            # Generate Unique ID for Profile Picture > Prevent accidental overwriting
            unique_filename = "{}_{}".format(
                str(uuid.uuid4()), safe_filename
            )
            # Save the profile picture
            file.save(os.path.join(current_app.config['PROFILE_PICTURE_FOLDER'], unique_filename))
            # Update the User Profile Database
            database = get_database()
            database.execute(
                'UPDATE user SET profile_picture = ? WHERE id = ?',
                (unique_filename, g.user['id'])
            )
            database.commit()
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile_picture.html')