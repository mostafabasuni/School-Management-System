from sch_management_db import Teacher

class TeacherService:
    def __init__(self):
        pass

    @staticmethod
    def create_teacher(id, name, subject):
        try:
            teacher = Teacher.create(teacher_id=id, name=name, specialization=subject)
            return teacher
        except Exception as e:
            print(f"Error creating teacher: {e}")
            return None
    
    def update_teacher(self, id, teacher_id, name, subject):
        try:
            teacher = Teacher.get(Teacher.id == id)
            teacher.teacher_id = teacher_id
            teacher.name = name
            teacher.specialization = subject
            teacher.save()
            return True, "تم تحديث بيانات المعلم بنجاح"
        except Teacher.DoesNotExist:
            return False, "المعلم غير موجود"
        except Exception as e:
            return False, f"حدث خطأ أثناء التحديث: {str(e)}"

