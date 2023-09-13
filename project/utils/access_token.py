from flask import jsonify
def check_token(user_id):
    try:
        get_user_id = user_id.split('/')
    except:
        return jsonify({"error":'Token is not valid'}),401
    return get_user_id