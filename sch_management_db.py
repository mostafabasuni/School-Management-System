from peewee import *
import datetime
import bcrypt

db = MySQLDatabase(
    'school_management',
    user='root',
    password="",
    host='localhost',
    port=3306
)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    fullname = CharField()
    user_name = CharField(unique=True)
    job = CharField()
    password = CharField()
    is_admin = BooleanField(default=False)

class Grade(BaseModel):
    grade_id = CharField(unique=True)  # مثلاً: "G1", "G2" أو "PRIM-1" للمرحلة الابتدائية
    name = CharField()                 # اسم واضح مثل "الصف الأول الابتدائي"
    level = CharField(null=True)       # المرحلة (ابتدائي/متوسط/ثانوي)
    section = CharField(null=True)     # الفصل (أ، ب، ج...)
    
class Student(BaseModel):
    student_id = CharField(unique=True)
    name = CharField()
    age = IntegerField()
    grade = ForeignKeyField(Grade, backref='students')
    registration_date = DateField(default=datetime.date.today)

class Teacher(BaseModel):
    teacher_id = CharField(unique=True)
    name = CharField()
    specialization = CharField()

class Course(BaseModel):
    course_id = CharField(unique=True)
    name = CharField()
    grade = ForeignKeyField(Grade, backref='courses', on_delete='CASCADE')
    teacher = ForeignKeyField(Teacher, backref='courses_teaching', null=True)
    
class StudentCourse(BaseModel):
    student = ForeignKeyField(Student, backref='enrollments')
    course = ForeignKeyField(Course, backref='enrollments')
    midterm_score = FloatField(null=True)
    final_score = FloatField(null=True)
    

    def calculate_final_grade(self):
        return (self.midterm_score * 0.4) + (self.final_score * 0.6)

    class Meta:
        indexes = (
            (('student', 'course'), True),
        )

class Permissions(BaseModel):
    user = ForeignKeyField(User, backref='permissions', on_update='CASCADE', on_delete='CASCADE')
    users_tab = BooleanField()
    teachers_tab = BooleanField()
    courses_tab = BooleanField()
    grades_tab = BooleanField()
    students_tab = BooleanField()
    scores_tab = BooleanField()
    student_score_tab = BooleanField()
    permissions_tab = BooleanField()

db.connect()
db.create_tables([User, Student, Teacher, Grade, Course, StudentCourse, Permissions])
# Close the database connection when done
db.close()




