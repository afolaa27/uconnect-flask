import models

from flask import Blueprint, request, jsonify, session, current_app
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from playhouse.shortcuts import model_to_dict

users= Blueprint('users', 'users')

#sign up route 
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
			)
		login_user(created_user)
		user_dict = model_to_dict(created_user)
		user_dict.pop('password')
		from app import make_token
		user_dict['token'] = make_token(created_user.id)
	return jsonify(
		data= user_dict,
		message='created an account',
		status=201),201


#login route
@users.route('/login', methods=['POST'])
def login(): 
	payload = request.get_json()
	try:
		user = models.User.get(models.User.username == payload['username'])
		user_dict = model_to_dict(user)

		check_password = check_password_hash(user_dict['password'],payload['password'])
		if check_password:

			login_user(user, remember=True)
			user_dict.pop('password')
			from app import make_token
			user_dict['token'] = make_token(user.id)
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

# #show all logged in user books
# @users.route('/', methods=['GET'])
# @login_required
# def index():
# 	current_user_books= [model_to_dict(book) for book in current_user.Books]
	
# 	for i in current_user_books:
# 		i['owner'].pop('age')
# 		i['owner'].pop('password')
# 		i['owner'].pop('email')
# 		i['owner'].pop('school')
# 		i['owner'].pop('id')
# 		i['image']['data']=str(i['image']['data'])
		 
	 
# 	return jsonify(
# 		data=current_user_books,
# 		message= 'Got current user books',
# 		status=200),200

#check who is logged in route
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
		user_dict['is_new'] = session.pop('is_new_user', False)
		user_dict['just_logged_in'] = session.pop('just_logged_in', False)

		return jsonify(
			data=user_dict,
			message='this is the current logged in user',
			status=200),200

#logout route
@users.route('logout', methods=['GET'])
def logout():
	logout_user()
	return jsonify(
		data={},
		message="Youve been logged out",
		status=200),200


#update profile route
@users.route('/profile', methods=['PUT'])
@login_required
def update_profile():
	payload = request.get_json()
	user = models.User.get_by_id(current_user.id)

	if 'username' in payload and payload['username']:
		user.username = payload['username']
	if 'email' in payload and payload['email']:
		user.email = payload['email'].lower()
	if 'age' in payload and payload['age']:
		user.age = int(payload['age'])
	if 'school' in payload and payload['school']:
		user.school = payload['school']
	if 'avatar' in payload:
		user.avatar = payload['avatar']
	if 'address' in payload:
		user.address = payload['address']

	if payload.get('new_password'):
		if not check_password_hash(user.password, payload.get('current_password', '')):
			return jsonify(data={}, message='Current password is incorrect', status=400), 400
		user.password = generate_password_hash(payload['new_password'])

	user.save()
	user_dict = model_to_dict(user)
	user_dict.pop('password')
	return jsonify(data=user_dict, message='Profile updated', status=200), 200


#delete user and all ref route
@users.route('/delete', methods=['DELETE'])
@login_required
def delete_user():

	# user_to_dict = model_to_dict(current_user)
	# print(user_to_dict)
	user_to_delete = models.User.get_by_id(current_user.id)
	user_to_delete.delete_instance()

	return jsonify(
			data={},
			message="Deleted Your account",
			status=200),200






