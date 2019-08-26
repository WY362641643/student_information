import os
import random
from flask import Flask, render_template, redirect, url_for, flash, abort, session, request, jsonify, \
    send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, RadioField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from threading import Thread
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import *
from . import main
from ..models import *


# 教师主页路由控制
@main.route('/u/<int:id>')
def user(id):
    # 验证是否已登录
    if session.get('user_id') is None or id != session.get('user_id'):
        session['user_id'] = None
        flash("未登录")
        return redirect(url_for('users.login'))
    user = Teachers.query.filter_by(id=id).first()
    students = user.studentlist.all()
    # 验证身份
    if not (user.role != '教师' or user.role != '班主任'):
        abort(400);
    return render_template('user.html', user=user,students=students)


# 学生主页路由控制 (未修改)
@main.route('/s/<int:id>')
def student(id):
    if session.get('user_id') is None or id != session.get('user_id'):
        session['user_id'] = None
        flash("未登录")
        return redirect(url_for('users.login'))
    user = Student.query.filter_by(id=id).first()
    teachers = user.teacher.all()
    if user.role != '学生':
        abort(400);
    return render_template('student.html', user=user, teachers=teachers)


# 教师个人信息路由控制
@main.route('/u/<int:id>/account')
def account(id):
    if session.get('user_id') is None or id != session.get('user_id'):
        session['user_id'] = None
        flash("未登录")
        return redirect(url_for('users.login'))
    user = Teachers.query.filter_by(id=id).first()
    if user.role == '其他人员':
        return render_template('error.html', code='404')
    num = user.studentlist.count()
    return render_template('account.html', user=user, num=num)


# 学生选择教师路由控制
@main.route('/s/<int:user_id>/<int:teacher_id>')
def detail(user_id, teacher_id):
    if session.get('user_id') is None or user_id != session.get('user_id'):
        session['user_id'] = None
        flash("未登录")
        return redirect(url_for('users.login'))
    user = Student.query.filter_by(id=user_id).first()
    if user.role != '学生':
        abort(400);
    teacher = Teachers.query.filter_by(id=teacher_id).first()
    # 为了更改id和role重新构建用户传递给跳转页面
    x_user={
        'name':teacher.name,
        "rmg":'这是老师的详情页,(通知,一般介绍..等等)'}
    return render_template('detail.html', user=x_user)


# 教师新增学生路由控制
@main.route('/u/<int:id>/add', methods=['GET', 'POST'])
def add(id):
    if session.get('user_id') is None or id != session.get('user_id'):
        session['user_id'] = None
        flash("未登录")
        return redirect(url_for('users.login'))
    user = Teachers.query.filter_by(id=id).first()
    if user.role== '教师':
        form = ClsAddForm()
        if form.validate_on_submit():
            cls_id = form.cls.data
            # 添加第三张表
            new_student_list = Student.query.filter_by(cls=cls_id).all()
            teacher = Teachers.query.filter_by(id=id).first()
            for new_student in new_student_list:
                print(new_student)
                teacher.studentlist.append(new_student)
            flash("添加成功")
            return redirect('/u/' + str(id) + '/add')
    elif user.role == '班主任':
        form = AddForm()
        if form.validate_on_submit():
            # 构建新学生并保存
            l = [form.stu_id.data, form.name.data, form.pwd.data,
                 form.cls.data, form.addr.data, form.phone.data, id]
            print('打印添加进Student的学生信息', l)
            # 添加学生信息
            new_student = Student(stu_id=form.stu_id.data, name=form.name.data, pwd=form.pwd.data,
                                  cls=form.cls.data, addr=form.addr.data, phone=form.phone.data)
            db.session.add(new_student)
            # 添加第三张表
            teacher = Teachers.query.filter_by(id=id).first()
            teacher.studentlist.append(new_student)
            flash("添加成功")
            return redirect('/u/' + str(id) + '/add')
    else:
        abort(400);
    return render_template('form.html', form=form, user=user)


# 教师搜索学生路由控制
@main.route('/u/<int:id>/search', methods=['GET', 'POST'])
def search(id):
    if session.get('user_id') is None or id != session.get('user_id'):
        session['user_id'] = None
        flash("未登录")
        return redirect(url_for('users.login'))
    form = SearchForm()
    user = Teachers.query.filter_by(id=id).first()
    if not (user.role != '教师' or user.role != '班主任'):
        abort(400);
    students = user.studentlist.all()
    hide = set()  # 不需显示的学生集合
    if form.validate_on_submit():
        student_list = user.studentlist.all()
        for student in student_list:
            word = str(student.stu_id) + ' ' + student.name \
                   + ' ' + student.cls + ' ' + \
                   student.addr + ' ' + student.phone
            # 没有关键字则添加进hide集合
            if form.keyword.data not in word:
                hide.add(student)
    return render_template('form.html', form=form, search=True,
                           user=user, hide=hide,students=students)


# 教师删除学生路由控制
@main.route('/u/<int:id>/delete', methods=['POST'])
def delete(id):
    if session.get('user_id') is None or id != session.get('user_id'):
        session['user_id'] = None
        flash("未登录")
        return redirect(url_for('users.login'))
    user = Teachers.query.filter_by(id=id).first()
    if not (user.role != '教师' or user.role != '班主任'):
        abort(400);
    students = user.studentlist.all()
    for student in students:
        flag = student.query.filter_by(stu_id=request.form.get('stu_id')).first()
    # student = Student.query.filter_by(stu_id=request.form.get('stu_id'), user_id=id).first()
        if flag:
            db.session.delete(student)
        return jsonify({'result': 'success'})


