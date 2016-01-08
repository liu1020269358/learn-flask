# -*- coding: utf-8 -*-

from flask import Blueprint

auth = Blueprint('auth', __name__)
#创建一个蓝图

from . import views
#从auth中导入views，views模块保存登录页面的路由