from sch_management_db import Grade, Course

class GradeService:
    def __init__(self):
        pass

    
    def create_grade(self, grade_id, name, level, section):
        try:
            return {Grade.create(grade_id=grade_id,
                    name=name,
                    level=level,
                    section=section)}
        except Exception as e:
            return False, f"خطأ في إنشاء المادة: {str(e)}"

    def update_grade(self, id, grade_id, name, level, section):
        try:
            grade = Grade.get(Grade.id == id)
            grade.grade_id = grade_id
            grade.name = name
            grade.level = level
            grade.section = section
            grade.save()
            return True, "تم تحديث بيانات الصف بنجاح"
        except Grade.DoesNotExist:
            return False, "الصف غير موجود"
        except Exception as e:
            return False, f"حدث خطأ أثناء التحديث: {str(e)}"

    def delete_grade(self, id):
        try:
            grade = Grade.get_by_id(id)
            grade.delete_instance()
            return True, "تم حذف الصف بنجاح"
        except Grade.DoesNotExist:
            return False, "الصف غير موجود"
        except Exception as e:
            return False, f"حدث خطأ أثناء الحذف: {str(e)}"