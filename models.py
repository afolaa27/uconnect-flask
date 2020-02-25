import datetime

from peewee import *


from flask_login import UserMixin

DATABASE = SqliteDatabase('uconnect.sqlite', pragmas={'foreign_keys': 1})


class User(UserMixin, Model):
	username = CharField(unique=True)
	latitude = DecimalField()
	longitude = DecimalField()
	age = IntegerField()
	email = CharField(unique=True)
	password = CharField()
	school = CharField()
	

	class Meta:
		database = DATABASE

class Image(Model):
	filename = TextField()
	data=BlobField()
	owner = ForeignKeyField(User, backref='Books', on_delete='CASCADE')
	
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
	image=ForeignKeyField(Image, backref='Books',on_delete='CASCADE')
	

	class Meta:
		database = DATABASE

class Favorite(Model):
	User_id = ForeignKeyField(User, backref='Favorite',on_delete='CASCADE')
	Book_Id =ForeignKeyField(Book, backref='Favorite')

	class Meta:
		database = DATABASE

class Notification(Model):
	Seller_id = ForeignKeyField(User, backref='Notification',on_delete='CASCADE')
	Book_id = ForeignKeyField(Book, backref='Notification',on_delete='CASCADE')
	Buyer_id = ForeignKeyField(User, backref='Notification',on_delete='CASCADE')
	status = BooleanField(null=True)
	message = CharField(null=False)

	class Meta:
		database = DATABASE

def initialize():
	DATABASE.connect()

	DATABASE.create_tables([User, Book, Favorite, Notification, Image], safe=True)
	print('connected and printed tables')


	DATABASE.close()

