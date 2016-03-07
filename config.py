# -*- coding: utf-8 -*-

import os #引入os模块
basedir = os.path.abspath(os.path.dirname(__file__)) 
# 将本文件的目录名规范化为绝对路径

class Config:
#通用配置
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
	#如果os.environ.get(''SECRET_KEY)为None，则将'hard to guess string'赋值给SECRET_KEY
	#这是密匙，以防CSRF攻击
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	#将其设为True时，每次请求结束后都会自动提交数据库的变动
	MAIL_SERVER = 'smtp.qq.com'
	#电子邮件服务器的主机名
	MAIL_PORT = 465
	#电子邮件服务器的端口
	MAIL_USE_SSL = True
	#启用TLS协议
	MAIL_USERNAME = 'example@qq.com'
	#邮件账户的用户名
	MAIL_PASSWORD = 'pass_word'
	#邮件账户的密码
	FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
	#邮件主题的前缀
	FLASKY_MAIL_SENDER = 'example@qq.com'
	#邮件的发送者
	FLASKY_ADMIN = 'example@qq.com'
	#管理员邮箱
	FLASKY_POSTS_PER_PAGE = 20
	#博客每页显示的数目为20
	FLASKY_FOLLOWERS_PER_PAGE = 50
	FLASKY_COMMENTS_PER_PAGE = 30
	@staticmethod
	def init_app(app):
		pass
	#对当前环境配置的初始化
		
class DevelopmentConfig(Config):
#开发配置
	DEBUG = True
	#开启调试模式
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
	#数据库URL从环境变量中导入或为默认URL
		
class TestiongConfig(Config):
#调试配置
	TESTING = True
	#启动测试模式
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
	#数据库URL从环境变量中导入或为默认URL
		
class ProductionConfig(Config):
#生产配置
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')
	#数据库URL从环境变量中导入或为默认URL

config = {
		'development': DevelopmentConfig,
		'testing': TestiongConfig,
		'production': ProductionConfig,
		
		'default': DevelopmentConfig
		#默认配置
	}
#在config中注册开发，测试，生产和默认时所需的配置环境
