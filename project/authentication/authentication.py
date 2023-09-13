from flask import Blueprint,request,jsonify
from ..database import get_db
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import create_access_token
import os
import re
from project.utils import mail,expire
import random
from datetime import datetime


auth_bp = Blueprint('auth',__name__)

@auth_bp.post('/login')
def login():
    try:
        data = request.json
    except:
        return jsonify({"error":'Please enter valid json fromat.'}),400
    username = data.get('username')
    password = data.get('password')

    if not username:
        return jsonify({"error":'Please enter username.'}),400
    if not password:
        return jsonify({"error":'Please enter password.'}),400
        
    # Check if the user exists in the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT username,password,id FROM tbl_users WHERE is_active=1 AND is_delete=0 AND username=%s', (username,))
    user = cursor.fetchone()

    if user:
        check_password=check_password_hash(user[1],password)
        if check_password:
            access = create_access_token(identity=str(
                    user[2]) + '/' + os.environ['SECRET_KEY'])
            return jsonify({'message':"Login Succefully!",'user':user[0],"user_id":user[2],"access":access}),200
        else:
            return jsonify({'error':"Invalid password. Please enter valid password."}),400
    else:
        return jsonify({"error":'Invalid data. Please enter valid username.'}),400
    
@auth_bp.post('/sign-up')
def signup():
        try:
            data = request.json
        except:
            return jsonify({"error":'Please enter valid json fromat.'}),400
        # Get user input from the form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone_number = data.get('phone_number')
        if not username:
            return jsonify({"error":'Please enter username.'}),400
        if not email:
            return jsonify({"error":'Please enter email.'}),400
        if not password:
            return jsonify({"error":'Please enter password.'}),400
        if not phone_number:
            return jsonify({"error":'Please enter phone_number.'}),400
        PasswordReg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        
        # Regular expression for username (letters, numbers, underscores, 3-20 characters)
        # UsernameReg = "^[a-zA-Z0-9_]{3,20}$"
        
        # Compile and search the username regex
        # pat = re.compile(UsernameReg)
        # mat = re.search(pat, username)
        
        # Compile and search the password regex
        pat = re.compile(PasswordReg)
        mat = re.search(pat, password)
        # Email regex
        EmailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        
        if not re.fullmatch(EmailRegex, email):
            return jsonify({"error":'Please enter a valid email address.'}),400
        
        if not mat:
            return jsonify({"error":'Please enter a valid password (6-20 characters, at least one uppercase, one lowercase, one digit, and one special character).'}),400

        # Check if the username is already in use
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM tbl_users WHERE username=%s', (username,))
        username_exists = cursor.fetchone()[0]
        # print("-------------------->",username_exists)
        cursor.close()

        if username_exists:
            return jsonify({"error":'Username is already in use. Please use a different username.'}),400
        pwh_hash = generate_password_hash(password, salt_length=8, method='sha256')
        # Insert the user data into the database using a cursor
        cursor = db.cursor()
        cursor.execute('INSERT INTO tbl_users (username, email, password, phone_number) VALUES (%s, %s, %s, %s)', (username, email, pwh_hash, phone_number))
        db.commit()
        cursor.close()

        # Close the database connection
        db.close()

        # Redirect to a success page or perform any necessary actions
        return jsonify({"message":'SignUp Successfully!!'}),201

@auth_bp.post('/forgot-password')
def forgot_password():
    try:
        data = request.json
    except:
        return jsonify({"error":'Please enter valid json fromat.'}),400
    email = data.get('email')
    if not email:
        return jsonify({"error":'Please enter email.'}),400
    EmailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        
    if not re.fullmatch(EmailRegex, email):
        return jsonify({"error":'Please enter a valid email address.'}),400
    
    # Check if the email is already in use
    db = get_db()
    cursor = db.cursor(buffered=True)
    cursor.execute('SELECT email,id FROM tbl_users WHERE email=%s', (email,))
    email_exists = cursor.fetchone()
    # print("-------------------->",email_exists)

    if email_exists:
        is_expire = expire.expire_otp()
        otp = random.randint(1000, 9999)

        cursor.execute(
            "INSERT INTO tbl_otp(user_id, otp, is_expire) VALUES(%s,%s,%s)", (email_exists[1], otp, is_expire))
        db.commit()
        cursor.close()
        title = 'Your Forgot Password Otp is'
        body = f"{otp}"
        mail.user_mail_register(title, body, data.get('email'))
        return jsonify({"message":"Mail send!!","user_id":email_exists[1]}),200
    else:
        return jsonify({"error":"Email is not register!!"}),400
    
@auth_bp.patch('/verify-otp/<user_id>')
def verify_otp(user_id):
    try:
        data = request.json
    except:
        return jsonify({"error": "Please enter valid JSON format"}), 400

    if not data.get('otp'):
        return jsonify({'error': "Please Enter OTP"}), 400
    # print("_________________________________________________",type(data.get('otp')))

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT otp,user_id,is_expire,is_used FROM tbl_otp WHERE is_active=1 AND is_delete=0 AND otp=%s AND user_id=%s',
                   (data.get('otp'), user_id))
    otp = cursor.fetchone()
    # print("_________________________________________________",data.get('otp'))
    # print("_________________________________________________",user_id)
    # print("_________________________________________________",otp)
    cursor.close()
    if not otp:
        return jsonify({"error": "OTP Invaid"}), 400
    current_datetime = datetime.now()


    if otp[3] == 0:
        if current_datetime > otp[2]:
            return jsonify({"error": "OTP is expired"}), 400
        cursor = db.cursor()
        cursor.execute('UPDATE tbl_otp SET is_used=1 WHERE user_id=%s', (user_id,))
        db.commit()
        return jsonify({'message': "OTP verified!"}), 200
    else:
        return jsonify({"error":"OTP is used.Send another request!!"}),400

@auth_bp.patch('/update-password/<user_id>')
def update_passowrd(user_id):
    try:
        data = request.json
    except:
        return jsonify({"error":"Please enter valid json formot"}),400
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT password,id FROM tbl_users WHERE id=%s AND is_active=1 AND is_delete=0',(user_id,))
    user = cursor.fetchone()
    if user:
        if not data.get('password'):
            return jsonify({"error":"Please enter password"}),400
        update_hash = generate_password_hash(data.get('password'),salt_length=8,method='sha256')
        cursor.execute('UPDATE tbl_users SET password=%s WHERE id=%s',(update_hash,user_id))
        db.commit()
        return jsonify({"message":'Password Update Successfully!'}),200
    else:
        return jsonify({"error":"Enter valid data"}),400