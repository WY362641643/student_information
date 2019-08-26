'''
此模块为数据逻辑操作包
'''

# 声明蓝图
from flask import Blueprint
androids =Blueprint('androids',__name__)
from . import views