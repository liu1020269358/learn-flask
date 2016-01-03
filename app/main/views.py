# -*- coding: utf-8 -*-

from flask import render_template, session, redirect, url_for, current_app

from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..email import send_email

@main.route('/', methods=['GET', 'POST'])
#将index函数作为'/'即根地址的处理程序，把POST加入请求方法列表
def index():
	form = NameForm()
	#实例化NameForm
	if form.validate_on_submit():
	#form.validate_on_submit()这个函数的作用为验证提交是否成功
	#若成功被验证函数通过，则返回True,反之为False
	#第一次访问时，没有提交表单数据，所以为False
		user = User.query.filter_by(username=form.name.data).first()
		#将User这个模型通过过滤器username=form.name.data查询后的第一个值赋值给user
		if user is None:
		#如果没有这个user
			user = User(username=form.name.data)
			#实例化User模型，将form.name.date（提交的name的数据）导入在其中的username列中
			db.session.add(user)
			#将user提交到会话当中
			session['known'] = False
			#将konwn变量写入会话中,设为False
			if current_app.config['FLASKY_ADMIN']:
			#如果在环境变量中设置了FLASKY_ADMIN
				send_email(current_app.config['FLASKY_ADMIN'], 'New User',
							'mail/new_user', user = user)
				#调用send_email()函数
		else:
			session['known'] = True
			#将会话中的known变量设为True
		session['name'] = form.name.data
		#将会话中的name变量设为form.name.data
		#将提交的name保存在会话name变量中
		return redirect(url_for('.index'))
		#重定向到.index的URL，重新发起GET请求
	return render_template('index.html',
	#渲染index.html模板
							form = form, name = session.get('name'),
							known = session.get('known', False))
							#模板中变量的真实值:from, name, known, current_time