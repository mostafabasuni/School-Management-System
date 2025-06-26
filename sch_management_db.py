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
    id = AutoField(primary_key=True)  # هذا الحقل ضروري
    grade_code = CharField(unique=True)  # مثلاً: "G1", "G2" أو "PRIM-1" للمرحلة الابتدائية
    name = CharField()                 # اسم واضح مثل "الصف الأول الابتدائي"
    level = CharField(null=True)       # المرحلة (ابتدائي/متوسط/ثانوي)
    term = CharField(null=True)     # الفصل الدراسي (الأول - الثاني.)
    academic_year = CharField()
    is_calculated = BooleanField(default=False)  # لتتبع ما إذا تم حساب النتائج
    
    def update_class_totals(self, academic_year):
        """تحديث نتائج جميع طلاب الصف"""
        try:
            with db.atomic():
                students = Student.select().where(Student.grade == self.id)
                
                for student in students:
                    totals = ScoreService.calculate_student_totals(student.id, academic_year)
                    if totals:
                        student.midterm_total = totals['midterm_total']
                        student.final_total = totals['final_total']
                        student.overall_average = totals['overall_total']
                        student.save()
                
                self.is_calculated = True
                self.save()
            
            return True, f"تم تحديث نتائج {students.count()} طالباً"
        
        except Exception as e:
            return False, f"خطأ في تحديث الصف: {str(e)}"
    
class Student(BaseModel):
    student_code = CharField(unique=True)
    name = CharField()
    age = IntegerField()
    grade = ForeignKeyField(Grade, field=Grade.id, backref='students')  # تحديد الحقل المرتبط صراحةً
    registration_date = DateField(default=datetime.date.today)
    midterm_total = FloatField(default=0.0)
    final_total = FloatField(default=0.0)
    overall_average = FloatField(default=0.0)
    def update_totals(self, academic_year):
        """تحديث المجاميع في سجل الطالب"""
        totals = ScoreService.calculate_student_totals(self.id, academic_year)
        if totals:
            self.midterm_total = totals['midterm_total']
            self.final_total = totals['final_total']
            self.overall_average = totals['overall_total']
            self.save()

class Teacher(BaseModel):
    teacher_code = CharField(unique=True)
    name = CharField()
    specialization = CharField()

class Course(BaseModel):
    course_code = CharField(unique=True)
    name = CharField()
    grade = ForeignKeyField(Grade, backref='courses', on_delete='CASCADE')
    teacher = ForeignKeyField(Teacher, backref='courses_teaching', null=True)
    
class StudentScore(BaseModel):
    student = ForeignKeyField(Student, backref='enrollments')
    course = ForeignKeyField(Course, backref='enrollments')
    midterm_score = FloatField(null=True)
    final_score = FloatField(null=True)
    academic_year = CharField()      # السنة الدراسية (مثل 2023-2024)    
    class Meta:
        indexes = (
            (('student', 'course', 'academic_year'), True),  # منع التكرار
        )

    '''def calculate_final_grade(self):
        return (self.midterm_score * 0.5) + (self.final_score * 0.5)
'''

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
db.create_tables([User, Student, Teacher, Grade, Course, StudentScore, Permissions])
# Close the database connection when done
'''student = Student()
student.student_code = "ST1Prime1"
student.name = "Ahmed"
student.age = 10    
student.grade = Grade.get(Grade.grade_code == "PRIM-1")  # Assuming "PRIM-1" is a valid grade_code
student.registration_date = datetime.date.today()'''
db.close()




