from flask_socketio import emit, SocketIO, join_room
from flask import request,g,jsonify
from ..database import get_db

# ...
socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('fetch_response')
def handle_message(data):
    print('Send message from client:', data['NewResponse'])
    # try:
    #     data = request.json
    # except:
    #     return jsonify({"error":"Please enter valid json formot"}),400
    # content = data['content']
    user_id = data['userId']
    content = data['NewResponse']
    status = "Online"
    
    db = get_db()
    cursor = db.cursor()
    
    # Assuming 'tbl_messages' is the table to store messages
    cursor.execute(
        'INSERT INTO tbl_messages (content, user_id, status) VALUES (%s, %s, %s)',
        (content, user_id, status)
    )
    
    db.commit()
    db.close()
    
    # Broadcast the message to all connected clients
    socketio.emit('fetch_response', data)
    return jsonify({"message": "Message sent successfully!"})

@socketio.on('start_typing')
def handle_message_t(data):
    print('start typing from client:', data)
    
    # Broadcast the message to all connected clients
    socketio.emit('start_typing', data)

@socketio.on('stop_typing')
def handle_message_s(data):
    print('stop typing from client:', data)
    
    # Broadcast the message to all connected clients
    socketio.emit('stop_typing', data)

@socketio.on("join_room")
def handle_join_room_event(data):
    print("{} has joined the room {}".format(data['username'], data['roomid']))
    join_room(data['roomid'])
    socketio.emit('join_room_announcement', data)