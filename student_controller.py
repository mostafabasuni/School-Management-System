from sch_management_db import Student, Grade
from peewee import DoesNotExist, IntegrityError

class StudentService:
    @staticmethod    
    def register_student(student_code, name, age, grade_id, registration_date):        
        try:
            # تأكد من أن grade_id هو ID الصف وليس كائن Grade
            student = Student.create(
                student_code=student_code,
                name=name,
                age=age,
                grade=grade_id,  # سيتم تحويله تلقائياً لكائن Grade
                registration_date=registration_date
            )
            return True, "تم تسجيل الطالب بنجاح"
        except DoesNotExist:
            return False, "الطالب المحدد غير موجود"
        except Exception as e:
            return False, f"خطأ تكرار بيانات"
        
    @staticmethod
    def student_update(student_id, student_code, name, age, grade_id, registration_date):
        
        try:
            student = Student.get(Student.id == student_id)            
            student.student_code = student_code
            student.name = name            
            student.age = age            
            student.grade_id = grade_id  # سيتم تحويله تلقائياً لكائن Grade
            student.registration_date = registration_date
            student.save()
            return True, "تم تحديث بيانات الطالب بنجاح"
        except DoesNotExist:
            return False, "الطالب غير موجود"
        except IntegrityError as e:
            return False, f"حدث خطأ أثناء التحديث"
    
    @staticmethod    
    def student_delete(student_id):
        try:
            student = Student.get(Student.id == student_id)
            student.delete_instance()
            return True, "تم حذف الطالب بنجاح"
        except DoesNotExist:
            return False, "الطالب غير موجود"
        except IntegrityError as e:
            return False, f"خطأ في قاعدة البيانات: {str(e)}"    