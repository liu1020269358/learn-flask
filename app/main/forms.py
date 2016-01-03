# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameForm(Form):
#定义一个继承自Form类的NameForm类
    name = StringField('What is your name?', validators=[Required()])
	#实例化StringField类为name字段
	#可选参数validators制定一个一个由验证函数构成的列表
	#其中Required()验证确保提交的字段不为空
    submit = SubmitField('Submit')
	#实例化SubmitField类为submit提交按钮