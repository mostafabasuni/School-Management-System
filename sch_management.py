from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
from peewee import fn
import sys
from grade_controller import GradeService  # استيراد وحدة التحكم للصفوف 
from user_controller import UserManager  # استيراد وحدة التحكم للمستخدم
from teacher_controller import TeacherService  # استيراد خدمة المعلم
from course_controller import CourseService  # استيراد خدمة الدورات
from student_controller import StudentService  # استيراد خدمة الطلاب
from score_controller import ScoreService  # استيراد وحدة التحكم للدرجات
from sch_management_db import User, Student, Teacher, Grade, Course, StudentScore, Permissions # استيراد الجداول من Peewee
from werkzeug.security import generate_password_hash, check_password_hash


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi('school_management.ui', self)  # تحميل ملف التصميم
        
        self.tabWidget.tabBar().setVisible(False)
        self.user_manager = UserManager()
        self.teacher_manager = TeacherService()  # إنشاء مثيل من خدمة المعلم
        self.grade_manager = GradeService()  # إنشاء مثيل من مدير الصفوف
        self.course_manager = CourseService()
        self.student_manager = StudentService()  # إنشاء مثيل من خدمة الطلاب
        
        self.setup_courses_tab()
        self.setup_student_tab()  # إعدادات تبويب الطلاب        
        self.load_students()
        self.load_courses()
        
        self.radioButton.toggled.connect(self.load_scores_for_term)
        self.radioButton_2.toggled.connect(self.load_scores_for_term)
        self.comboBox_16.currentIndexChanged.connect(self.load_scores_for_term)
        
        
        
        #self.tableWidget_5.cellChanged.connect(self.calculate_totals)
        self.tableWidget.itemClicked.connect(self.user_table_select)
        self.tableWidget_2.itemClicked.connect(self.teacher_table_select)
        self.tableWidget_3.itemClicked.connect(self.course_table_select)
        self.tableWidget_4.itemClicked.connect(self.student_table_select)
        self.tableWidget_9.itemClicked.connect(self.grade_table_select)
        self.pushButton.clicked.connect(self.open_users_tab)        
        self.pushButton_2.clicked.connect(self.open_teachers_tab)
        self.pushButton_3.clicked.connect(self.open_courses_tab)
        self.pushButton_4.clicked.connect(self.open_students_tab)
        self.pushButton_5.clicked.connect(self.open_scores_tab)
        self.pushButton_8.clicked.connect(self.handle_login)
        self.pushButton_9.clicked.connect(self.clear_user_form)
        self.pushButton_10.clicked.connect(self.handle_user_creation)
        self.pushButton_11.clicked.connect(self.handle_user_update)
        self.pushButton_12.clicked.connect(self.handle_user_delete)
        self.pushButton_14.clicked.connect(self.clear_teacher_form)
        self.pushButton_15.clicked.connect(self.handle_teacher_creation)
        self.pushButton_16.clicked.connect(self.handle_teacher_update)
        self.pushButton_17.clicked.connect(self.handle_teacher_delete)
        self.pushButton_20.clicked.connect(self.clear_course_form)
        self.pushButton_21.clicked.connect(self.handle_course_creation)
        self.pushButton_22.clicked.connect(self.handle_course_update)
        self.pushButton_23.clicked.connect(self.handle_course_delete)
        self.pushButton_24.clicked.connect(self.clear_student_form)
        self.pushButton_25.clicked.connect(self.handle_student_registration)
        self.pushButton_26.clicked.connect(self.handle_student_update)
        self.pushButton_27.clicked.connect(self.handle_student_delete)
        self.pushButton_31.clicked.connect(self.save_course_scores)
        self.pushButton_50.clicked.connect(self.clear_grade_form)
        self.pushButton_51.clicked.connect(self.handle_grade_creation)
        self.pushButton_52.clicked.connect(self.handle_grade_update)
        self.pushButton_53.clicked.connect(self.handle_grade_delete)
        self.pushButton_67.clicked.connect(self.open_grades_tab)
        self.pushButton_68.clicked.connect(self.load_students_for_scores)
        self.load_users()  # تحميل المستخدمين عند بدء التشغيل
        self.load_teachers()
        self.load_grades()
    def load_users(self):     
        self.tableWidget.setRowCount(0)
        for row_index, user in enumerate(User.select()):
            self.tableWidget.insertRow(row_index)
            self.tableWidget.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(user.id)))
            self.tableWidget.setItem(row_index, 1, QtWidgets.QTableWidgetItem(user.fullname))
            self.tableWidget.setItem(row_index, 2, QtWidgets.QTableWidgetItem(str(user.job)))
            self.tableWidget.setItem(row_index, 3, QtWidgets.QTableWidgetItem(str(user.user_name)))
            self.tableWidget.setItem(row_index, 4, QtWidgets.QTableWidgetItem("نعم" if user.is_admin else "لا"))
    
    def user_table_select(self):        
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار مستخدم من الجدول")
            return

        user_id = int(self.tableWidget.item(selected_row, 0).text())
        user = User.get_by_id(user_id)
        self.lineEdit_3.setText(str(user.id))
        self.lineEdit_4.setText(user.fullname)        
        self.lineEdit_5.setText(user.job)
        self.lineEdit_6.setText(user.user_name)
        self.checkBox.setChecked(user.is_admin)        
        
    def handle_login(self):
        self.groupBox.setEnabled(True)
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_5.setEnabled(False)
        self.pushButton_6.setEnabled(False)
        self.pushButton_36.setEnabled(False)
        
        username = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()

        success, result = self.user_manager.login(username, password)

        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", f"مرحبًا {result.user_name}!")
            permissions = self.user_manager.get_permissions()
            for p in permissions:
                if p.users_tab:
                    self.pushButton.setEnabled(True)
                if p.teachers_tab:
                    self.pushButton_2.setEnabled(True)
                if p.courses_tab:
                    self.pushButton_3.setEnabled(True)
                if p.students_tab:
                    self.pushButton_4.setEnabled(True)
                if p.scores_tab:
                    self.pushButton_5.setEnabled(True)
                if p.student_score_tab:
                    self.pushButton_36.setEnabled(True)
                if p.permissions_tab:
                    self.pushButton_6.setEnabled(True)
                    
            # يمكنك هنا تفعيل التبويبات أو إظهار الصفحة التالية
            self.lineEdit.clear()
            self.lineEdit_2.clear()
        else:
            QtWidgets.QMessageBox.warning(self, "فشل", result)        
