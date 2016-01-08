# -*- coding: utf-8 -*-

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))
	#接收user_id，如果用户存在，则返回用户对象，否则返回None
	
class Role(db.Model):
#定义Roel模型
	__tablename__ = 'roles'
	#表单名字为roles
	id = db.Column(db.Integer, primary_key=True)
	#设定id列，这是表的主键
	name = db.Column(db.String(64), unique=True)
	#设定name列，不允许出现重复的值
	users = db.relationship('User', backref='role', lazy='dynamic')
	#定义users属性为与Role关联的模型的列表
	#若将uselist设为False，则不返回列表，而使用标量值
	def __repr__(self):
		return '<Role %r>' % self.name
		#返回一个字符串，以供调试和测试
		
class User(UserMixin, db.Model):
#定义User模型
	__tablename__ = 'users'
	#表单名字为users
	id = db.Column(db.Integer, primary_key=True)
	#设定id列，这是表的主键
	username = db.Column(db.String(64), unique=True, index=True)
	#设定username列，不允许出现重复的值，创建索引
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	#定义role_id列为外键，roles.id表明此列的值
	password_hash = db.Column(db.String(128))
	#设定password_hash列
	email = db.Column(db.String(64), unique = True, index = True)
	#设定mail列
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')
	#如果试图读取password属性则抛出AttributeError
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)
	#将password哈希后传给self.password_hash,可通过User.password = ''调用
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	#验证password是否输入正确
	def __repr__(self):
		return '<User %r>' % self.username
		#返回一个字符串，以供调试和测试