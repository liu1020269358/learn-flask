# -*- coding: utf-8 -*-

import os
from app import create_app, db
from app.models import User, Role, Permission, Post, Follow, Comment
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
#调用create_app函数，参数为
manager = Manager(app)
#实例化Manager类
migrate = Migrate(app, db)
#实例化Migrate对象

def make_shell_context():
#为shell定义上下文函数
	return dict(app = app, db = db, User = User, Role = Role, Permission = Permission,
					Post = Post, Follow = Follow, Comment = Comment)
	#返回一个字典，包含上下文,注册了程序，数据库实例和模型
manager.add_command("shell", Shell(make_context=make_shell_context))
#接收make_shell_context函数作为Shell的make_context属性的值
#将'Shell'和Shell类作为参数，调用manager模块中的add_command方法
#在Shell中输入命令shell时，自动加载make_shell_context中定义的上下文
manager.add_command('db', MigrateCommand)
#在Shell中可使用db命令及其子命令
#子命令init可创建迁移仓库

@manager.command
def test():
	"""Run the unit tests."""
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity = 2).run(tests)

if __name__ == '__main__':
	manager.run()
	#调用manager实例的run方法，启动程序