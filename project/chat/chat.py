from flask import Blueprint,request,jsonify
from ..database import get_db
from flask_jwt_extended import jwt_required,get_jwt_identity
from project.utils import access_token
import os
from datetime import datetime, timedelta
from collections import OrderedDict

chat_bp = Blueprint('chat',__name__)

@chat_bp.route('/member-list')
@jwt_required()
def member_list():
    user_id = get_jwt_identity()
    get_user_id = access_token.check_token(user_id)
    if get_user_id[1] == os.environ['SECRET_KEY']:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id,username,profile_picture,phone_number FROM tbl_users WHERE is_active=1 AND is_delete=0 AND id!=%s',(get_user_id[0],))
        users = cursor.fetchall()
        # print(users)
        cursor.close()
        data = [{"id":i[0],"username":i[1],"profile_picture":i[2],"phone_number":i[3]} for i in users]
        # print("------------------------------------------------->",data)
        return jsonify({'member_list':data})
    
@chat_bp.post('/send-message')
def send_message():
    try:
        data = request.json
    except:
        return jsonify({"error":"Please enter valid json formot"}),400
    content = data.get('content')
    user_id = data.get('user_id')
    status = data.get('status')
    
    db = get_db()
    cursor = db.cursor()
    
    # Assuming 'tbl_messages' is the table to store messages
    cursor.execute(
        'INSERT INTO tbl_messages (content, user_id, status) VALUES (%s, %s, %s)',
        (content, user_id, status)
    )
    
    db.commit()
    db.close()
    
    return jsonify({"message": "Message sent successfully!"})

@chat_bp.get('/get-all-message')
def get_all_messages():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        'SELECT content, user_id, created_at, status FROM tbl_messages'
    )
    
    messages = cursor.fetchall()
    db.close()

    message_list = []
    for message in messages:
        message_dict = {
            "content": message[0],
            "sender": message[1],
            "time": message[2].strftime("%H:%M:%S"),
            "status": message[3],
        }
        message_list.append(message_dict)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    data = {
        "04/06/2021": message_list,
        "YESTERDAY": yesterday,
        "TODAY": today,
    }
    # data['YESTERDAY'] = data.get(yesterday, [])
    # data['TODAY'] = data.get(today, [])
    return jsonify({"messages": data})

@chat_bp.get('/get-message')
@jwt_required()
def get_messages():
    user_id = get_jwt_identity()
    get_user_id = access_token.check_token(user_id)
    if get_user_id[1] == os.environ['SECRET_KEY']:
    
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT content, user_id, created_at, status FROM tbl_messages WHERE user_id=%s',(get_user_id[0],))
        messages_from_db = cursor.fetchall()
        # print("This is message from db-------------->",messages_from_db)
        db.close()

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        messages = {"YESTERDAY": [],"TODAY": []}

        for message in messages_from_db:
            created_at = message['created_at']  # Assuming 'created_at' is already a datetime.datetime object

            message_date_get = created_at.date()
            message_date = str(message_date_get)
            message_time = created_at.strftime("%H:%M:%S")

            if message_date == str(today):
                messages["TODAY"].append({
                    'content': message['content'],
                    'sender': message['user_id'],
                    'time': message_time,
                    'status': message['status']
                })
            elif message_date == str(yesterday):
                messages["YESTERDAY"].append({
                    'content': message['content'],
                    'sender': message['user_id'],
                    'time': message_time,
                    'status': message['status']
                })
            else:
                # Messages from other dates
                if message_date not in messages:
                    messages[message_date] = []

                messages[message_date].append({
                    'content': message['content'],
                    'sender': message['user_id'],
                    'time': message_time,
                    'status': message['status']
                })

        print("This is Response : ----------------------->", {"message": messages})

        return jsonify({"messages": messages})
    else:
        return jsonify({"error":"Invalid Token"}),400