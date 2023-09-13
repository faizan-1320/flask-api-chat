import datetime
import jwt
key = "\/this\/is\/secret\/key\/"

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0,seconds=59),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return str(jwt.encode(
            payload,
            key,
            algorithm='HS256'
        ))
    except Exception as e:
        return e
    
def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, key,algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        a = False
        return a
    except jwt.InvalidTokenError: 
        b = False
        return b