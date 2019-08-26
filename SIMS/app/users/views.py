# encoding='utf-8'
# 导入所需模块
import os
import random
from flask import Flask,render_template, redirect, url_for, flash, abort, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, RadioField
from wtforms.validators import Email, DataRequired, Length, EqualTo
from flask_mail import Mail, Message
from threading import Thread
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from . import users
from ..models import *

# 邮件配置
mail_app = Flask(__name__)

# 实例化所需模块
# 配置发送邮件
mail_app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.qq.com',
    MAIL_PROT=25,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='362641643@qq.com',
    MAIL_PASSWORD='wyysvcjgjqbubjgb',
    MAIL_DEBUG=True
)
mail = Mail(mail_app)


# 异步发送邮件
def send_async_mail(mail_app, msg):
    with mail_app.app_context():
        mail.send(msg)
        print('发送邮件成功,请查收')


def send_mail(to, sub, link):
    msg = Message('学生信息管理系统的邮件来啦', sender='362641643@qq.com', recipients=[to])
    msg.body = sub + link
    msg.html = '<h1>' + sub + '</h1><a href=' + link + '>' + link + '</a>'
    thr = Thread(target=send_async_mail, args=[mail_app, msg])
    thr.start()
    return thr


# 管理员表单模型
class AdminForm(FlaskForm):
    # 邮箱验证
    def account_check(self, field):
        print(field.data)
        if field.data != 'adminsuper@163.com':
            raise ValidationError('你可能是假的管理员')

    # 密码验证
    def password_check(self, field):
        print(field.data)
        if field.data != 'superuser':
            raise ValidationError('你可能是假的管理员')

    email = StringField("管理员邮箱", validators=[DataRequired(message='邮箱是空的请加油'),
                                             Email(message=u'不是邮箱'), account_check])
    password = PasswordField("管理员密码", validators=[DataRequired(message='密码忘了哦'), password_check])
    login = SubmitField("有请最牛逼的管理员登录")


# 用户登录表单模型
class LoginForm(FlaskForm):
    # 验证用户是否存在
    def email_exist(self, field):
        if '@' in field.data:
            if not Teachers.query.filter_by(email=field.data).first():
                raise ValidationError('这邮箱不能用啊')
        else:
            if not Student.query.filter_by(stu_id=field.data).first():
                raise ValidationError('这学号不能用啊')

    email = StringField("教师邮箱/学生学号", validators=[DataRequired(message='邮箱是空的请加油'),
                                                 Length(6, message=u'你这是账号吗?'), email_exist])
    password = PasswordField("密码", validators=[DataRequired(message='密码都没有咋登录')])
    role = RadioField('身份', choices=[('学生', '学生'), ('教师', '教师')], default='学生')
    login = SubmitField("登录")


# 用户注册表单模型
class SignupForm(FlaskForm):
    def email_unique(self, field):
        pass
        print('验证邮箱')
        if Teachers.query.filter_by(email=field.data).first():
            raise ValidationError('为啥用人家的邮箱?')

    # 检测密码中是否有空格
    def password_noblank(self, field):
        print('检查密码')
        for s in field.data:
            if s == ' ':
                raise ValidationError('密码有空格,不要搞事情!')

    name = StringField('姓名', validators=[DataRequired(message='必填')])
    email = StringField("邮箱", validators=[DataRequired(message='连邮箱都没有?'),
                                          Email(message='神TM邮箱'), email_unique])
    course = StringField('课程', validators=[DataRequired()])

    password = PasswordField("密码", validators=[DataRequired(message='密码不设置的?'),
                                               Length(6, message='这么短?最少六位'), password_noblank])
    confirm = PasswordField("确认密码", validators=[DataRequired(message='确认一下是好的'),
                                                EqualTo('password', "两次密码不一样!")])
    role = RadioField('身份', choices=[('教师', '教师'),('班主任','班主任')], default='教师')

    signup = SubmitField("注册")


# 找回密码表单模型
class ForgetForm(FlaskForm):
    def email_exist(self, field):
        if not Teachers.query.filter_by(email=field.data).first():
            raise ValidationError('没有这个邮箱')

    def password_noblank(self, field):
        for s in field.data:
            if s == ' ':
                raise ValidationError('密码有空格,搞事情!')

    email = StringField("注册时邮箱", validators=[DataRequired(message='邮箱不能为空'),
                                             Email(message='这也叫邮箱?'), email_exist])
    password = PasswordField("密码", validators=[DataRequired(message='密码不能为空'),
                                               Length(6, message='密码搞这么短干嘛? 最少六位'), password_noblank])
    confirm = PasswordField("确认密码", validators=[DataRequired(message='密码不能为空'),
                                                EqualTo('password', "两次密码不一致")])
    getback = SubmitField("确认")


