from sch_management_db import Student, Grade
from peewee import DoesNotExist, IntegrityError

class StudentService:
    @staticmethod    
    def register_student(student_id, name, age, grade_id, registration_date):
        print(f"Registering student: {student_id}, {name}, {age}, {grade_id}, {registration_date}")
        try:
            # تأكد من أن grade_id هو ID الصف وليس كائن Grade
            student = Student.create(
                student_id=student_id,
                name=name,
                age=age,
                grade=grade_id,  # سيتم تحويله تلقائياً لكائن Grade
                registration_date=registration_date
            )
            return True, "تم تسجيل الطالب بنجاح"
        except DoesNotExist:
            return False, "الصف المحدد غير موجود"
        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                return False, "رقم الطالب مسجل مسبقاً"
            return False, f"خطأ في قاعدة البيانات: {str(e)}"