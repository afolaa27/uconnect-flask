import os
import datetime

from peewee import *


from flask_login import UserMixin

from playhouse.db_url import connect
if os.environ.get('DATABASE_URL'):
    DATABASE = connect(os.environ.get('DATABASE_URL'))
else:
    DATABASE = SqliteDatabase('uconnect.sqlite')


class User(UserMixin, Model):
	username = CharField(unique=True)
	age = IntegerField()
	email = CharField(unique=True)
	password = CharField()
	school = CharField()
	avatar = CharField(default='')
	address = CharField(default='')
	
	

	class Meta:
		database = DATABASE

class Book(Model):
	title = CharField()
	ISBN = CharField()
	description = TextField()
	created_date = DateTimeField(default=datetime.datetime.now)
	Sold = BooleanField(default=False)
	price = IntegerField()
	owner = ForeignKeyField(User, backref='Books', on_delete='CASCADE')
	image = CharField()
	address= CharField()
	subject = CharField(default='')
	condition = CharField(default='')

	class Meta:
		database = DATABASE


class Favorite(Model):
	User_id = ForeignKeyField(User, backref='Favorite',on_delete='CASCADE')
	Book_Id =ForeignKeyField(Book, backref='Favorite', on_delete='CASCADE')

	class Meta:
		database = DATABASE

class Notification(Model):
	Seller_id = ForeignKeyField(User, backref='received_notifications', on_delete='CASCADE')
	Book_id = ForeignKeyField(Book, backref='Notification', on_delete='CASCADE')
	Buyer_id = ForeignKeyField(User, backref='sent_notifications', on_delete='CASCADE')
	status = BooleanField(null=True)
	message = CharField(null=False)
	read = BooleanField(default=False)
	created_at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = DATABASE

class Offer(Model):
	book = ForeignKeyField(Book, backref='offers', on_delete='CASCADE')
	buyer = ForeignKeyField(User, backref='sent_offers', on_delete='CASCADE')
	seller = ForeignKeyField(User, backref='received_offers', on_delete='CASCADE')
	amount = IntegerField()
	status = CharField(default='pending')  # 'pending', 'accepted', 'declined'
	created_at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = DATABASE

class Message(Model):
	offer = ForeignKeyField(Offer, backref='messages', on_delete='CASCADE')
	sender = ForeignKeyField(User, backref='sent_messages', on_delete='CASCADE')
	body = TextField()
	created_at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = DATABASE

def initialize():
	DATABASE.connect()

	DATABASE.create_tables([User, Book, Favorite, Notification, Offer, Message], safe=True)
	print('connected and printed tables')

	try:
		DATABASE.execute_sql('ALTER TABLE notification ADD COLUMN read INTEGER DEFAULT 0')
	except:
		pass
	try:
		DATABASE.execute_sql('ALTER TABLE notification ADD COLUMN created_at TEXT')
		DATABASE.execute_sql("UPDATE notification SET created_at = datetime('now') WHERE created_at IS NULL")
	except:
		pass
	try:
		DATABASE.execute_sql("ALTER TABLE book ADD COLUMN subject TEXT DEFAULT ''")
	except:
		pass
	try:
		DATABASE.execute_sql("ALTER TABLE book ADD COLUMN condition TEXT DEFAULT ''")
	except:
		pass
	try:
		DATABASE.execute_sql("ALTER TABLE user ADD COLUMN avatar TEXT DEFAULT ''")
	except:
		pass
	try:
		DATABASE.execute_sql("ALTER TABLE user ADD COLUMN address TEXT DEFAULT ''")
	except:
		pass

	DATABASE.close()

