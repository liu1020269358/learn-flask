# -*- coding: utf-8 -*-

from flask import Blueprint

main = Blueprint('main', __name__)
#实例化Blueprint类对象，创建main实例

from . import views,errors
#从app\main文件夹中导入views和errors模块
#views模块保存主页面的路由，errors模块保存程序的错误处理程序
from ..models import Permission

@main.app_context_processor
def inject_permission():
	return dict(Permission = Permission)
#把Permission添加到上下文中，以便让所有模块都可以访问