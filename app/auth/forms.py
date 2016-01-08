# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email

class LoginForm(Form):
#一个表单
	email = StringField('Email', validators = [Required(), Length(1, 64),
												Email()])
	#输入email
	password = PasswordField('Password', validators = [Required()])
	#输入password
	remember_me = BooleanField('Keep me logged in')
	#复选框remember_me
	submit = SubmitField('Log In')
	#提交按钮