# 教师更改学生路由控制
@main.route('/u/<int:id>/change', methods=['POST'])
def change(id):
    if session.get('user_id') is None or id != session.get('user_id'):
        session['user_id'] = None
        flash("未登录")
        return redirect(url_for('users.login'))
    user = Teachers.query.filter_by(id=id).first()
    if not (user.role != '教师' or user.role != '班主任'):
        abort(400);
    elif user.role !='班主任' :
        flash('您没有权限')
        return redirect('/u/' + str(id) + '/account')
    # 更改学生信息
    students = user.studentlist.all()
    print(students)
    for student in students:
        flag = student.query.filter_by(id=request.form.get('id')).first()
        if flag:
    # student = Student.query.filter_by(id=request.form.get('id')).first()
            student.stu_id = request.form.get('stu_id')
            student.name = request.form.get('name')
            student.cls = request.form.get('cls')
            student.addr = request.form.get('addr')
            student.phone = request.form.get('phone')
            db.session.add(student)
            return jsonify({'result': 'success'})


# 管理员控制台路由控制
@main.route('/admin/control', methods=['GET', 'POST'])
def control():
    if not session.get('admin'):
        abort(400)
    users = Teachers.query.all()
    return render_template('control.html', users=users)


# 管理员新增用户路由控制
@main.route('/admin/add', methods=['GET', 'POST'])
def admin_add():
    if not session.get('admin'):
        abort(400)
    form = AdminAddForm()
    if form.validate_on_submit():
        # 简化增加用户,自动生成随机码
        n = []
        for i in range(10):
            n.append(str(random.randint(0, 9)))
        active_code = ''.join(n)
        # 自动构建通过验证的用户
        user = Teachers(name=form.name.data, email=form.email.data, course=form.course.data,
                        password=form.password.data,
                        role=form.role.data, active_code=active_code, active_state=True)
        db.session.add(user)
        flash('增加成功')
        return redirect(url_for('main.admin_add'))
    return render_template('adminadd.html', form=form)


# 管理员删除用户路由控制
@main.route('/admin/delete', methods=['POST'])
def admin_delete():
    if session.get('admin'):
        user = Teachers.query.filter_by(id=request.form.get('id')).first()
        if user:
            db.session.delete(user)
        return 'ok'
    abort(400)


# 管理员冻结用户路由控制
@main.route('/admin/frozen', methods=['POST'])
def admin_frozen():
    if session.get('admin'):
        user = Teachers.query.filter_by(id=request.form.get('id')).first()
        if user:
            user.frozen = True
            db.session.add(user)
        return 'ok'
    abort(400)


# 管理员解冻用户路由控制
@main.route('/admin/normal', methods=['POST'])
def admin_normal():
    if session.get('admin'):
        user = Teachers.query.filter_by(id=request.form.get('id')).first()
        user.frozen = False
        db.session.add(user)
        return 'ok'
    abort(400)


# 教师新增学生表单模型
class AddForm(FlaskForm):
    # 检测学号是否存在
    def student_exist(self, field):
        user = Teachers.query.filter_by(id=session.get('user_id')).first()
        student_list = user.studentlist.all()
        for student in student_list:
            if student.stu_id == field.data:
                raise ValidationError("该学号学生已存在")
    stu_id = StringField("学生学号", validators=[DataRequired(message="这能空?"), Length(6, 15, "6-15位"), student_exist])
    name = StringField("学生姓名", validators=[DataRequired(message="这能空?"), Length(-1, 10, "名字过长,10位以内")])
    pwd = StringField("登录密码", validators=[DataRequired(message="这能空?"), Length(6, 10, "密码在6-10位之间")])
    cls = StringField("专业班级", validators=[DataRequired(message="没有数据不好交差"), Length(-1, 15, "精简一下,15位以内")])
    addr = StringField("所在寝室", validators=[DataRequired(message="没有数据不好交差"), Length(-1, 15, "字太多了,15位以内")])
    phone = StringField("联系方式", validators=[DataRequired(message="没有数据不好交差")])
    add = SubmitField("添加吧,皮卡丘!!!")

# 科任老师添加学生
class ClsAddForm(FlaskForm):
    # 检测班级是否存在
    def cls_exist(self, field):
        user = Teachers.query.filter_by(id=session.get('user_id'))\
            .first().studentlist.all()
        flag = Student.query.filter_by(cls=field.data).all()
        print('user', type(user), user)
        print('flag',type(flag),flag)
        if not flag:
            raise ValidationError("没有这个班级")
        elif flag[0] in user:
            raise ValidationError("您已添加该班级")
    cls = StringField("专业班级", validators=[DataRequired(message="没有数据不好交差"), Length(-1, 15, "精简一下,15位以内"),cls_exist])
    add = SubmitField("添加吧,皮卡丘!!!")


# 教师搜索学生表单模型
class SearchForm(FlaskForm):
    keyword = StringField("输入查询关键字", validators=[DataRequired(message="输入不能为空")])
    search = SubmitField("Find It!")


# 管理员增加用户表单模型
class AdminAddForm(FlaskForm):
    # 检测邮箱唯一性
    def email_unique(self, field):
        if Teachers.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱存在')

    name = StringField('用户名', validators=[DataRequired()])
    email = StringField('用户邮箱', validators=[DataRequired(), email_unique])
    password = StringField('用户密码', validators=[DataRequired()])
    course = StringField('课程', validators=[DataRequired()])
    role = RadioField('身份', choices=[('教师', '教师'),('班主任','班主任'), ('其他职位', '其他职位')], default='教师')
    add = SubmitField("增加用户")


# 错误页面路由控制
@main.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code='404'), 404


@main.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', code='500'), 500


@main.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code='400'), 500


# 文件下载路由控制
@main.route('/download/<path:filename>')
def download(filename):
    path = os.getcwd()
    print(path)
    return send_from_directory(path, filename, as_attachment=True)
