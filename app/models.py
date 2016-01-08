# -*- coding: utf-8 -*-

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

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
	confirmed = db.Column(db.Boolean, default = False)
	#设定confirmed列，为布尔属性，默认为False，为True说明已被验证过
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
	
	def generate_confirmation_token(self, expiration = 3600):
	#生成加密令牌
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		#接收SECRET_KEY为参数生成一个JSON Web签名，expiration为有效时间
		return s.dumps({'confirm': self.id})
		#将self.id生成一个加密签名，再生成一个令牌字符串
		
	def confirm(self, token):
	#验证令牌
		s = Serializer(current_app.config['SECRET_KEY'])
		#接收SECRET_KEY为参数生成一个JSON Web签名
		try:
			data = s.loads(token)
			#解码令牌
		except:
			return False
			#如果令牌过期或令牌错误，则返回False
		#以上是为了验证接收的token是否为SECRET_KEY的加密令牌
		if data.get('confirm') != self.id:
			return False
			#如果令牌中的id和存储在current_user中已登录的用户id不同，则返回False
		self.confirmed = True
		#以上验证都通过的话，将confirmed列（属性）设为True
		db.session.add(self)
		#将表单数据提交到数据库
		return True
		#返回True
		
	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id})
		
	def reset_password(self, token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.id:
			return False
		self.password = new_password
		db.session.add(self)
		return True
		
	def generate_email_change_token(self, new_email, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'change_email': self.id, 'new_email': new_email})
		
	def change_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('change_email') != self.id:
			return False
		new_email = data.get('new_email')
		if new_email is None:
			return False
		if self.query.filter_by(email=new_email).first() is not None:
			return False
		self.email = new_email
		db.session.add(self)
		return True
		
	def __repr__(self):
		return '<User %r>' % self.username
		#返回一个字符串，以供调试和测试