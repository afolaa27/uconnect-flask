import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, g, redirect, session
from flask_cors import CORS
from flask_login import LoginManager, login_user
from flask_socketio import emit, join_room
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized

from extensions import socketio

from resources.users import users
from resources.books import books
from resources.notifications import notifications
from resources.favorites import favorites
from resources.offers import offers
from resources.ai import ai
import models

DEBUG = True
PORT = 8000
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

if DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

socketio.init_app(app, cors_allowed_origins=['http://localhost:3000', 'https://uconnect-react-app.herokuapp.com'])

CORS(app, origins=['http://localhost:3000', 'https://uconnect-react-app.herokuapp.com'], supports_credentials=True)

# ── Google OAuth ──────────────────────────────────────────────────────────────
google_bp = make_google_blueprint(
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    scope=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
)
app.register_blueprint(google_bp, url_prefix='/api/v1/auth')


@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    if not token:
        return redirect(FRONTEND_URL)
    resp = blueprint.session.get('https://www.googleapis.com/oauth2/v2/userinfo')
    if not resp.ok:
        return redirect(FRONTEND_URL)
    info = resp.json()
    email = info['email'].lower()
    is_new = False
    try:
        user = models.User.get(models.User.email == email)
    except models.DoesNotExist:
        is_new = True
        base = info.get('given_name', email.split('@')[0]).lower().replace(' ', '_')
        username = base
        i = 1
        while True:
            try:
                models.User.get(models.User.username == username)
                username = f'{base}{i}'
                i += 1
            except models.DoesNotExist:
                break
        user = models.User.create(
            username=username, email=email, password='', age=18, school=info.get('hd', ''),
        )
    login_user(user, remember=True)
    session['is_new_user'] = is_new
    session['just_logged_in'] = True
    return redirect(FRONTEND_URL)
# ─────────────────────────────────────────────────────────────────────────────

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify(data={'error': 'User not logged in'}, message='You must be logged in', status=401), 401


app.register_blueprint(users, url_prefix='/api/v1/users')
app.register_blueprint(books, url_prefix='/api/v1/books')
app.register_blueprint(favorites, url_prefix='/api/v1/favorites')
app.register_blueprint(notifications, url_prefix='/api/v1/notifications')
app.register_blueprint(offers, url_prefix='/api/v1/offers')
app.register_blueprint(ai)

if 'ON_HEROKU' in os.environ:
    app.config.update(SESSION_COOKIE_SECURE=True, SESSION_COOKIE_SAMESITE='None')


@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


if 'ON_HEROKU' in os.environ:
    print('\non heroku!')
    models.initialize()


# ── SocketIO event handlers ───────────────────────────────────────────────────
@socketio.on('join_offer')
def on_join_offer(data):
    join_room(f"offer_{data['offer_id']}")


@socketio.on('join_user_room')
def on_join_user(data):
    user_id = data.get('user_id')
    if user_id:
        join_room(f'user_{user_id}')


@socketio.on('send_message')
def on_message(data):
    offer = models.Offer.get_by_id(data['offer_id'])
    msg = models.Message.create(
        offer=offer,
        sender=data['sender_id'],
        body=data['body']
    )
    emit('new_message', {
        'id': msg.id,
        'body': msg.body,
        'sender_id': data['sender_id'],
        'sender_username': data['sender_username'],
        'created_at': msg.created_at.isoformat()
    }, room=f"offer_{data['offer_id']}")
# ─────────────────────────────────────────────────────────────────────────────


if __name__ == '__main__':
    models.initialize()
    socketio.run(app, debug=DEBUG, port=PORT, allow_unsafe_werkzeug=True)
