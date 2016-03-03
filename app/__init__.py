# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
#login_manager对象的session_protection属性可设为None, 'basic'或'strong'提供不同的安全等级
login_manager.login_view = 'auth.login'
#login_view属性设置登录页面的端点
 

def create_app(config_name):
#定义 creat_app()函数
	app = Flask(__name__)
	#创建Flask类的实例app
	app.config.from_object(config[config_name])
	#导入config[config_name]这个配置,
	#config_name可为config.py文件中中四个配置中的一种
	config[config_name].init_app(app)
	#将app这个程序实例环境配置初始化
	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)
	#将bootstrap、mail、moment、db、实例初始化
	from .main import main as main_blueprint
	#从app\main模块中导入main实例，并叫做main_blueprint
	app.register_blueprint(main_blueprint)
	#在app中注册主页面蓝图
	from .auth import auth as auth_blueprint
	#从app\auth模块中导入auth实例，并叫做auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix = '/auth')
	#在app中注册登录页面的蓝图，并在路由前面加上auth前缀
	return app
	#返回app实例
#这个函数称为工厂函数，接收一个参数(程序的配置名)，创建多个程序实例，
#程序创建好后，再进行初始化，这样可以动态修改配置
#也就是说，config_name更换后，程序实例再次初始化，配置也就改变了