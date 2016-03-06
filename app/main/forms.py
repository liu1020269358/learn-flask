# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, Length, Regexp, Email
from wtforms import ValidationError
from ..models import User, Role
from flask.ext.pagedown.fields import PageDownField

class NameForm(Form):
#定义一个继承自Form类的NameForm类
	name = StringField('What is your name?', validators=[Required()])
	#实例化StringField类为name字段
	#可选参数validators制定一个一个由验证函数构成的列表
	#其中Required()验证确保提交的字段不为空
	submit = SubmitField('Submit')
	#实例化SubmitField类为submit提交按钮

class EditProfileForm(Form):
#编辑资料表单
	name = StringField('Real name', validators = [Length(0, 64)])
	location = StringField('Location', validators = [Length(0, 64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')
	#可以编辑name, location, about_me
	
class EditProfileAdminForm(Form):
#编辑管理员资料表单
	email = StringField('Email', validators = [Required(), Length(1, 64),
												Email()])
	username = StringField('Username', validators = [
		Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
											#正则表达式
										'Usernames must have only letters, '
										'numbers, dots or underscores')])
	confirmed = BooleanField('Confirmed')
	role = SelectField('Role', coerce = int)
	#SelectField为下拉控件coerce参数表示把字段的值转化为整数，而不是默认的字符串
	#本应由一个choice参数，在__init__方法中设置了
	name = StringField('Real name', validators = [Length(0, 64)])
	location = StringField('Location', validators = [Length(0, 64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')
	
	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name)
							for role in Role.query.order_by(Role.name).all()]
		#choice接收的参数为一个由元组构成的列表，元组的第一个值为标识符，第二个值为显示在控件中的文本字符串
		#由Role.name排序显示
		self.user = user
		#接收user对象是为了后面的mail验证和username验证
	
	def validate_mail(self, field):
		if field.data != self.user.email and \
				User.query.filter_by(email = field.data).first():
			raise ValidationError('Email already registered.')
		#验证邮箱是否发生变化，若发生变化且更改后与数据库中已有的email重合，则报错
	
	def validate_username(self, field):
		if field.data != self.user.username and \
				User.query.filter_by(username = field.data).first():
			raise ValidationError('Username already in use')
		#验证用户名是否发生变化，若发生变化且更改后与数据库中已有的username重合，则报错

class PostForm(Form):
	body = PageDownField("What's on your mind?", validators = [Required()])
	submit = SubmitField('Submit')
#提交博客的表单

class CommentForm(Form):
	body = StringField('', validators = [Required()])
	submit = SubmitField('Submit')
#提交评论的表单