from . import db


# 老师模型
class Teachers(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64))
    # 课程
    course = db.Column(db.String(64))
    # 身份
    role = db.Column(db.String(64), default='教师')
    # 验证邮箱码
    active_code = db.Column(db.String(10))
    # 激活状态
    active_state = db.Column(db.Boolean, default=False)

    # 冻结状态
    frozen = db.Column(db.Boolean, default=False)
    # 增加对Student类的多对多操作(关联属性和反向引用关系属性)
    studentlist = db.relationship(
        "Student",
        secondary='student_teacher',
        lazy='dynamic',
        backref=db.backref(
            "teacher",
            lazy="dynamic"
        )
    )

# 学生模型
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    stu_id = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64))
    pwd = db.Column(db.String(64))
    role = db.Column(db.String(64), default='学生')
    # 班级
    cls = db.Column(db.String(64))
    # 寝室
    addr = db.Column(db.String(64))
    phone = db.Column(db.String(64))



# 实体类- StudentCourse,表示Student和Course之间的第三张关联表
class StudentTeachers(db.Model):
    __tablename__ = 'student_teacher'
    id = db.Column(db.Integer, primary_key=True)
    # 外键:引用自student表的主键
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id")
    )
    # 外键:引用自teachers表的主键
    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey('teachers.id')
    )
