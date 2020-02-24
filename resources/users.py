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
