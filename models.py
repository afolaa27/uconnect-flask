import datetime

from peewee import *


from flask_login import UserMixin




DATABASE = SqliteDatabase('users.sqlite')


class User(UserMixin,Model):
	username = CharField(unique=True)
	latitude = DecimalField()
	longitude = DecimalField()
	age = IntegerField()
	email = CharField(unique=True)
	password = CharField()
	radius = IntegerField()
	school = CharField()

	class meta:
		databse = DATABASE



class Book(Model):
	title = CharField()
	ISBN = CharField()
	description = TextField()
	created_date = DateTimeField(default=datetime.datetime.now)
	Sold = BooleanField()
	favorite = BooleanField()
	owner = ForeignKeyField(User, backref='Books')

	class meta:
		databse = DATABASE


class Favorite(Model):
	
	UserId = ForeignKeyField(User, backref='Favorite')
	Book_Id =ForeignKeyField(Book, backref='Favorite')

	class meta:
		databse = DATABASE

def initialize():
	DATABASE.connect()

	DATABASE.create_tables([User, Book, Favorite], safe=True)
	print('connected and printed tables')


	DATABASE.close()

