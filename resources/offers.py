import datetime
import models
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from playhouse.shortcuts import model_to_dict
from extensions import socketio

offers = Blueprint('offers', 'offers')

def clean_offer(o):
    d = model_to_dict(o, recurse=True)
    for key in ['buyer', 'seller']:
        if d.get(key):
            d[key].pop('password', None)
    if d.get('book') and d['book'].get('owner'):
        d['book']['owner'].pop('password', None)
    return d

def clean_message(m):
    d = model_to_dict(m, recurse=True)
    if d.get('sender'):
        d['sender'].pop('password', None)
    if d.get('offer'):
        d['offer'] = {'id': m.offer.id}
    return d

def _push_notif(recipient_id, notif_type, message, book_title):
    """Emit a live notification to a user's room and save it to the DB."""
    payload = {
        'type': notif_type,
        'message': message,
        'book': book_title,
        'read': False,
        'created_at': datetime.datetime.now().isoformat(),
    }
    socketio.emit('new_notification', payload, room=f'user_{recipient_id}', namespace='/')

# POST /api/v1/offers/ — buyer creates an offer
@offers.route('/', methods=['POST'])
@login_required
def create_offer():
    payload = request.get_json()
    book = models.Book.get_by_id(payload['book_id'])
    offer = models.Offer.create(
        book=book,
        buyer=current_user.id,
        seller=book.owner.id,
        amount=payload['amount']
    )
    if payload.get('message'):
        models.Message.create(offer=offer, sender=current_user.id, body=payload['message'])

    # Notify seller in real time
    _push_notif(
        recipient_id=book.owner.id,
        notif_type='new_offer',
        message=f'{current_user.username} made an offer of ${payload["amount"]} on "{book.title}"',
        book_title=book.title,
    )
    # Persist to DB
    try:
        models.Notification.create(
            Seller_id=book.owner.id,
            Book_id=book.id,
            Buyer_id=current_user.id,
            message=f'{current_user.username} made an offer of ${payload["amount"]} on "{book.title}"',
            read=False,
        )
    except Exception:
        pass

    return jsonify(data=clean_offer(offer), status=201), 201

# GET /api/v1/offers/
@offers.route('/', methods=['GET'])
@login_required
def get_offers():
    as_buyer = models.Offer.select().where(models.Offer.buyer == current_user.id)
    as_seller = models.Offer.select().where(models.Offer.seller == current_user.id)
    all_offers = list(as_buyer) + list(as_seller)
    seen, unique = set(), []
    for o in all_offers:
        if o.id not in seen:
            seen.add(o.id)
            unique.append(o)
    return jsonify(data=[clean_offer(o) for o in unique], status=200), 200

# GET /api/v1/offers/<id>/messages
@offers.route('/<id>/messages', methods=['GET'])
@login_required
def get_messages(id):
    offer = models.Offer.get_by_id(id)
    msgs = models.Message.select().where(models.Message.offer == offer).order_by(models.Message.created_at)
    return jsonify(data=[clean_message(m) for m in msgs], status=200), 200

# POST /api/v1/offers/<id>/messages — send a message
@offers.route('/<id>/messages', methods=['POST'])
@login_required
def send_message(id):
    payload = request.get_json()
    offer = models.Offer.get_by_id(id)
    msg = models.Message.create(offer=offer, sender=current_user.id, body=payload['body'])

    # Emit chat message to the offer room
    socketio.emit('new_message', {
        'id': msg.id,
        'body': msg.body,
        'sender_id': current_user.id,
        'sender_username': current_user.username,
        'created_at': msg.created_at.isoformat(),
    }, room=f'offer_{offer.id}', namespace='/')

    # Notify the other participant
    other_id = offer.seller.id if current_user.id == offer.buyer.id else offer.buyer.id
    preview = payload['body'][:60] + ('…' if len(payload['body']) > 60 else '')
    notif_msg = f'{current_user.username}: "{preview}"'
    _push_notif(
        recipient_id=other_id,
        notif_type='new_message',
        message=notif_msg,
        book_title=offer.book.title,
    )
    # Persist so the panel shows it when opened
    try:
        models.Notification.create(
            Seller_id=other_id,
            Book_id=offer.book.id,
            Buyer_id=current_user.id,
            message=notif_msg,
            read=False,
        )
    except Exception:
        pass

    return jsonify(data=clean_message(msg), status=201), 201

# PATCH /api/v1/offers/<id>/status — seller accepts or declines
@offers.route('/<id>/status', methods=['PATCH'])
@login_required
def update_status(id):
    payload = request.get_json()
    offer = models.Offer.get_by_id(id)
    if offer.seller.id != current_user.id:
        return jsonify(data={}, message='Forbidden', status=403), 403
    status = payload.get('status')
    if status not in ('accepted', 'declined'):
        return jsonify(data={}, message='Invalid status', status=400), 400
    offer.status = status
    offer.save()

    verb = 'accepted' if status == 'accepted' else 'declined'
    status_msg = f'{current_user.username} {verb} your offer on "{offer.book.title}"'
    _push_notif(
        recipient_id=offer.buyer.id,
        notif_type='offer_update',
        message=status_msg,
        book_title=offer.book.title,
    )
    try:
        models.Notification.create(
            Seller_id=offer.buyer.id,
            Book_id=offer.book.id,
            Buyer_id=offer.seller.id,
            message=status_msg,
            read=False,
        )
    except Exception:
        pass

    # If accepted → notify other users who favorited this book that it may sell
    if status == 'accepted':
        try:
            favorites = models.Favorite.select().where(models.Favorite.Book_Id == offer.book.id)
            for fav in favorites:
                if fav.User_id.id != offer.buyer.id:
                    _push_notif(
                        recipient_id=fav.User_id.id,
                        notif_type='book_sold',
                        message=f'"{offer.book.title}" you saved has received an accepted offer — it may sell soon!',
                        book_title=offer.book.title,
                    )
        except Exception:
            pass

    return jsonify(data=clean_offer(offer), status=200), 200
