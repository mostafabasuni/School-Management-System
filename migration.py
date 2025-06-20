# ملف جديد باسم migrate.py
from sch_management_db import db, StudentCourse, StudentScore

def migrate_table():
    # 1. إنشاء الجدول الجديد إذا لم يكن موجوداً
    db.create_tables([StudentScore])
    
    # 2. نقل البيانات من الجدول القديم إلى الجديد
    for old_record in StudentCourse.select():
        StudentScore.create(
            student=old_record.student,
            course=old_record.course,
            midterm_score=old_record.midterm_score,
            final_score=old_record.final_score
        )
    
    # 3. (اختياري) حذف الجدول القديم بعد التأكد من نقل البيانات
    db.drop_tables([StudentCourse])

if __name__ == '__main__':
    migrate_table()