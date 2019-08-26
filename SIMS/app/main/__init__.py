'''
此模块为数据逻辑操作包
'''

# 声明蓝图
from flask import Blueprint
main =Blueprint('main',__name__)
from . import views