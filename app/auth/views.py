# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash
from . import auth
from .. import db
from flask.ext.login import login_user, login_required, logout_user, current_user
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
	PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm

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
			#重定向到之前的页面或主页面
		flash('Invalid username or password.')
		#如果用户名或密码错误，则会有一个flash消息
	return render_template('auth/login.html', form = form)
	#渲染模板'auth/login.html'
	#将login.html保存在templates/auth文件夹中，防止与其他蓝本冲突
	
@auth.route('/logout')
@login_required
#这个页面需要登录才能访问
def logout():
	logout_user()
	#登出用户
	flash('You have been logged out.')
	return redirect(url_for('main.index'))
	#登出到主页面

@auth.route('/register', methods = ['GET', 'POST'])
def register():
	form = RegistrationForm()
	#创建注册页面实例
	if form.validate_on_submit():
	#如果POST请求有效
		user = User(email = form.email.data,
					username = form.username.data,
					password = form.password.data)
		#创建User实例
		db.session.add(user)
		#将这个新注册用户添加到数据库
		db.session.commit()
		#提交数据
		token = user.generate_confirmation_token()
		#将用户的SECRET_KEY生成加密令牌
		send_email(user.email, 'Confirm Your Account',
					'auth/email/confirm', user = user, token = token)
		#发送邮件
		flash('A confirmation email has been sent to you by email.')
		#发出消息，告诉用户验证邮件已发出
		return redirect(url_for('main.index'))
		#重定向到主页面
	return render_template('auth/register.html', form = form)
	#把注册页面实例传入，渲染表单

@auth.route('/confirm/<token>')
@login_required
#这个页面需要登录才能访问
def confirm(token):
#创建一个验证加密令牌的类confirm
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	#如果当前的令牌已被验证过，则重定向到主页面
	if current_user.confirm(token):
		flash('You have confirmed your account. Thanks!')
	#如果验证成功，弹出消息
	else:
		flash('The confirmation link is invalid or has expired.')
	#如果验证失败，弹出消息
	return redirect(url_for('main.index'))
	#重定向到主页面

@auth.before_app_request
#在全局条件下在每个请求之前
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		#如果用户验证成功，则调用ping方法，last_seen会被加入到session中
		if not current_user.confirmed\
				and request.endpoint[:5] != 'auth.'\
				and request.endpoint != 'static':
		#当前用户已登录
		#当前用户还未验证
		#请求的路径不在认证蓝本中
		#请求的路径不是'static'
			return redirect(url_for('auth.unconfirmed'))
			#重定向到'未认证页面'

@auth.route('/unconfirmed')
#未认证页面
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
	#如果当前用户是匿名的或当前用户已认证成功
		return redirect(url_for('main.index'))
		#重定向到主页面
	return render_template('auth/unconfirmed.html')
	#渲染未认证页面

@auth.route('/confirm')
#认证页面
@login_required
def resend_confirmation():
#这是由未认证页面连接的页面，以防之前的邮件丢失，请求再次发送邮件
	token = current_user.generate_confirmation_token()
	#将当前用户的SECRET_KEY生成加密令牌
	send_email(current_user.email, 'Confirm Your Account',
				'auth/email/confirm', user = current_user, token = token)
	#发送邮件给当前用户的邮箱
	flash('A confirmation email has been sent to you by email.')
	#弹出消息
	return redirect(url_for('main.index'))
	#重定向到主页面
	
@auth.route('change-password', methods = ['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			flash('Your password has been updated')
			return redirect(url_for('main.index'))
		else:
			flash('Invalid Password')
	return render_template('auth/change_password.html', form = form)
	
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_token()
			send_email(user.email, 'Reset Your Password',
					'auth/email/reset_password',
					user=user, token=token,
					next=request.args.get('next'))
					#next参数的作用为？
			flash('An email with instructions to reset your password has been '
				'sent to you.')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token, form.password.data):
			flash('Your password has been updated.')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form=form)
	
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_email = form.email.data
			token = current_user.generate_email_change_token(new_email)
			send_email(new_email, 'Confirm your email address',
					'auth/email/change_email',
					user=current_user, token=token)
			flash('An email with instructions to confirm your new email '
					'address has been sent to you.')
			return redirect(url_for('main.index'))
		else:
			flash('Invalid email or password.')
	return render_template("auth/change_email.html", form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
	if current_user.change_email(token):
		flash('Your email address has been updated.')
	else:
		flash('Invalid request.')
	return redirect(url_for('main.index'))
