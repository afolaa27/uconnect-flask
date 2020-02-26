import models

from flask import Blueprint, request, jsonify 

from flask_login import current_user, login_required 

from playhouse.shortcuts import model_to_dict

favorites = Blueprint('favorites', 'favorites')

#get all user favorite books
@favorites.route('/', methods=['GET'])
@login_required
def favorite_books():
	current_user_favorites= [model_to_dict(book) for book in current_user.Favorite]
	print(current_user_favorites[1])
	for i in current_user_favorites:
		i['User_id'].pop('latitude')
		i['User_id'].pop('longitude')
		i['User_id'].pop('password')
		i['Book_Id']['owner'].pop('latitude')
		i['Book_Id']['owner'].pop('longitude')
		i['Book_Id']['owner'].pop('password')
		i['Book_Id']['image'].pop('data')
	return jsonify(
		data=current_user_favorites,
		message='Got favorite books',
		status=200),200

#create favorite for a book
@favorites.route('/<id>', methods=['POST'])
@login_required
def create_favorite_book(id):
	
	favorite = models.Favorite.create(
		User_id=current_user.id,
		Book_Id=id)

	favorite_dict = model_to_dict(favorite)
	print(">>>>",favorite_dict)

	#favorite_dict['User_id'].pop('')
	favorite_dict['User_id'].pop('latitude')
	favorite_dict['User_id'].pop('longitude')
	favorite_dict['User_id'].pop('password')
	favorite_dict['Book_Id']['owner'].pop('latitude')
	favorite_dict['Book_Id']['owner'].pop('longitude')
	favorite_dict['Book_Id']['owner'].pop('password')
	favorite_dict['Book_Id']['image'].pop('data')
	return jsonify(
		data=favorite_dict,
		message= 'created a favorite for a book',
		status=200),200

#removes a book as a favorite
@favorites.route('/<id>', methods=['Delete'])
@login_required
def delete_Book_favorite(id):
	fav_to_remove = models.Favorite.get_by_id(id)
	print("My current User id >>>>",current_user.id)
	print("My fav to remove >>>>",fav_to_remove.User_id)
	print("Type current User id >>>>",type(current_user.id))
	print("Type fav to remove >>>>",type(fav_to_remove.User_id.id))
	if fav_to_remove.User_id.id == current_user.id:
		fav_to_remove.delete_instance()
		return jsonify(data={}, 
			message='Deleted Favorite', 
			status=200),200
	else:
		return jsonify(
			data={
				'error': 'Forbidden'
			}, message='cant delete favorite', status=403),403

 

