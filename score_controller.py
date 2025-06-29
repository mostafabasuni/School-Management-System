from sch_management_db import db, StudentScore, Student, Grade, Course
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
    
    
    @staticmethod
    def calculate_student_totals(grade_id, academic_year):
        """
        حساب التصنيفات داخل الصف
        Returns:
            list: قائمة مصنفة تحتوي على:
                [{'student': student_obj, 'overall_average': x, 'rank': y}, ...]
        """
        print(f"Calculating totals for grade {grade_id} in academic year {academic_year}")
        # جلب الطلاب في الصف المحدد مع درجاتهم
        students = (Student
                .select()
                .where(
                (Student.grade == grade_id) &
                (Student.overall_average > 0)
                )
                .order_by(Student.overall_average.desc()))
        
        rankings = []
        for rank, student in enumerate(students, start=1):
            rankings.append({
                'student': student,
                'overall_average': student.overall_average,
                'rank': rank
            })
        
        return rankings
    
    
    @staticmethod
    def update_class_totals(grade_id, academic_year):        
        """
        تحديث نتائج جميع طلاب الصف
        المعاملات:
            grade_id (int): معرّف الصف
            academic_year (str): السنة الدراسية (مثل "2023-2024")
        
        الإرجاع:
            tuple: (success: bool, message: str)
        """
        try:
            with db.atomic():
                # جلب كائن الصف والتأكد من وجوده
                grade = Grade.get_by_id(grade_id)
                students = Student.select().where(Student.grade == grade_id)                
                updated_count = 0
                for student in students:
                    # حساب المجاميع لكل طالب
                    totals =  ScoreService.calculate_student_totals(student.id, academic_year)                    
                    if totals:
                        student.midterm_total = totals['midterm_total']
                        student.final_total = totals['final_total']
                        student.overall_average = totals['overall_total']
                        student.save()
                        updated_count += 1
                
                # تحديث حالة الصف
                grade.is_calculated = True
                grade.save()
                
                return True, f"تم تحديث {updated_count} طالبًا في الصف {grade.name}"
                
        except Grade.DoesNotExist:
            return False, "الصف غير موجود"
        except Exception as e:
            return False, f"خطأ فني: {str(e)}"
    

    
    @staticmethod
    def calculate_class_rankings(grade_id, academic_year):
        """
        حساب التصنيفات داخل الصف
        Returns:
            list: قائمة مصنفة تحتوي على:
                [{'student': student_obj, 'overall_average': x, 'rank': y}, ...]
        """
        students = (Student
                .select()
                .where(
                    (Student.grade == grade_id) &
                    (Student.overall_average > 0)
                )
                .order_by(Student.overall_average.desc()))
        
        rankings = []
        for rank, student in enumerate(students, start=1):
            rankings.append({
                'student': student,
                'overall_average': student.overall_average,
                'rank': rank
            })
        
        return rankings
    
    @staticmethod
    def calculate_school_rankings(academic_year):
        """
        حساب التصنيفات على مستوى المدرسة
        Returns:
            list: قائمة العشرة الأوائل
        """
        top_students = (Student
                    .select()
                    .where(Student.overall_average > 0)
                    .order_by(Student.overall_average.desc())
                    .limit(10))
        
        return top_students
    
    @staticmethod
    def export_class_results(grade_id, academic_year):
        """تصدير نتائج الصف لملف Excel"""
        try:
            students = (Student
                    .select()
                    .where(
                        (Student.grade == grade_id) &
                        (Student.academic_year == academic_year)
                    .order_by(Student.overall_average.desc())))
            
            # إنشاء DataFrame (إذا كنت تستخدم pandas)
            data = []
            for rank, student in enumerate(students, start=1):
                data.append([
                    rank,
                    student.student_code,
                    student.name,
                    student.midterm_total,
                    student.final_total,
                    student.overall_average,
                    ScoreService.get_grade_letter(student.overall_average)
                ])
            
            return data
        
        except Exception as e:
            print(f"Export error: {str(e)}")
            return None