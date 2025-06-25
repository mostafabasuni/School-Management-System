from sch_management_db import Course, Teacher, Grade
from peewee import DoesNotExist

class CourseService:
    @staticmethod
    def create_course(course_code, name, grade_id, teacher_id):
        try:
            course = Course.create(
                course_code=course_code,
                name=name,
                grade=grade_id,
                teacher=teacher_id
            )
            return True, "تم إنشاء المادة الدراسية بنجاح"
        except DoesNotExist:
            return False, "المدرس أو الصف غير موجود"
        except Exception as e:
            return False, f"خطأ في إنشاء المادة: {str(e)}"

    @staticmethod
    def get_all_courses():
        return Course.select()

    
    @staticmethod
    def update_course(course_id, name, grade_id, teacher_id=None):
        try:
            # التحقق من وجود المادة الدراسية
            course = Course.get(Course.course_id == course_id)
            
            # التحقق من وجود الصف والمدرس (إذا كان معطى)
            grade = Grade.get(Grade.grade_id == grade_id)
            teacher = Teacher.get(Teacher.teacher_id == teacher_id) if teacher_id else None
            
            # تحديث البيانات
            course.name = name
            course.grade = grade
            course.teacher = teacher
            course.save()
            
            return True, "تم تحديث المادة الدراسية بنجاح"
        
        except DoesNotExist:
            return False, "المادة أو الصف أو المدرس غير موجود"
        except Exception as e:
            return False, f"حدث خطأ أثناء التحديث: {str(e)}"

    @staticmethod
    def delete_course(course_id):
        try:
            print(course_id)
            course = Course.get_by_id(course_id)
            course.delete_instance()
            return True, "تم حذف المادة بنجاح"
        except Course.DoesNotExist:
            return False, "المادة غير موجودة"
        except Exception as e:
            return False, f"حدث خطأ أثناء الحذف: {str(e)}"
    