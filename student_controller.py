from sch_management_db import Student, Grade
from peewee import DoesNotExist, IntegrityError

class StudentService:
    @staticmethod    
    def register_student(student_id, name, age, grade_id, registration_date):        
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
                return False, "هذاالطالب تم تسجيله مسبقاً"
            return False, f"خطأ في قاعدة البيانات: {str(e)}"
        
    @staticmethod
    def student_update(student_id, name, age, grade_id, registration_date):
        print(f"Updating student: {student_id}, {name}, {age}, {grade_id}")
        try:
            student = Student.get(Student.student_id == student_id)
            if name is not None:
                student.name = name
            if age is not None:
                student.age = age
            if grade_id is not None:
                student.grade = grade_id  # سيتم تحويله تلقائياً لكائن Grade
            student.save()
            return True, "تم تحديث بيانات الطالب بنجاح"
        except DoesNotExist:
            return False, "الطالب غير موجود"
        except IntegrityError as e:
            return False, f"خطأ في قاعدة البيانات: {str(e)}"
    
    @staticmethod    
    def student_delete(student_id):
        try:
            student = Student.get(Student.student_id == student_id)
            student.delete_instance()
            return True, "تم حذف الطالب بنجاح"
        except DoesNotExist:
            return False, "الطالب غير موجود"
        except IntegrityError as e:
            return False, f"خطأ في قاعدة البيانات: {str(e)}"    