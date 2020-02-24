import models

from flask import Blueprint, request, jsonify 
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user
from playhouse.shortcuts import model_to_dict

users= Blueprint('users', 'users')


@users.route('/register', methods=['POST'])
def register_user():
	payload = request.get_json()
	payload['email'] = payload['email'].lower()
	try:
		models.User.get(models.User.email == payload['email'] and models.User.username == payload['username'])
		return jsonify(data={},
			message="User with email or username already exists",
			status=401),401
	except models.DoesNotExist:
		created_user = models.User.create(
			username= payload['username'],
			email=payload['email'],
			password=generate_password_hash(payload['password']),
			age= payload['age'],
			school= payload['school'],
			longitude=payload['longitude'],
			latitude= payload['latitude']
			)
		login_user(created_user)
		user_dict = model_to_dict(created_user)
		user_dict.pop('password')
	return jsonify(
		data= user_dict,
		message='created an account',
		status=201),201


@users.route('/login', methods=['POST'])
def login(): 
	payload = request.get_json()
	try:
		user = models.User.get(models.User.username == payload['username'])
		user_dict = model_to_dict(user)

		check_password = check_password_hash(user_dict['password'],payload['password'])
		if check_password:
			login_user(user)
			user_dict.pop('password')


			# print(user_dict['latitude'])
			# print(type(user_dict['latitude']))
			# user_dict.pop('latitude')
			# user_dict.pop('longitude')
			user_dict['latitude']=str(user_dict['latitude'])
			user_dict['longitude']=str(user_dict['longitude'])
			print(type(user_dict['longitude']))
			return jsonify(
				data=user_dict,
				message='logged in',
				status=200
				), 200

	except models.DoesNotExist:
		return jsonify(
			data={},
			message='email or password incorrect',
			status=401),401


@users.route('loggedin', methods=['GET'])
def get_logged_in_user():
	if not current_user.is_authenticated:
		return jsonify(
			data={},
			message='No user logged in',
			status= 401),401
	else :
		user_dict = model_to_dict(current_user)
		user_dict.pop('password')
		user_dict['latitude']=str(user_dict['latitude'])
		user_dict['longitude']=str(user_dict['longitude'])
		
		return jsonify(
			data=user_dict,
			message='this is the current logged in user',
			status=200),200

@users.route('logout', methods=['GET'])
def logout():
	logout_user()
	return jsonify(
		data={},
		message="Youve been logged out",
		status=200),200

