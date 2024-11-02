from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'student_management'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    teachers = db.relationship('Teacher', secondary='teacher_student', back_populates='students')

class Teacher(db.Model):
    __tablename__ = 'teacher_management'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    students = db.relationship('Student', secondary='teacher_student', back_populates='teachers')

class TeacherStudent(db.Model):
    __tablename__ = 'teacher_student'
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_management.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_management.id'), primary_key=True)

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(100))
    sign_in_time = db.Column(db.DateTime, default=datetime.utcnow)
