import models
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from playhouse.shortcuts import model_to_dict

notifications = Blueprint('notifications', 'notifications')

def clean_notif(n):
    d = model_to_dict(n)
    d['Seller_id'].pop('password', None)
    d['Buyer_id'].pop('password', None)
    d['Book_id']['owner'].pop('password', None)
    return d

@notifications.route('/<id>', methods=['POST'])
@login_required
def create_notification(id):
    payload = request.get_json()
    notification = models.Notification.create(
        Seller_id=payload['Seller_id'],
        Book_id=id,
        Buyer_id=current_user.id,
        message=payload['message']
    )
    return jsonify(data=clean_notif(notification), message='Notification created', status=201), 201

@notifications.route('/', methods=['GET'])
@login_required
def get_notifications():
    notifs = (models.Notification
        .select()
        .where(models.Notification.Seller_id == current_user.id)
        .order_by(models.Notification.created_at.desc()))
    return jsonify(data=[clean_notif(n) for n in notifs], status=200), 200

@notifications.route('/unread_count', methods=['GET'])
@login_required
def unread_count():
    count = (models.Notification
        .select()
        .where(
            models.Notification.Seller_id == current_user.id,
            models.Notification.read == False
        ).count())
    return jsonify(data={'count': count}, status=200), 200

@notifications.route('/<id>/read', methods=['PATCH'])
@login_required
def mark_read(id):
    notif = models.Notification.get_by_id(id)
    if notif.Seller_id.id == current_user.id:
        notif.read = True
        notif.save()
    return jsonify(data={}, status=200), 200
