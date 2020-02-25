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
	

	image = models.Image.create(
		filename=payload['filename'],
		data=payload['data']
		)

	image_dict = model_to_dict(image)
	

	book = models.Book.create(
		title=payload['title'],
		ISBN=payload['ISBN'],
		description=payload['description'],
		price=payload['price'],
		owner=current_user.id,
		image=image_dict['id']
	)

	book_dict = model_to_dict(book)
	print("this is book_dict >>> ",book_dict)
	book_dict["image"].pop('data')
	book_dict["owner"].pop('latitude')
	book_dict["owner"].pop('longitude')
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
	current_user_books= [model_to_dict(book) for book in current_user.Books]
	
	for i in current_user_books:
		i['owner'].pop('age')
		i['owner'].pop('longitude')
		i['owner'].pop('latitude')
		i['owner'].pop('password')
		i['owner'].pop('email')
		i['owner'].pop('school')
		i['owner'].pop('id')
		i['image']['data']=str(i['image']['data'])
		 
	 
	return jsonify(
		data=current_user_books,
		message= 'Got current user books',
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
		book.save()
		book_dict = model_to_dict(book)
		print(book_dict)
		book_dict["image"].pop('data')
		book_dict["owner"].pop('latitude')
		book_dict["owner"].pop('longitude')
		book_dict["owner"].pop('password')
		
		return jsonify(
			data=book_dict,
			message='You updated your book',
			status=200),200
	else:
		return jsonify(
			data={
				'error': 'Forbidden'
			}, message='cant updated book', status=403),403