# 登录路由控制
@users.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        role = form.role.data
        email = form.email.data
        if role == '教师':
            print('教师登录')
            user = Teachers.query.filter_by(email=email).first()
            # 验证是否被冻结
            if user.frozen:
                flash("你的账户已被冻结")
                return redirect(url_for('users.login'))
            # 验证是否激活邮箱
            if user.active_state == False:
                n = []
                for i in range(10):
                    n.append(str(random.randint(0, 9)))
                active_code = ''.join(n)
                user.active_code = active_code
                sub = "请点击下方链接继续完成注册："
                link = '127.0.0.1:5000/c/' + str(user.id) + '/' + active_code
                print(str(email) + '邮箱的验证链接' + str(link))
                send_mail(email, sub, link)
                flash("请查收邮件以完成注册")
                return redirect(url_for('users.login'))
            # 验证密码是否正确
            elif user.password != form.password.data:
                flash("密码不正确")
                return redirect(url_for('users.login'))
            # 记住登录状态
            session['user_id'] = user.id
            print('重定向教师')
            return redirect('/u/' + str(user.id))
        else:
            print('学生登录')
            user = Student.query.filter_by(stu_id=email).first()
            # 验证密码是否正确
            if user.pwd != form.password.data:
                flash("密码不正确")
                return redirect(url_for('users.login'))
            # 记住登录状态
            session['user_id'] = user.id
            print('重定向学生')
            return redirect('/s/' + str(user.id))
    print('form: ', form)
    return render_template('form.html', form=form)


# 退出路由控制
@users.route('/logout')
def logout():
    # 管理员退出
    if session.get('admin'):
        session['admin'] = None
    # 普通用户退出
    elif session.get('user_id') is None:
        flash("未登录")
        return redirect(url_for('users.login'))
    flash("退出成功")
    session['user_id'] = None
    return redirect(url_for('users.login'))


# 注册路由邮件控制
@users.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # 生成随机码
        n = []
        for i in range(10):
            n.append(str(random.randint(0, 9)))
        active_code = ''.join(n)
        # 实例化用户
        new_user = Teachers(name=form.name.data, email=form.email.data, course=form.course.data,
                            password=form.password.data,
                            role=form.role.data, active_code=active_code)
        # 新增用户
        db.session.add(new_user)
        # 发送验证邮件
        user = Teachers.query.filter_by(email=form.email.data).first()
        sub = "请点击下方链接继续完成注册："
        link = '127.0.0.1:5000/c/' + str(user.id) + '/' + active_code
        print(str(new_user.email) + '邮箱的验证链接' + str(link))
        send_mail(new_user.email, sub, link)

        flash("请查收邮件以继续完成注册")
        return redirect(url_for('users.login', _external=True))
    return render_template('form.html', form=form)


# 验证邮箱路由控制
@users.route('/c/<int:id>/<active_code>')
def check(id, active_code):
    user = Teachers.query.filter_by(id=id).first()
    # 验证随机码是否匹配
    if user is not None and user.active_code == active_code:
        user.active_state = True
        db.session.add(user)
        return render_template('success.html', action="注册")
    abort(400)


# 找回密码路由控制
@users.route('/forget', methods=['GET', 'POST'])
def forget():
    form = ForgetForm()
    if form.validate_on_submit():
        # 发送找回密码邮件
        user = Teachers.query.filter_by(email=form.email.data).first()
        sub = "请点击下方链接继续完成密码更改："
        link = '127.0.0.1:5000/f/' + str(user.id) + '/' + user.active_code + '/' + form.password.data
        flash("请查收邮件以完成密码更改")
        print(str(user.email) + '邮箱的验证链接' + str(link))
        send_mail(user.email, sub, link)

        return redirect(url_for('users.login'))
    return render_template("form.html", form=form)


# 找回密码邮箱验证路由控制
@users.route('/f/<int:id>/<active_code>/<password>')
def new_password(id, active_code, password):
    user = Teachers.query.filter_by(id=id).first()
    if user is not None and user.active_code == active_code:
        # 更改密码并存入数据库
        user.password = password
        db.session.add(user)
        return render_template('success.html', action="密码更改")
    abort(400)


# 错误页面路由控制
@users.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code='404'), 404


# 管理员登录路由控制
@users.route('/admin', methods=['GET', 'POST'])
def admin():
    form = AdminForm()
    if form.validate_on_submit():
        session['admin'] = True
        return redirect('/admin/control')
    return render_template('form.html', form=form)


@users.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', code='500'), 500


@users.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code='400'), 500
