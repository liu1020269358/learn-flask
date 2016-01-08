# -*- coding: utf-8 -*-

import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
	def setUp(self):
	#相当于初始化函数，在每个测试函数运行前运行
		self.app = create_app('testing')
		#将'testing'传入create_app()初始化整个程序
		self.app_context = self.app.app_context()
		#创建应用上下文
		self.app_context.push()
		#将应用上下文推入栈中
		db.create_all()
		#创建一个初始数据库
		
	def tearDown(self):
	#在所有测试函数运行后运行，收尾的函数
		db.session.remove()
		#删除会话
		db.drop_all()
		#删除所有的表
		self.app_context.pop()
		#删除应用上下文
		
	def test_app_exists(self):
		self.assertFalse(current_app is None)
		#验证current_app是否存在，也就是当前应用是否创建成功
	def test_app_testing(self):
		self.assertTrue(current_app.config['TESTING'])
		#验证程序的配置是否在为'TESTING'，确保当前程序是在测试的配置条件下运行