# =================== Users =========================
    def handle_user_creation(self):
        fullname = self.lineEdit_4.text().strip()
        username = self.lineEdit_6.text().strip()
        password = self.lineEdit_7.text().strip()
        job = self.lineEdit_5.text().strip()
        is_admin = self.checkBox.isChecked()

        if not fullname or not username or not password or not job:
            QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول.")
            return

        user = UserManager.create_user(fullname, username, password, job, is_admin)

        if user:
            QtWidgets.QMessageBox.information(self, "نجاح", "تم إنشاء المستخدم بنجاح.")
            self.lineEdit_3.clear()
            self.lineEdit_4.clear()
            self.lineEdit_5.clear()
            self.lineEdit_6.clear()
            self.lineEdit_7.clear()
            self.checkBox.setChecked(False)
            self.load_users()  # إعادة تحميل المستخدمين بعد الإضافة
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", "فشل في إنشاء المستخدم.")

    def open_users_tab(self):
        self.tabWidget.setCurrentIndex(1)    
        
    def handle_user_update(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار مستخدم من الجدول")
            return
        user_id = int(self.tableWidget.item(selected_row, 0).text())
        fullname = self.lineEdit_4.text().strip()
        job = self.lineEdit_5.text().strip()
        username = self.lineEdit_6.text().strip()
        is_admin = self.checkBox.isChecked()
        success, message = self.user_manager.update_user(user_id, fullname, job, username, is_admin)
        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.load_users()
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)    
        
        
    def handle_user_delete(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار مستخدم من الجدول")
            return
        user_id = int(self.tableWidget.item(selected_row, 0).text())
        reply = QtWidgets.QMessageBox.question(
        self,
        "تأكيد الحذف",
        "هل أنت متأكد من حذف هذا المستخدم؟",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    )
    
        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.user_manager.delete_user(user_id)
            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_users()
                self.clear_user_form()
            else:
                QtWidgets.QMessageBox.warning(self, "خطأ", message)
    def clear_user_form(self):
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.lineEdit_5.clear()
        self.lineEdit_6.clear()
        self.lineEdit_7.clear()
        self.checkBox.setChecked(False)
# =================== Users ends =========================
# =================== Teachers =========================
    def load_teachers(self):
        self.tableWidget_2.setRowCount(0)
        for row_index, teacher in enumerate(Teacher.select()):
            self.tableWidget_2.insertRow(row_index)
            self.tableWidget_2.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(teacher.id)))
            self.tableWidget_2.setItem(row_index, 1, QtWidgets.QTableWidgetItem(str(teacher.teacher_id)))
            self.tableWidget_2.setItem(row_index, 2, QtWidgets.QTableWidgetItem(teacher.name))
            self.tableWidget_2.setItem(row_index, 3, QtWidgets.QTableWidgetItem(teacher.specialization))
    def open_teachers_tab(self):
        self.tabWidget.setCurrentIndex(2)
    
    def teacher_table_select(self):
        selected_row = self.tableWidget_2.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار معلم من الجدول")
            return

        id_ = int(self.tableWidget_2.item(selected_row, 0).text())
        teacher = Teacher.get_by_id(id_)
        self.lineEdit_9.setText(teacher.teacher_id)
        self.lineEdit_10.setText(teacher.name)
        self.lineEdit_11.setText(teacher.specialization)
        
    def handle_teacher_creation(self):
        id_ = self.lineEdit_9.text().strip()
        teacher_name = self.lineEdit_10.text().strip()
        subject = self.lineEdit_11.text().strip()        
        if not id_ or not teacher_name or not subject:
            QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول.")
            return        
        if TeacherService.create_teacher(id_, teacher_name, subject):
            QtWidgets.QMessageBox.information(self, "نجاح", "تم إضافة المعلم بنجاح.")
            self.lineEdit_9.clear()
            self.lineEdit_10.clear()
            self.lineEdit_11.clear()
            self.load_teachers()

    def handle_teacher_update(self):
        selected_row = self.tableWidget_2.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار معلم من الجدول")
            return
        id_ = int(self.tableWidget_2.item(selected_row, 0).text())
        teacher_id = self.lineEdit_9.text().strip()
        name = self.lineEdit_10.text().strip()
        specialization = self.lineEdit_11.text().strip()
        
        success, message = self.teacher_manager.update_teacher(id_, teacher_id, name, specialization)
        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.load_teachers()
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)
    def handle_teacher_delete(self):
        selected_row = self.tableWidget_2.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار معلم من الجدول")
            return
        id_ = int(self.tableWidget_2.item(selected_row, 0).text())
        reply = QtWidgets.QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا المعلم؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
    
        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.teacher_manager.delete_teacher(id_)
            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_teachers()
                self.clear_teacher_form()
            else:
                QtWidgets.QMessageBox.warning(self, "خطأ", message)
    def clear_teacher_form(self):
        self.lineEdit_9.clear()
        self.lineEdit_10.clear()
        self.lineEdit_11.clear()
