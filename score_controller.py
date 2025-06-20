from sch_management_db import db, StudentScore, Student, Course
from peewee import *
class ScoreService:
    @staticmethod
    def save_scores(course_id, score_data, term_type, academic_year):
        """حفظ الدرجات مع تحديد نوع الترم"""
        try:
            with db.atomic():
                for student_id, score in score_data.items():
                    # البحث عن سجل موجود أو إنشاء جديد
                    score_record, created = StudentScore.get_or_create(
                        student=student_id,
                        course=course_id,
                        academic_year=academic_year,
                        defaults={term_type: score}  # القيم الافتراضية للسجل الجديد
                    )
                    
                    if not created:
                        # تحديث السجل الموجود
                        setattr(score_record, term_type, score)
                        score_record.save()
            
            return True, "تم حفظ الدرجات بنجاح"
        except Exception as e:
            return False, f"خطأ في الحفظ: {str(e)}"
    @staticmethod
    def get_students_by_grade(grade_id):
        #جلب قائمة الطلاب للصف المحدد
        return Student.select().where(Student.grade == grade_id)