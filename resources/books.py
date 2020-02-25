import models

from flask import Blueprint, request, jsonify 

from flask_login import current_user, login_required 

from playhouse.shortcuts import model_to_dict

books = Blueprint('books', 'books')


@books.route('/', methods=['POST'])
@login_required
def create_book():
	payload = request.get_json()
	book = models.Book.create(
		title=payload['title'],
		ISBN=payload['ISBN'],
		description=payload['description'],
		price=payload['price'],
		owner=current_user.id
	)

	book_dict = model_to_dict(book)
	print(book_dict)
	book_dict["owner"].pop('latitude')
	book_dict["owner"].pop('longitude')
	book_dict["owner"].pop('password')
	return jsonify(
		data=book_dict,
		massage='you listed a book',
		status=201),201