import jwt
import datetime

SECRET_KEY = 'supersecretkey'  # For testing only. Store securely in production.

def generate_jwt(payload, expires_in_minutes=60):
    payload_copy = payload.copy()
    payload_copy['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)
    token = jwt.encode(payload_copy, SECRET_KEY, algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
