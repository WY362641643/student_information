import os
import random
from flask import Flask, render_template, redirect, url_for, flash, abort, session, request, jsonify
from . import androids
from app.models import *
from app.users.views import send_mail

# android登录路由控制
@androids.route('/android/login', methods=['POST'])
def android_login():
    # 根据账号邮箱找到用户
    print('android,根据账号邮箱找到用户')
    email = request.form['account']
    password = request.form['password']
    user = Teachers.query.filter_by(email=email).first()
    # 比较密码和注册状态
    if user is not None and user.password == password and user.active_state == True:
        return 'ok'
    return 'error'


# 初始化Android本地数据库
@androids.route('/android/init', methods=['POST'])
def return_students():
    email = request.form['account']
    user = Teachers.query.filter_by(email=email).first()
    if user and user.students.count() != 0:
        students = []
        for student in user.students:
            students.append(student.name + ' ' + student.stu_id + ' ' + student.cls + ' ' +
                            student.addr + ' ' + student.phone + ' ')
        return ''.join(students)
    return 'error'


# Android删除学生
@androids.route('/android/delete', methods=['POST'])
def delete_student():
    email = request.form['account']
    # 找到用户
    user = Teachers.query.filter_by(email=email).first()
    # 找到要删除的学生
    student = Student.query.filter_by(stu_id=request.form['id'], user_id=user.id).first()
    if student:
        db.session.delete(student)
        return 'ok'
    return 'error'


# Android修改或者新建学生
@androids.route('/android/change', methods=['POST'])
def change_student():
    # 要修改的学生学号或者为空说明是新建学生
    old_id = request.form['old_id']
    email = request.form['account']
    id = request.form['id']
    name = request.form['name']
    cls = request.form['cls']
    addr = request.form['addr']
    phone = request.form['phone']
    # 找到用户
    user = Teachers.query.filter_by(email=email).first()
    if old_id != '':
        # 修改学生信息
        student = Student.query.filter_by(stu_id=old_id, user_id=user.id).first();
        if student:
            student.stu_id = id
            student.name = name
            student.cls = cls
            student.addr = addr
            student.phone = phone
            db.session.add(student)
            return 'ok'
        return 'error'
    else:
        # 新增学生
        # 实例化学生
        new_student = Student(stu_id=id, name=name, cls=cls, addr=addr,
                              phone=phone, user_id=user.id)
        db.session.add(new_student)
        return 'ok'
    return 'error'


# android反馈活动处理
@androids.route('/android/feedback', methods=['POST'])
def feedbakc():
    message = request.form['message']
    email = request.form['account']
    sub = "反馈信息来自:" + email
    send_mail('504629278@qq.com', sub, message)
    return 'ok'
