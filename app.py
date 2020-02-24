from flask import Flask, jsonify, g

from flask_cors import CORS

from flask_login import LoginManager 

from resources.users import users
# from resources.books import books
# from resources.favorites import favorites
import models

DEBUG = True
PORT= 8000


app = Flask(__name__)


app.secret_key = 'Juice world'
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
	return jsonify(
		data={
			'error':'User not logged in'
		}, 
		message='You must be logged in to access that',
		status=401
		), 401


CORS(users, origins=['http://localhost:3000'], supports_credentials=True)
# CORS(books, origins=['http://localhost:3000'], supports_credentials=True)
# CORS(favorites, origins=['http://localhost:3000'], supports_credentials=True)


app.register_blueprint(users, url_prefix='/api/v1/users')
# app.register_blueprint(books, url_prefix='/api/v1/books')
# app.register_blueprint(favorites, url_prefix='/api/v1/favorites')


@app.before_request
def before_request():
	g.db= models.DATABASE
	g.db.connect()


@app.after_request
def after_request(response):
	g.db.close()
	return response



if __name__ == '__main__':
	models.initialize()
	app.run(debug=DEBUG, port=PORT)

