# -*- coding: utf-8 -*-

from flask import Blueprint

auth = Blueprint('auth', __name__)
#����һ����ͼ

from . import views
#��auth�е���views��viewsģ�鱣���¼ҳ���·��