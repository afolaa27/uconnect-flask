import os
import datetime

from peewee import *


from flask_login import UserMixin

from playhouse.db_url import connect
DATABASE = SqliteDatabase('uconnect.sqlite', pragmas={'foreign_keys': 1})

if 'ON_HEROKU' in os.environ: # later we will manually add this env var 
                              # in heroku so we can write this code
  DATABASE = connect(os.environ.get('DATABASE_URL')) # heroku will add this 
                                                     # env var for you 
                                                     # when you provision the
                                                     # Heroku Postgres Add-on
else:
  DATABASE = SqliteDatabase('uconnect.sqlite')


class User(UserMixin, Model):
	username = CharField(unique=True)
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
	Sold = BooleanField(default=False)
	price = IntegerField()
	owner = ForeignKeyField(User, backref='Books', on_delete='CASCADE')
	image = CharField()
	address= CharField()

	class Meta:
		database = DATABASE


class Favorite(Model):
	User_id = ForeignKeyField(User, backref='Favorite',on_delete='CASCADE')
	Book_Id =ForeignKeyField(Book, backref='Favorite', on_delete='CASCADE')

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

	DATABASE.create_tables([User, Book, Favorite, Notification], safe=True)
	print('connected and printed tables')


	DATABASE.close()

