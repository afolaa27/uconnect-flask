import datetime

from peewee import *


from flask_login import UserMixin

DATABASE = SqliteDatabase('uconnect.sqlite')


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



class Book(Model):
	title = CharField()
	ISBN = CharField()
	description = TextField()
	created_date = DateTimeField(default=datetime.datetime.now)
	Sold = BooleanField()
	favorite = BooleanField()
	owner = ForeignKeyField(User, backref='Books')

	class Meta:
		database = DATABASE


class Favorite(Model):
	UserId = ForeignKeyField(User, backref='Favorite')
	Book_Id =ForeignKeyField(Book, backref='Favorite')

	class Meta:
		database = DATABASE

def initialize():
	DATABASE.connect()

	DATABASE.create_tables([User, Book, Favorite], safe=True)
	print('connected and printed tables')


	DATABASE.close()

