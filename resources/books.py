import models

from flask import Blueprint, request, jsonify 

from flask_login import current_user, login_required 

from playhouse.shortcuts import model_to_dict

books = Blueprint('books', 'books')


#create book route
@books.route('/', methods=['POST'])
@login_required
def create_book():
	payload = request.get_json()
	print("post route")


	print(payload)

	
	
	book = models.Book.create(
		title=payload['title'],
		ISBN=payload['ISBN'],
		description=payload['description'],
		price=payload['price'],
		owner=current_user.id,
		image=payload['image'],
		address=payload['value']
	)

	book_dict = model_to_dict(book)
	print("this is book_dict >>> ",book_dict)
	
	book_dict["owner"].pop('password')
	print(book_dict['id'])
	print('the book id ^^^^')

	return jsonify(
		data=book_dict,
		massage='you listed a book',
		status=201),201

#show all logged in user books
@books.route('/', methods=['GET'])
@login_required
def index():
	current_user_books = [model_to_dict(book) for book in current_user.Books]
	
	for i in current_user_books:
		i['owner'].pop('age')
		i['owner'].pop('password')
		i['owner'].pop('email')
		i['owner'].pop('school')
		i['owner'].pop('id')
		
		 
	 
	return jsonify(
		data=current_user_books,
		message= 'Got current user books',
		status=200),200


@books.route('/all', methods=['GET'])
@login_required
def all():

	all_users_books = models.Book.select().where(models.Book.owner != current_user.id)
	
	all_users_books_dict = [model_to_dict(book) for book in all_users_books]

	for i in all_users_books_dict:
		i['owner'].pop('age')
		i['owner'].pop('password')
		i['owner'].pop('email')
		i['owner'].pop('school')
		i['owner'].pop('id')
		
		 
	 
	return jsonify(
		data=all_users_books_dict,
		message= 'Got all books',
		status=200),200



#Gets information about one book 
@books.route('/<id>', methods=['GET'])
@login_required
def show(id):
	book = models.Book.get_by_id(id)
	book_dict = model_to_dict(book)
	book_dict["image"].pop('data')
	book_dict["owner"].pop('password')
	return jsonify(
		data=book_dict,
		message="show page",
		status=200),200


#update one book
@books.route('/<id>', methods=['PUT'])
@login_required
def update_book(id):
	payload = request.get_json()
	book = models.Book.get_by_id(id)
	

	if book.owner.id==current_user.id:
		if 'title' in payload:
			book.title = payload['title']
		if 'ISBN' in payload:
			book.ISBN = payload['ISBN']
		if 'price' in payload:
			book.price = payload['price']
		if 'description' in payload:
			book.description = payload['description']
		if 'image' in payload:
			book.image = payload['image']
		if 'address' in payload:
			book.address = payload['address']
		book.save()
		book_dict = model_to_dict(book)
	
		
		book_dict["owner"].pop('password')

		return jsonify(
			data=book_dict,
			message='You updated your book',
			status=200),200
	else:
		return jsonify(
			data={
				'error': 'Forbidden'
			}, 
			message='cant updated book', 
			status=403),403

#delete one book route
@books.route('/<id>', methods=['Delete'])
def delete_book(id):
	book_to_delete = models.Book.get_by_id(id)
	if current_user.id == book_to_delete.owner.id:
		book_to_delete.delete_instance()

		return jsonify(data={}, 
			message='Deleted book', 
			status=200),200
	else:
		return jsonify(
			data={
				'error': 'Forbidden'
			}, message='cant delete book', status=403),403

#searches based on user choice of search either ISBN, Title, Price, school
@books.route('/search', methods=['GET'])
def search_book():
	query = models.Book.select()
	payload = request.get_json()

	if payload['choice'] == 'ISBN':
		isbn = payload['search']
		for book in query.where(models.Book.ISBN ==isbn):
			print(book.ISBN)
	elif payload['choice'] == 'title':
		title =payload['search']
		for book in query.where(models.Book.title == title):
			print(book.title)
	elif payload['choice'] == 'price':
		price =payload['search']
		for book in query.where(models.Book.price == price):
			print(book.title)
	return jsonify(
		data={})