# =================== Teachers Ends =========================
# =================== Grades =========================
    def load_grades(self):
        self.tableWidget_9.setRowCount(0)
        for row_index, grade in enumerate(Grade.select()):
            self.tableWidget_9.insertRow(row_index)
            self.tableWidget_9.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(grade.id)))
            self.tableWidget_9.setItem(row_index, 1, QtWidgets.QTableWidgetItem(grade.term))
            self.tableWidget_9.setItem(row_index, 2, QtWidgets.QTableWidgetItem(grade.level))
            self.tableWidget_9.setItem(row_index, 3, QtWidgets.QTableWidgetItem(grade.name))
            self.tableWidget_9.setItem(row_index, 4, QtWidgets.QTableWidgetItem(grade.grade_id))
    
    
    
    def open_grades_tab(self):
        self.tabWidget.setCurrentIndex(4)
    
    def grade_table_select(self):
        selected_row = self.tableWidget_9.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار صف من الجدول")
            return

        grade_id = int(self.tableWidget_9.item(selected_row, 0).text())
        grade = Grade.get_by_id(grade_id)
        self.lineEdit_44.setText(grade.grade_id)
        self.lineEdit_48.setText(grade.name)
        self.lineEdit_47.setText(grade.level)
        self.lineEdit_46.setText(grade.term)
        
    def handle_grade_creation(self):
        grade_id = self.lineEdit_44.text().strip()
        grade_name = self.lineEdit_48.text().strip()
        level = self.lineEdit_47.text().strip()
        term = self.lineEdit_46.text().strip()
        
        if not grade_id or not grade_name or not level or not term:
            QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول.")
            return
        if self.grade_manager.create_grade(grade_id, grade_name, level, term):
            QtWidgets.QMessageBox.information(self, "نجاح", "تم إضافة الصف بنجاح.")
        
        self.load_grades()  # إعادة تحميل الصفوف بعد الإضافة
        self.clear_grade_form()
        
    
    def handle_grade_update(self):
        selected_row = self.tableWidget_9.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار صف من الجدول")
            return
        id_ = int(self.tableWidget_9.item(selected_row, 0).text())
        grade_id = self.lineEdit_44.text().strip()
        grade_name = self.lineEdit_48.text().strip()
        level = self.lineEdit_47.text().strip()
        term = self.lineEdit_46.text().strip()
        success, message = self.grade_manager.update_grade(id_, grade_id, grade_name, level, term)
        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.load_grades()
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)
    
    def handle_grade_delete(self):
        selected_row = self.tableWidget_9.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار صف من الجدول")
            return
        id_ = int(self.tableWidget_9.item(selected_row, 0).text())
        reply = QtWidgets.QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا الصف؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.grade_manager.delete_grade(id_)
            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_grades()
                self.clear_grade_form()
            else:
                QtWidgets.QMessageBox.warning(self, "خطأ", message)
                
    def clear_grade_form(self):
        self.lineEdit_44.clear()
        self.lineEdit_48.clear()
        self.lineEdit_47.clear()
        self.lineEdit_46.clear()
