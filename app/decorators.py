#-*- coding: utf-8 -*-

from functools import wraps
from flask import abort
from flask.ext.login import current_user
from .models import Permission

#这个类为自定义修饰器的类

def permission_required(permission):
#接收一个权限参数
	def decorator(f):
	#接收一个函数
		@wraps(f)
		#decorated_function = wraps(decorated_function)
		def decorated_function(*args, **kwargs):
			if not current_user.can(permission):
			#如果当前用户请求的权限不存在
				abort(403)
				#弹出403错误页面
			return f(*args, **kwargs)
			#返回f(*args, **kwargs)也就是拥有该权限后调用的函数结果
			#在书中的例子为一个字符串，实际中可能是一个render_template()
		return decorated_function
		#返回decorated_function这个函数
	return decorator
	#返回decorator这个函数
#permission_required这个函数接收一个权限参数，返回一个其中定义的函数decorator
#decorator这个函数接收一个函数，返回一个其中定义的函数decorated_function
#decorated_function这个函数被wraps装饰器修饰
#其返回值要么是403错误，要么是decorator函数接收到的函数参数
#这个装饰器用于只对特殊用户开放的视图函数views.py

def admin_required(f):
	return permission_required(Permission.ADMINISTER)(f)
#调用admin_required(f), f为验证成功后调用的函数
#permission_required(Permission.ADMINISTER)等于decorator，以及一个Permission.ADMINISTER参数
#permission_required(Permission.ADMINISTER)(f)等于decorator(f)
#decorator(f)等于decorated_function以及两个参数Permission.ADMINISTER和f
#decorated_function等于验证请求的权限，要么403，要么f的调用
#这个装饰器用于只对管理员开放的视图函数views.py