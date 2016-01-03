# -*- coding: utf-8 -*-

from flask import Blueprint

main = Blueprint('main', __name__)
#实例化Blueprint类对象，创建main实例

from . import views,errors
#从app\main文件夹中导入views和errors模块
#views模块保存程序的路由，errors模块保存程序的错误处理程序