#-*- coding: utf-8 -*-

from threading import Thread
from flask import current_app, render_template
from flask.ext.mail import Message
from . import mail

def send_async_email(app, msg):
#定义一步发送电子邮件的函数
	with app.app_context():
	#使用with语句，调用上下文管理器
	#创建应用上下文，在执行app.app_context():之前，会调用__enter__()进入上下文
		mail.send(msg)
		#调用mail实例的send方法,将msg实例作为参数传入
		#发送电子邮件
		
def send_email(to, subject, template, **kwargs):
#定义send_email函数，参数为：接收者的邮箱，主题，模板，关键字参数
	app = current_app._get_current_object()
	#得到当前应用对象
	msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
					sender = app.config['FLASKY_MAIL_SENDER'], recipients = [to])
	#从配置文件中获取主题前缀后加上标题形成完整的主题
	#从配置文件中获取发送者，从参数中获取接收者
	#以上三个变量作为Message()类的属性，实例化了一个Message类为msg实例
	#Message封装了一个message消息
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	#分别渲染.txt和.html模板，将关键字参数传入render_template函数中以便渲染模板
	thr = Thread(target = send_async_email, args = [app, msg])
	#实例化Thread类，将函数和参数传入，得到一个Thread实例对象赋给thr
	thr.start()
	#调用Thread中的start方法，启动新线程，也就是子线程
	return thr
	#返回thr