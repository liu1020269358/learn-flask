# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, Length, Regexp, Email
from wtforms import ValidationError
from ..models import User, Role

class NameForm(Form):
#定义一个继承自Form类的NameForm类
	name = StringField('What is your name?', validators=[Required()])
	#实例化StringField类为name字段
	#可选参数validators制定一个一个由验证函数构成的列表
	#其中Required()验证确保提交的字段不为空
	submit = SubmitField('Submit')
	#实例化SubmitField类为submit提交按钮

class EditProfileForm(Form):
	name = StringField('Real name', validators = [Length(0, 64)])
	location = StringField('Location', validators = [Length(0, 64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')

class EditProfileAdminForm(Form):
	email = StringField('Email', validators = [Required(), Length(1, 64),
												Email()])
	username = StringField('Username', validators = [
		Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
										'Usernames must have only letters, '
										'numbers, dots or underscores')])
	confirmed = BooleanField('Confirmed')
	role = SelectField('Role', coerce = int)
	name = StringField('Real name', validators = [Length(0, 64)])
	location = StringField('Location', validators = [Length(0, 64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')
	
	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name)
							for role in Role.query.order_by(Role.name).all()]
		self.user = user
	
	def validate_mail(self, field):
		if field.data != self.user.email and \
				User.query.filter_by(email = field.data).first():
			raise ValidationError('Email already registered.')
	
	def validate_username(self, field):
		if field.data != self.user.username and \
				User.query.filter_by(username = field.data).first():
			raise ValidationError('Username already in use')