# =================== Courses =========================
    def open_courses_tab(self):
        self.tabWidget.setCurrentIndex(3)
        
    def load_courses(self):
        self.tableWidget_3.setRowCount(0)
        for row_index, course in enumerate(Course.select()):
            self.tableWidget_3.insertRow(row_index)
            self.tableWidget_3.setItem(row_index, 0, QtWidgets.QTableWidgetItem(course.course_id))
            self.tableWidget_3.setItem(row_index, 1, QtWidgets.QTableWidgetItem(course.name))
            self.tableWidget_3.setItem(row_index, 2, QtWidgets.QTableWidgetItem(course.grade.name))
            self.tableWidget_3.setItem(row_index, 3, QtWidgets.QTableWidgetItem(course.grade.level if course.grade else ""))
            self.tableWidget_3.setItem(row_index, 4, QtWidgets.QTableWidgetItem(course.grade.term if course.grade else ""))
            self.tableWidget_3.setItem(row_index, 5, QtWidgets.QTableWidgetItem(course.teacher.name if course.teacher else ""))

    def handle_course_creation(self):
        course_id = self.lineEdit_14.text().strip()
        course_name = self.lineEdit_15.text().strip()
        teacher_id = self.comboBox_7.currentData()
        grade = self.comboBox_8.currentText()   
        level = self.comboBox_9.currentText()
        term = self.comboBox_10.currentText()
        grade_id = Grade.get(Grade.name == grade, Grade.level == level, Grade.term == term).grade_id if grade and level and term else None
        

        if not all([course_id, course_name, grade_id]):
            QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول الإجبارية")
            return

        success, message = self.course_manager.create_course(
            course_id=course_id,
            name=course_name,
            grade_id=grade_id,
            teacher_id=teacher_id
        )

        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.load_courses()
            self.clear_course_form()
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)

    def clear_course_form(self):
        self.lineEdit_14.clear()
        self.lineEdit_15.clear()
        self.comboBox_7.setCurrentIndex(-1)
        self.comboBox_8.setCurrentIndex(-1)
        self.comboBox_9.setCurrentIndex(-1)
        self.comboBox_10.setCurrentIndex(-1)

    def setup_courses_tab(self):
    # تحميل المدرسين في Combobox
        self.comboBox_7.clear()
        for teacher in Teacher.select():            
            self.comboBox_7.addItem(teacher.name, teacher.teacher_id)
        
        # تحميل الصفوف في Combobox
        grades = Grade.select(fn.DISTINCT(Grade.name)).where(Grade.name.is_null(False))
        self.comboBox_8.clear()
        self.comboBox_13.clear()
        for grade in grades: #Grade.select():            
            self.comboBox_8.addItem(grade.name, grade.grade_id)
            self.comboBox_13.addItem(grade.name, grade.grade_id)
        
        levels = Grade.select(fn.DISTINCT(Grade.level)).where(Grade.level.is_null(False))
        self.comboBox_9.clear()
        self.comboBox_14.clear()
        for grade in levels:
            self.comboBox_9.addItem(grade.level)
            self.comboBox_14.addItem(grade.level)
            
        terms = Grade.select(fn.DISTINCT(Grade.term)).where(Grade.level.is_null(False))
        self.comboBox_10.clear()
        self.comboBox_15.clear()
        for grade in terms:
            self.comboBox_10.addItem(grade.term)
            self.comboBox_15.addItem(grade.term)
        
        courses = Course.select(fn.DISTINCT(Course.name)).where(Course.name.is_null(False))
        self.comboBox.clear()
        for course in courses:
            self.comboBox.addItem(course.name)


    '''def update_grade_details(self):
        grade_id = self.comboBox_8.currentData()
        print(f"Selected Grade ID: {grade_id}")        
        if grade_id:
            grade = Grade.get(Grade.grade_id == grade_id)
            self.comboBox_9.setCurrentText(grade.level)
            self.comboBox_10.setCurrentText(grade.term)
    '''
    def course_table_select(self):
        selected_row = self.tableWidget_3.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار مادة من الجدول")
            return
        
        try:
            # جلب البيانات من الجدول
            course_id = self.tableWidget_3.item(selected_row, 0).text()
            course_name = self.tableWidget_3.item(selected_row, 1).text()
            grade_name = self.tableWidget_3.item(selected_row, 2).text()
            teacher_name = self.tableWidget_3.item(selected_row, 5).text()
            
            # تعبئة الحقول في الواجهة
            self.lineEdit_14.setText(course_id)
            self.lineEdit_15.setText(course_name)
            self.comboBox_7.setCurrentText(teacher_name)
            self.comboBox_8.setCurrentText(grade_name)

            # جلب كائن المادة من قاعدة البيانات
            course = Course.get(Course.course_id == course_id)
            
            # جلب بيانات الصف المرتبط
            grade = Grade.get(Grade.id == course.grade.id)  # أو Grade.grade_id == course.grade.grade_id
            self.comboBox_9.setCurrentText(grade.level)
            self.comboBox_10.setCurrentText(grade.term)

        except DoesNotExist:
            QtWidgets.QMessageBox.critical(self, "خطأ", "المادة أو الصف غير موجود في قاعدة البيانات")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")
                
    def handle_course_update(self):
        try:
            selected_row = self.tableWidget_3.currentRow()
            if selected_row == -1:
                QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار مادة من الجدول")
                return
            
            # جلب البيانات من الواجهة
            old_course_id = self.tableWidget_3.item(selected_row, 0).text()  # ID الأصلي من الجدول
            new_course_id = self.lineEdit_14.text().strip()
            course_name = self.lineEdit_15.text().strip()
            teacher_id = self.comboBox_7.currentData()
            grade_name = self.comboBox_8.currentText()
            level = self.comboBox_9.currentText()
            term = self.comboBox_10.currentText()

            # الحصول على grade_id من الجداول المرتبطة
            grade = Grade.get(
                (Grade.name == grade_name) & 
                (Grade.level == level) & 
                (Grade.term == term))
            grade_id = grade.grade_id

            '''grade = Grade.select().where(
                (Grade.name == grade_name) &
                (Grade.level == level) &
                (Grade.term == term)).get()'''
            # التحقق من الحقول الإجبارية
            if not all([new_course_id, course_name, grade_id]):
                QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول الإجبارية")
                return

            # استدعاء دالة التحديث
            success, message = self.course_manager.update_course(
                course_id=old_course_id,  # نستخدم ID الأصلي للبحث
                name=course_name,
                grade_id=grade_id,
                teacher_id=teacher_id
            )

            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_courses()
                self.clear_course_form()
            else:
                QtWidgets.QMessageBox.critical(self, "خطأ", message)

        except DoesNotExist:
            QtWidgets.QMessageBox.critical(self, "خطأ", "الصف المحدد غير موجود")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")
        
    def handle_course_delete(self):
        selected_row = self.tableWidget_3.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار مادة من الجدول")
            return
        
        course_id = self.tableWidget_3.item(selected_row, 0).text()
        c_id = Course.get(Course.course_id == course_id).id
        
        reply = QtWidgets.QMessageBox.question(
            self, "تأكيد", "هل أنت متأكد من حذف هذه المادة؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.course_manager.delete_course(c_id)
            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_courses()
                self.clear_course_form()
            else:
                QtWidgets.QMessageBox.warning(self, "خطأ", message)
                
# =================== Courses Ends =========================

# =================== Students =========================
    def open_students_tab(self):
        self.tabWidget.setCurrentIndex(5)
    
    def clear_student_form(self):
        self.lineEdit_18.clear()
        self.lineEdit_19.clear()
        self.spinBox.setValue(0)
        self.comboBox_11.setCurrentIndex(-1)
        self.comboBox_12.setCurrentIndex(-1)
        self.dateEdit.setDate(QDate.currentDate())
        
    def handle_student_registration(self):
        try:
            student_id = self.lineEdit_18.text().strip()
            name = self.lineEdit_19.text().strip()
            age = self.spinBox.value()
            grade_name = self.comboBox_11.currentText()
            level = self.comboBox_12.currentText()
            reg_date = self.dateEdit.date().toPyDate()

            # الحصول على ID الصف بدلاً من الكائن
            grade = Grade.get_or_none(Grade.name == grade_name, Grade.level == level)            
            if not grade:
                QtWidgets.QMessageBox.warning(self, "خطأ", "الصف المحدد غير موجود")
                return

            if not all([student_id, name]):
                QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى تعبئة جميع الحقول الإجبارية")
                return

            success, message = self.student_manager.register_student(
                student_id=student_id,
                name=name,
                age=age,
                grade_id=grade.id,  # إرسال ID الصف فقط
                registration_date=reg_date
            )

            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_students()
                #self.clear_student_form()
            else:
                QtWidgets.QMessageBox.critical(self, "خطأ", message)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")
    
    def handle_student_update(self):
        selected_row = self.tableWidget_4.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار طالب من الجدول")
            return        
        student_id = self.tableWidget_4.item(selected_row, 0).text()
        name = self.lineEdit_19.text().strip()
        age = self.spinBox.value()
        grade_name = self.comboBox_11.currentText()
        level = self.comboBox_12.currentText()
        reg_date = self.dateEdit.date().toPyDate()
        # الحصول على ID الصف بدلاً من الكائن
        grade = Grade.get_or_none(Grade.name == grade_name, Grade.level == level)
        
        if not grade:
            QtWidgets.QMessageBox.warning(self, "خطأ", "الصف المحدد غير موجود")
            return

        success, message = self.student_manager.student_update(
            student_id=student_id,
            name=name,
            age=age,
            grade_id=grade.id,  # إرسال ID الصف فقط
            registration_date=reg_date
        )

        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.load_students()
            #self.clear_student_form()
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)        
    
    def handle_student_delete(self):
        selected_row = self.tableWidget_4.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار طالب من الجدول")
            return
        
        student_id = self.tableWidget_4.item(selected_row, 0).text()
        reply = QtWidgets.QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا الطالب؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
    
        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.student_manager.student_delete(student_id)
            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_students()
                #self.clear_student_form()
            else:
                QtWidgets.QMessageBox.warning(self, "خطأ", message)
    
    def student_table_select(self):
        selected_row = self.tableWidget_4.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار طالب من الجدول")
            return

        student_id = self.tableWidget_4.item(selected_row, 0).text()
        student = Student.get(Student.student_id == student_id)        
        self.lineEdit_18.setText(student.student_id)
        self.lineEdit_19.setText(student.name)
        self.spinBox.setValue(student.age)
        self.comboBox_11.setCurrentText(student.grade.name)
        self.comboBox_12.setCurrentText(student.grade.level)
        self.dateEdit.setDate(student.registration_date)
            
    def setup_student_tab(self):
                # تحميل الصفوف في Combobox
        grades = Grade.select(fn.DISTINCT(Grade.name)).where(Grade.name.is_null(False))
        self.comboBox_11.clear()
        for grade in grades: #Grade.select():            
            self.comboBox_11.addItem(grade.name, grade.grade_id)
        
        levels = Grade.select(fn.DISTINCT(Grade.level)).where(Grade.level.is_null(False))
        self.comboBox_12.clear()
        for grade in levels:
            self.comboBox_12.addItem(grade.level)
    def load_students(self):
        self.tableWidget_4.setRowCount(0)
        for row, student in enumerate(Student.select()):
        
            self.tableWidget_4.insertRow(row)
            self.tableWidget_4.setItem(row, 0, QtWidgets.QTableWidgetItem(student.student_id))
            self.tableWidget_4.setItem(row, 1, QtWidgets.QTableWidgetItem(student.name))
            self.tableWidget_4.setItem(row, 2, QtWidgets.QTableWidgetItem(str(student.age)))
            self.tableWidget_4.setItem(row, 3, QtWidgets.QTableWidgetItem(student.grade.name))
            self.tableWidget_4.setItem(row, 4, QtWidgets.QTableWidgetItem(student.grade.level))
            self.tableWidget_4.setItem(row, 5, QtWidgets.QTableWidgetItem(student.registration_date.strftime("%Y-%m-%d")))
    # =================== Students End =========================        
    # =================== scores =========================
    def open_scores_tab(self):
        self.tabWidget.setCurrentIndex(6)
    

    def load_students_for_scores(self):
        #تحميل الطلاب للصف المحدد
        grade_name = self.comboBox_13.currentText()
        level = self.comboBox_14.currentText()
        term = self.comboBox_15.currentText()
        grade_id = Grade.get(Grade.name == grade_name, Grade.level == level, Grade.term == term).id if grade_name and level and term else None        
        students = Student.select().where(Student.grade == grade_id)
        
        self.tableWidget_5.setRowCount(0)
        for row, student in enumerate(students):
            self.tableWidget_5.insertRow(row)
            self.tableWidget_5.setItem(row, 0, QtWidgets.QTableWidgetItem(student.student_id))
            self.tableWidget_5.setItem(row, 1, QtWidgets.QTableWidgetItem(student.name))
            
            # إضافة خلايا editable للدرجات
            self.tableWidget_5.setItem(row, 2, QtWidgets.QTableWidgetItem(""))
            self.tableWidget_5.setItem(row, 3, QtWidgets.QTableWidgetItem(""))
            
            # تعطيل عمود الدرجة النهائية (سيتم حسابه تلقائياً)
            total_item = QtWidgets.QTableWidgetItem("")
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
            self.tableWidget_5.setItem(row, 4, total_item)

    def save_course_scores(self):
        try:
            # جلب البيانات من الواجهة
            course = self.comboBox.currentText()
            term_type = "midterm" if self.radioButton.isChecked() else "final"  # تحديد نوع الترم
            academic_year = self.comboBox_16.currentText()  # يجب إضافة Combobox للسنة
            
            grade = self.comboBox_13.currentText()
            level = self.comboBox_14.currentText()
            
            if not all([course, term_type, academic_year, grade, level]):
                QtWidgets.QMessageBox.warning(self, "تحذير", "يجب تعبئة جميع الحقول الإجبارية")
                return

            # الحصول على الـ IDs
            grade_id = Grade.get(Grade.name == grade, Grade.level == level).id
            course_id = Course.get(Course.name == course, Course.grade == grade_id).id

            # جمع بيانات الدرجات
            score_data = {}
            for row in range(self.tableWidget_5.rowCount()):
                student_id = self.tableWidget_5.item(row, 0).text()
                student_id = Student.get(Student.student_id == student_id).id
                score = float(self.tableWidget_5.item(row, 2 if term_type == "midterm" else 3).text())
                score_data[student_id] = score

            # حفظ الدرجات
            success, message = ScoreService.save_scores(
                course_id=course_id,
                score_data=score_data,
                term_type=term_type,
                academic_year=academic_year
            )

            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_scores_for_term()  # عرض الدرجات المحفوظة
            else:
                QtWidgets.QMessageBox.critical(self, "خطأ", message)

        except DoesNotExist:
            QtWidgets.QMessageBox.critical(self, "خطأ", "بيانات الطالب أو المادة غير موجودة")
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "خطأ", "قيم درجات غير صالحة")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")
        
    
    def load_scores_for_term(self):
        #تحميل الدرجات حسب الترم المحدد
        try:
            course = self.comboBox.currentText()
            term_type = "midterm" if self.radioButton.isChecked() else "final"  # تحديد نوع الترم
            academic_year = self.comboBox_16.currentText()  # يجب إضافة Combobox للسنة            
            grade = self.comboBox_13.currentText()
            level = self.comboBox_14.currentText()
            grade_id = Grade.get(Grade.name == grade, Grade.level == level).id
            course_id = Course.get(Course.name == course, Course.grade == grade_id).id
            
            # جلب الدرجات من قاعدة البيانات
            scores = StudentScore.select().where(
                (StudentScore.course == course_id) &
                (StudentScore.academic_year == academic_year)
            )
            
            # عرض البيانات في الجدول
            self.tableWidget_5.setRowCount(0)
            for row, score in enumerate(scores):
                self.tableWidget_5.insertRow(row)
                
                # عرض بيانات الطالب
                student = score.student
                self.tableWidget_5.setItem(row, 0, QtWidgets.QTableWidgetItem(student.student_id))
                self.tableWidget_5.setItem(row, 1, QtWidgets.QTableWidgetItem(student.name))
                
                # عرض الدرجات حسب الترم المحدد
                if term_type == "midterm":
                    self.tableWidget_5.setItem(row, 2, QtWidgets.QTableWidgetItem(str(score.midterm_score or "")))
                    self.tableWidget_5.setItem(row, 3, QtWidgets.QTableWidgetItem(""))
                else:
                    self.tableWidget_5.setItem(row, 2, QtWidgets.QTableWidgetItem(str(score.midterm_score or "")))
                    self.tableWidget_5.setItem(row, 3, QtWidgets.QTableWidgetItem(str(score.final_score or "")))
                
                # حساب المجموع
                total = (score.midterm_score * 0.4 + score.final_score * 0.6) if score.midterm_score and score.final_score else None
                self.tableWidget_5.setItem(row, 4, QtWidgets.QTableWidgetItem(str(total) if total else ""))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل الدرجات: {str(e)}")
        
        
    def calculate_totals(self):
        #حساب الدرجات النهائية وعرضها
        for row in range(self.tableWidget_5.rowCount()):
            try:
                midterm = float(self.tableWidget_5.item(row, 2).text() or 0)
                final = float(self.tableWidget_5.item(row, 3).text() or 0)
                total = (midterm * 0.4) + (final * 0.6)
                self.tableWidget_5.item(row, 4).setText(f"{total:.2f}")
            except:
                self.tableWidget_5.item(row, 4).setText("0.00")
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    Window = Main()
    Window.show()
    app.exec_()
if __name__ == '__main__':
    main()
    