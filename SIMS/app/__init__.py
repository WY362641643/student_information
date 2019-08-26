'''
app包,模块化所有程序处理相关的文件
__init__.py
    1.构建Flask程序实例及配置
    2.构建SQLAlchemy数据库实例
'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

db = SQLAlchemy()

def create_app():
    #创建flask程序实例
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = "suibianxie"
    app.config['SQLALCHEMY_DATABASE_URI']="mysql+pymysql://root:123456@localhost:3306/sims"
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    #关联db和app
    db.init_app(app)
    bootstrap = Bootstrap(app)

    # 将main蓝图程序与app相关联
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .androids import androids as androids_blueprint
    app.register_blueprint(androids_blueprint)
    # 将users蓝图程序与app相关联
    from .users import users as users_blueprint
    app.register_blueprint(users_blueprint)


    # 返回Flask程序实例
    return app