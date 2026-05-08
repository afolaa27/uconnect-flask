import os
from itsdangerous import URLSafeTimedSerializer

def make_token(user_id):
    s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    return s.dumps(str(user_id), salt='auth')

def decode_token(token):
    s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    try:
        return int(s.loads(token, salt='auth', max_age=60 * 60 * 24 * 30))
    except Exception:
        return None
