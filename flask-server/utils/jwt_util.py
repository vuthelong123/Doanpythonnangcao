# pyrefly: ignore [missing-import]
import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from config import Config

def gen_token(username=None, password=None):
    payload = {
        'username': username,
        'password': password,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=Config.JWT_EXPIRES_MINUTES)
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
    return token
    
def check_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token') or request.headers.get('authorization')
        if not token:
            return jsonify({'success': False, 'message': 'Token không hợp lệ'}), 401
        try:
            jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Hết hạn token'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token không hợp lệ'}), 401
        return f(*args, **kwargs)
    return decorated
