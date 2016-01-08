# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash
from . import auth
from flask.ext.login import login_user, login_required, logout_user
from ..models import User
from .forms import LoginForm

@auth.route('/login', methods = ['GET', 'POST'])
#路由路由为/login
#由于在create_app中加入了参数url_prefix = '/auth'，所以实际路由为'auth/login'
def login():
	form = LoginForm()
	#创建一个表单实例
	if form.validate_on_submit():
	#验证表单数据，验证POST请求是否有效
		user = User.query.filter_by(email = form.email.data).first()
		#user为User表中email列的数据，即用户名为电子邮件地址
		if user is not None and user.verify_password(form.password.data):
		#如果用户存在且密码正确
			login_user(user, form.remember_me.data)
			#登录用户，是否记住cookies看remember_me是否勾选
			return redirect(request.args.get('next') or url_for('main.index'))
			#如果用户没有被授权
		flash('Invalid username or password.')
		#如果用户名或密码错误，则会有一个flash消息
	return render_template('auth/login.html', form = form)
	#渲染模板'auth/login.html'
	#将login.html保存在templates/auth文件夹中，防止与其他蓝本冲突
	
@auth.route('/logout')
@login_required
def logout():
	logout_user()
	#登出用户
	flash('You have been logged out.')
	return redirect(url_for('main.index'))
	#登出到主页面