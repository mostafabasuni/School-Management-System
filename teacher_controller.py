from sch_management_db import Teacher

class TeacherService:
    def __init__(self):
        pass

    @staticmethod
    def create_teacher(t_code, name, subject):
        try:            
            return {Teacher.create(teacher_code=t_code, 
                            name=name, 
                            specialization=subject)}
        except Exception as e:
            print(f"Error creating teacher: {e}")
            return None
    
    def update_teacher(self, id, teacher_code, name, subject):
        try:
            teacher = Teacher.get(Teacher.id == id)
            teacher.teacher_code = teacher_code
            teacher.name = name
            teacher.specialization = subject
            teacher.save()
            return True, "تم تحديث بيانات المعلم بنجاح"
        except Teacher.DoesNotExist:
            return False, "المعلم غير موجود"
        except Exception as e:
            return False, f"حدث خطأ أثناء التحديث: {str(e)}"

    def delete_teacher(self, id):
        try:
            teacher = Teacher.get_by_id(id)
            teacher.delete_instance()
            return True, "تم حذف المدرس بنجاح"
        except Teacher.DoesNotExist:
            return False, "المدرس غير موجود"
        except Exception as e:
            return False, f"حدث خطأ أثناء الحذف: {str(e)}"