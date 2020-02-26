import models

from flask import Blueprint, request, jsonify 

from flask_login import current_user, login_required 

from playhouse.shortcuts import model_to_dict

notifications = Blueprint('notifications', 'notifications')

#creates a notification
@notifications.route('/', methods=['POST'])
@login_required
def create_notification():
	payload = request.get_json()

	notification = models.Notification.create(
		Seller_id=payload['Seller_id'],
		Book_id=payload['Book_id'],
		Buyer_id= current_user.id,
		message=payload['message'])

	notification_to_dict = model_to_dict(notification)
	print(notification_to_dict)
	notification_to_dict['Seller_id'].pop('password')
	notification_to_dict['Buyer_id'].pop('password')
	notification_to_dict['Book_id']['owner'].pop('password')
	notification_to_dict['Book_id']['image'].pop('data')
	
	return jsonify(
		data=notification_to_dict,
		message="Notification created",
		status=200),200

#gets all notification for logged in user
@notifications.route('/', methods=['GET'])
@login_required
def get_notifications():
	current_user_notifications= [model_to_dict(nots) for nots in current_user.Favorite]
	for i in current_user_notifications:
		i['User_id'].pop('password')
		i['Book_Id']['owner'].pop('password')
		i['Book_Id']['image'].pop('data')

	return jsonify(data=current_user_notifications,
		message="got all notifications",
		status=200),200