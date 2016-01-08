# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class RegistrationForm(Form):
#注册表单
	email = StringField('Email', validators = [Required(), Length(1, 64), Email()])
	#输入邮箱
	username = StringField('Username', validators = [
		Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
											'Usernames must have only letters, '
											'numbers, dots or underscores')])
	#输入用户名，Regexp为正则表达式函数，再次用于匹配username只能包含字母，数字，下划线和'.'后面的参数为验证失败的信息
	password = PasswordField('Password', validators = [
		Required(), EqualTo('password2', message = 'Passwords must match.')])
	#password必须与password2相等，由EqualTo实现
	password2 = PasswordField('Confirm password', validators = [Required()])
	#输入password2
	submit = SubmitField('Register')
	#提交按钮
	
	def validate_email(self, field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError('Email already registered.')
	#validate_开头且后面更正字段名，这个方法就会和该字段的验证函数一起调用
	#这个方法是验证email是否已经在数据库中存在
		
	def validate_username(self, field):
		if User.query.filter_by(username = field.data).first():
			raise ValidationError('Username already in use.')
	#这个方法是验证username是否已经在数据库中存在
class LoginForm(Form):
#登录表单
	email = StringField('Email', validators = [Required(), Length(1, 64), Email()])
	#输入email
	password = PasswordField('Password', validators = [Required()])
	#输入password
	remember_me = BooleanField('Keep me logged in')
	#复选框remember_me
	submit = SubmitField('Log In')
	#提交按钮
	
class ChangePasswordForm(Form):
	old_password = PasswordField('Old Password', validators = [Required()])
	password = PasswordField('After Password', validators = [
		Required(), EqualTo('password2', message = 'Passwords must match')])
	password2 = PasswordField('Confirm password', validators = [Required()])
	submit = SubmitField('Update Password')
	
class PasswordResetRequestForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64),
											Email()])
	submit = SubmitField('Reset Password')

class PasswordResetForm(Form):
	email = StringField('Email', validators=[Required(), Length(1, 64),
											Email()])
	password = PasswordField('New Password', validators=[
		Required(), EqualTo('password2', message='Passwords must match')])
	password2 = PasswordField('Confirm password', validators=[Required()])
	submit = SubmitField('Reset Password')
	
	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first() is None:
			raise ValidationError('Unknown email address.')

class ChangeEmailForm(Form):
	email = StringField('New Email', validators=[Required(), Length(1, 64),
												Email()])
	password = PasswordField('Password', validators=[Required()])
	submit = SubmitField('Update Email Address')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')
