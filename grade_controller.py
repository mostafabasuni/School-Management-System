from sch_management_db import Grade, Course

class GradeService:
    def __init__(self):
        pass

    
    def create_grade(self, grade_code, name, section, level, term, academic_year):
        try:
            Grade.create(grade_code=grade_code,
                    name=name,
                    section=section,  # إضافة القسم
                    level=level,
                    term=term,
                    academic_year=academic_year)
            return True, "تم إنشاء الصف بنجاح"
        except Exception as e:
            return False, f"خطأ تكرار بيانات"

    def update_grade(self, grade_id, grade_code, section, name, level, term, academic_year):
        try:
            grade = Grade.get(Grade.id == grade_id)
            grade.grade_code = grade_code
            grade.section = section  # تحديث القسم
            grade.name = name
            grade.level = level
            grade.term = term
            grade.academic_year = academic_year
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