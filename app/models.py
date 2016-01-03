# -*- coding: utf-8 -*-

from . import db



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
		
class User(db.Model):
#定义User模型
	__tablename__ = 'users'
	#表单名字为users
	id = db.Column(db.Integer, primary_key=True)
	#设定id列，这是表的主键
	username = db.Column(db.String(64), unique=True, index=True)
	#设定username列，不允许出现重复的值，创建索引
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	#定义role_id列为外键，roles.id表明此列的值
	def __repr__(self):
		return '<User %r>' % self.username
		#返回一个字符串，以供调试和测试