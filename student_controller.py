from sch_management_db import Student, Grade

class StudentService:
    @staticmethod
    def register_student(student_id, name, age, grade_id):
        try:
            grade = Grade.get(Grade.grade_id == grade_id)
            student = Student.create(
                student_id=student_id,
                name=name,
                age=age,
                grade=grade
            )
            return True, "تم تسجيل الطالب بنجاح"
        except DoesNotExist:
            return False, "الصف المحدد غير موجود"
        except IntegrityError:
            return False, "رقم الطالب مسجل مسبقاً"