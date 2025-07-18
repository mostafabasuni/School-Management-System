from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from peewee import fn
from peewee import DoesNotExist
import sys

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument, QPainter
from PyQt5.QtCore import Qt, QTextStream, QFile
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPageLayout, QPageSize
from PyQt5.QtGui import QPageLayout, QPageSize


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
        self.load_users_in_combo()
        self.load_student_in_combo()
        self.apply_permissions()

        self.permission_checkboxes = [
        self.checkBox_15,  # users_tab
        self.checkBox_18,  # teachers_tab
        self.checkBox_16,  # courses_tab
        self.checkBox_25,  # students_tab
        self.checkBox_26,  # score_tab
        self.checkBox_28,  # student_score_tab
        self.checkBox_27,  # permissions_tab
        self.checkBox_21,  # grades_tab
        self.checkBox_33,  # final_results_tab
        ]
        
        self.nav_buttons = [
        self.pushButton,
        self.pushButton_2,
        self.pushButton_3,
        self.pushButton_4,
        self.pushButton_5,
        self.pushButton_6,
        self.pushButton_36,  # student_score_tab
        self.pushButton_67,  # grades_tab
        self.pushButton_72,  # final_results_tab        
        ]

        
        self.result_type = None  # None | 'midterm' | 'final' | 'top_ten'    
        
        self.radioButton.clicked.connect(self.midterm_scores)
        self.radioButton_2.clicked.connect(self.final_scores)
        self.comboBox_16.currentIndexChanged.connect(self.final_scores)
        
        # عند تغيير الصف
        self.comboBox_18.currentIndexChanged.connect(self.refresh_result_for_selected_grade)


        # عند تغيير السنة
        self.comboBox_20.currentIndexChanged.connect(self.display_final_results)

        # زر التحديث
        #self.pushButton_refresh.clicked.connect(self.display_final_results)

        # زر التصدير
        #self.pushButton_export.clicked.connect(self.export_results)
        
        '''
        self.pushButton_class_top.clicked.connect(
            lambda: self.display_top_ten(current_grade_id))
        self.pushButton_school_top.clicked.connect(
            lambda: self.display_top_ten())'''
        self.pushButton_69.clicked.connect(self.upgrade_grade_scores)
        
        #self.pushButton_display_results.clicked.connect(self.display_final_results)     
        
        #self.tableWidget_5.setColumnHidden(0, True)  # إخفاء العمود الأول (ID)    
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
        self.pushButton_6.clicked.connect(self.open_permission_tab)
        self.pushButton_7.clicked.connect(self.logout)
        self.pushButton_8.clicked.connect(self.handle_login)
        self.pushButton_9.clicked.connect(self.clear_user_form)
        self.pushButton_10.clicked.connect(self.handle_user_creation)
        self.pushButton_11.clicked.connect(self.handle_user_update)
        self.pushButton_12.clicked.connect(self.handle_user_delete)
        self.pushButton_13.clicked.connect(self.user_search)
        self.pushButton_14.clicked.connect(self.clear_teacher_form)
        self.pushButton_15.clicked.connect(self.handle_teacher_creation)
        self.pushButton_16.clicked.connect(self.handle_teacher_update)
        self.pushButton_17.clicked.connect(self.handle_teacher_delete)
        self.pushButton_18.clicked.connect(self.teacher_search)
        self.pushButton_19.clicked.connect(self.grade_course_search)
        self.pushButton_20.clicked.connect(self.clear_course_form)
        self.pushButton_21.clicked.connect(self.handle_course_creation)
        self.pushButton_22.clicked.connect(self.handle_course_update)
        self.pushButton_23.clicked.connect(self.handle_course_delete)
        self.pushButton_24.clicked.connect(self.clear_student_form)
        self.pushButton_25.clicked.connect(self.handle_student_registration)
        self.pushButton_26.clicked.connect(self.handle_student_update)
        self.pushButton_27.clicked.connect(self.handle_student_delete)
        self.pushButton_28.clicked.connect(self.student_search)
        self.pushButton_29.clicked.connect(self.save_permissions)
        self.pushButton_31.clicked.connect(self.save_course_scores)
        self.pushButton_35.clicked.connect(self.toggle_all_permissions)
        self.pushButton_36.clicked.connect(self.open_student_score_tab)
        self.pushButton_37.clicked.connect(self.student_score_search)
        self.pushButton_50.clicked.connect(self.clear_grade_form)
        self.pushButton_51.clicked.connect(self.handle_grade_creation)
        self.pushButton_52.clicked.connect(self.handle_grade_update)
        self.pushButton_53.clicked.connect(self.handle_grade_delete)
        self.pushButton_67.clicked.connect(self.open_grades_tab)
        self.pushButton_68.clicked.connect(self.print_settings)
        self.pushButton_70.clicked.connect(self.on_show_final_clicked)
        self.pushButton_71.clicked.connect(self.on_show_top_ten_clicked)
        self.pushButton_72.clicked.connect(self.final_results_tab)
        self.pushButton_73.clicked.connect(self.print_settings)
        self.pushButton_74.clicked.connect(self.on_show_midterm_clicked)
        self.pushButton_75.clicked.connect(self.section_search)
        self.pushButton_76.clicked.connect(self.print_settings)
        self.comboBox_3.currentIndexChanged.connect(self.show_permissions)
        
        self.pushButton.clicked.connect(lambda: self.highlight_active_button(self.pushButton))
        self.pushButton_2.clicked.connect(lambda: self.highlight_active_button(self.pushButton_2))
        self.pushButton_3.clicked.connect(lambda: self.highlight_active_button(self.pushButton_3))
        self.pushButton_4.clicked.connect(lambda: self.highlight_active_button(self.pushButton_4))
        self.pushButton_5.clicked.connect(lambda: self.highlight_active_button(self.pushButton_5))
        self.pushButton_6.clicked.connect(lambda: self.highlight_active_button(self.pushButton_6))
        self.pushButton_36.clicked.connect(lambda: self.highlight_active_button(self.pushButton_36))
        self.pushButton_67.clicked.connect(lambda: self.highlight_active_button(self.pushButton_67))
        self.pushButton_72.clicked.connect(lambda: self.highlight_active_button(self.pushButton_72))

        
        self.load_users()  # تحميل المستخدمين عند بدء التشغيل
        self.load_teachers()
        self.load_grades()
    
    def highlight_active_button(self, active_button):
        for btn in self.nav_buttons:
            if btn == active_button:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d7;
                        color: white;
                        font-family: 'Tajawal';
                        font-size: 11pt;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: none;
                        color: black;
                        font-family: 'Tajawal';
                        font-size: 11pt;
                        font-weight: bold;
                    }
                """)

    
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
        self.pushButton_67.setEnabled(False)
        self.pushButton_72.setEnabled(False)
        
        username = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()
        if not all([username, password]):        
            QtWidgets.QMessageBox.warning(self, "بيانات ناقصة", "يرجى ملء جميع الحقول.")
            return 

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
                if p.grades_tab:
                    self.pushButton_67.setEnabled(True)
                if p.students_tab:
                    self.pushButton_4.setEnabled(True)
                if p.score_tab:
                    self.pushButton_5.setEnabled(True)
                if p.student_score_tab:
                    self.pushButton_36.setEnabled(True)
                if p.final_results_tab:
                    self.pushButton_72.setEnabled(True)
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
        if not all([fullname, username, password, job]):        
            QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول.")
            return        

        success, message = UserManager.create_user(fullname, username, password, job, is_admin)

        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.lineEdit_3.clear()
            self.lineEdit_4.clear()
            self.lineEdit_5.clear()
            self.lineEdit_6.clear()
            self.lineEdit_7.clear()
            self.checkBox.setChecked(False)
            self.load_users()  # إعادة تحميل المستخدمين بعد الإضافة
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)

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
                
    def user_search(self):
        try:
            # جلب بيانات البحث
            user_name = self.lineEdit_8.text().strip()            
            # التحقق من المدخلات
            if not (user_name):
                QtWidgets.QMessageBox.warning(self, "تحذير", " يرجى إدخال اسم الموظف ")
                return
            # البحث باستخدام OR للسماح بالبحث بكلا الحقلين معاً
            query = User.select()
            if user_name :
                query = query.where((User.fullname.contains(user_name)))            
            user = query.first()           
            if not user:
                QtWidgets.QMessageBox.information(self, "تنبيه", "لا يوجد موظف بهذه البيانات")
                return
            item = self.tableWidget.findItems(str(user.id), Qt.MatchContains)            
            self.tableWidget.setCurrentItem(item[0])
        except DoesNotExist:
            QtWidgets.QMessageBox.warning(self, "خطأ", "الموظف غير موجود")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")

    
    def clear_user_form(self):
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.lineEdit_5.clear()
        self.lineEdit_6.clear()
        self.lineEdit_7.clear()
        self.checkBox.setChecked(False)
    
    def load_users_in_combo(self):
        self.comboBox_3.clear()
        self.comboBox_3.addItem("اختر مستخدم")
        users = User.select()
        for user in users:
            self.comboBox_3.addItem(user.fullname)
            
        
# =================== Users ends =========================
# =================== Teachers =========================
    def load_teachers(self):
        self.tableWidget_2.setRowCount(0)
        for row_index, teacher in enumerate(Teacher.select()):
            self.tableWidget_2.insertRow(row_index)
            self.tableWidget_2.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(teacher.id)))
            self.tableWidget_2.setItem(row_index, 1, QtWidgets.QTableWidgetItem(str(teacher.teacher_code)))
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
        self.lineEdit_9.setText(teacher.teacher_code)
        self.lineEdit_10.setText(teacher.name)
        self.lineEdit_11.setText(teacher.specialization)
    
    def teacher_search(self):
        try:
            # جلب بيانات البحث
            teacher_name = self.lineEdit_12.text().strip()            
            # التحقق من المدخلات
            if not (teacher_name):
                QtWidgets.QMessageBox.warning(self, "تحذير", " يرجى إدخال اسم الموظف ")
                return
            # البحث باستخدام OR للسماح بالبحث بكلا الحقلين معاً
            query = Teacher.select()
            if teacher_name :
                query = query.where((Teacher.name.contains(teacher_name)))            
            teacher = query.first()            
            if not teacher:
                QtWidgets.QMessageBox.information(self, "تنبيه", "لا يوجد مدرس بهذه البيانات")
                return
            item = self.tableWidget_2.findItems(str(teacher.id), Qt.MatchContains)            
            self.tableWidget_2.setCurrentItem(item[0])
        except DoesNotExist:
            QtWidgets.QMessageBox.warning(self, "خطأ", "المدرس غير موجود")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")

        
    def handle_teacher_creation(self):
        t_code = self.lineEdit_9.text().strip()
        teacher_name = self.lineEdit_10.text().strip()
        subject = self.lineEdit_11.text().strip()        
        if not all([t_code, teacher_name, subject]):        
            QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول.")
            return        
        success, message = TeacherService.create_teacher(t_code, teacher_name, subject)
        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.lineEdit_9.clear()
            self.lineEdit_10.clear()
            self.lineEdit_11.clear()
            self.load_teachers()
            self.setup_courses_tab()  # إعادة تحميل الدورات بعد إضافة معلم جديد
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)


    def handle_teacher_update(self):
        selected_row = self.tableWidget_2.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار معلم من الجدول")
            return
        id_ = int(self.tableWidget_2.item(selected_row, 0).text())
        teacher_code = self.lineEdit_9.text().strip()
        name = self.lineEdit_10.text().strip()
        specialization = self.lineEdit_11.text().strip()
        
        success, message = self.teacher_manager.update_teacher(id_, teacher_code, name, specialization)
        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.comboBox_7.clear()
            for teacher in Teacher.select():            
                self.comboBox_7.addItem(teacher.name, teacher.teacher_code)
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
            self.tableWidget_9.setItem(row_index, 1, QtWidgets.QTableWidgetItem(grade.grade_code))
            self.tableWidget_9.setItem(row_index, 2, QtWidgets.QTableWidgetItem(grade.academic_year))
            self.tableWidget_9.setItem(row_index, 3, QtWidgets.QTableWidgetItem(grade.term))
            self.tableWidget_9.setItem(row_index, 4, QtWidgets.QTableWidgetItem(grade.level))
            self.tableWidget_9.setItem(row_index, 5, QtWidgets.QTableWidgetItem(grade.name))    
            self.tableWidget_9.setItem(row_index, 6, QtWidgets.QTableWidgetItem(str(grade.section)))    
            
    
    def open_grades_tab(self):
        self.tabWidget.setCurrentIndex(4)
    
    def grade_table_select(self):
        selected_row = self.tableWidget_9.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار صف من الجدول")
            return

        grade_id = int(self.tableWidget_9.item(selected_row, 0).text())
        grade = Grade.get_by_id(grade_id)
        self.lineEdit_44.setText(grade.grade_code)
        self.spinBox_2.setValue(grade.section)  # تعيين قيمة القسم من SpinBox
        self.lineEdit_48.setText(grade.name)
        self.lineEdit_47.setText(grade.level)
        self.lineEdit_46.setText(grade.term)
        self.lineEdit_61.setText(grade.academic_year)  # إضافة حقل السنة الأكاديمية
        
    def handle_grade_creation(self):
        grade_code = self.lineEdit_44.text().strip()
        grade_name = self.lineEdit_48.text().strip()
        section = self.spinBox_2.value()  # الحصول على قيمة القسم من SpinBox
        level = self.lineEdit_47.text().strip()
        term = self.lineEdit_46.text().strip()
        year = self.lineEdit_61.text().strip()
        
        if not all([grade_code, grade_name, section, level, term, year]):
            QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول.")
            return
        success, message = self.grade_manager.create_grade(grade_code, grade_name, section, level, term, year)
        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)        
        self.load_grades()  # إعادة تحميل الصفوف بعد الإضافة
        self.clear_grade_form()
        
    
    def handle_grade_update(self):
        selected_row = self.tableWidget_9.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار صف من الجدول")
            return
        grade_id = int(self.tableWidget_9.item(selected_row, 0).text())
        grade_code = self.lineEdit_44.text().strip()
        section = self.spinBox_2.value()  # الحصول على قيمة القسم من SpinBox
        grade_name = self.lineEdit_48.text().strip()
        level = self.lineEdit_47.text().strip()
        term = self.lineEdit_46.text().strip()
        year = self.lineEdit_61.text().strip()
        success, message = self.grade_manager.update_grade(grade_id, grade_code, section, grade_name, level, term, year)
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
        grade_id = int(self.tableWidget_9.item(selected_row, 0).text())
        reply = QtWidgets.QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذا الصف؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.grade_manager.delete_grade(grade_id)
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
        self.lineEdit_61.clear()
        self.spinBox_2.setValue(1)  # إعادة تعيين SpinBox إلى القيمة الافتراضية 1
# =================== Courses =========================
    def open_courses_tab(self):
        self.tabWidget.setCurrentIndex(3)
        
    def load_courses(self):
        self.tableWidget_3.setRowCount(0)
        for row_index, course in enumerate(Course.select()):
            self.tableWidget_3.insertRow(row_index)
            self.tableWidget_3.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(course.id)))
            self.tableWidget_3.setItem(row_index, 1, QtWidgets.QTableWidgetItem(course.course_code))
            self.tableWidget_3.setItem(row_index, 2, QtWidgets.QTableWidgetItem(course.name))
            self.tableWidget_3.setItem(row_index, 3, QtWidgets.QTableWidgetItem(course.grade.term if course.grade else ""))
            self.tableWidget_3.setItem(row_index, 4, QtWidgets.QTableWidgetItem(course.grade.level if course.grade else ""))
            self.tableWidget_3.setItem(row_index, 5, QtWidgets.QTableWidgetItem(course.grade.name))
            self.tableWidget_3.setItem(row_index, 6, QtWidgets.QTableWidgetItem(str(course.grade.section if course.grade else "")))            
            self.tableWidget_3.setItem(row_index, 7, QtWidgets.QTableWidgetItem(course.teacher.name if course.teacher else ""))

    def handle_course_creation(self):
        course_code = self.lineEdit_14.text().strip()
        course_name = self.lineEdit_15.text().strip()
        teacher_code = self.comboBox_7.currentData()        
        grade = self.comboBox_8.currentText()   
        level = self.comboBox_9.currentText()
        term = self.comboBox_10.currentText()
        section = self.spinBox_7.value()  # الحصول على قيمة القسم من SpinBox
        grade_id = Grade.get(Grade.name == grade, Grade.section == section, Grade.level == level, Grade.term == term).id if grade and level and term else None
        teacher_id = Teacher.get(Teacher.teacher_code == teacher_code).id if teacher_code else None        

        if not all([course_code, course_name, grade_id]):
            QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول الإجبارية")
            return

        success, message = self.course_manager.create_course(
            course_code=course_code,
            name=course_name,
            grade_id=grade_id,
            teacher_id=teacher_id
        )

        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.load_courses()
            self.clear_course_form()
            self.setup_courses_tab()  # إعادة تحميل الدورات بعد إضافة مادة جديدة
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)

    def clear_course_form(self):
        self.lineEdit_14.clear()
        self.lineEdit_15.clear()
        self.comboBox_7.setCurrentIndex(-1)
        self.comboBox_8.setCurrentIndex(-1)
        self.comboBox_9.setCurrentIndex(-1)
        self.comboBox_10.setCurrentIndex(-1)
        self.comboBox_17.setCurrentIndex(-1)
        self.comboBox_22.setCurrentIndex(-1)
        self.comboBox_23.setCurrentIndex(-1)
        self.spinBox_7.setValue(1)  # إعادة تعيين SpinBox إلى القيمة الافتراضية 1
        self.spinBox_8.setValue(1)

    def setup_courses_tab(self):
    # تحميل المدرسين في Combobox
        self.comboBox_16.clear()
        self.comboBox_20.clear()
        academic_years = Grade.select(fn.DISTINCT(Grade.academic_year)).where(Grade.academic_year.is_null(False))
        for year in academic_years:
            self.comboBox_16.addItem(year.academic_year)
            self.comboBox_20.addItem(year.academic_year)
        
        self.comboBox_7.clear()
        for teacher in Teacher.select():            
            self.comboBox_7.addItem(teacher.name, teacher.teacher_code)
        
        # تحميل الصفوف في Combobox
        grades = Grade.select(fn.DISTINCT(Grade.name)).where(Grade.name.is_null(False))
        self.comboBox_8.clear()
        self.comboBox_13.clear()
        self.comboBox_18.clear()
        for grade in grades: #Grade.select():            
            self.comboBox_8.addItem(grade.name, grade.grade_code)
            self.comboBox_13.addItem(grade.name, grade.grade_code)
            self.comboBox_22.addItem(grade.name, grade.grade_code)
            self.comboBox_18.addItem(grade.name, grade.grade_code)
        
        levels = Grade.select(fn.DISTINCT(Grade.level)).where(Grade.level.is_null(False))
        self.comboBox_9.clear()
        self.comboBox_14.clear()
        self.comboBox_21.clear()
        for grade in levels:
            self.comboBox_9.addItem(grade.level)
            self.comboBox_14.addItem(grade.level)
            self.comboBox_17.addItem(grade.level)
            self.comboBox_21.addItem(grade.level)
            
        terms = Grade.select(fn.DISTINCT(Grade.term)).where(Grade.level.is_null(False))
        self.comboBox_10.clear()
        self.comboBox_15.clear()
        self.comboBox_19.clear()
        for grade in terms:
            self.comboBox_10.addItem(grade.term)
            self.comboBox_15.addItem(grade.term)
            self.comboBox_19.addItem(grade.term)
            self.comboBox_23.addItem(grade.term)
        
        courses = Course.select(fn.DISTINCT(Course.name)).where(Course.name.is_null(False))
        self.comboBox.clear()
        for course in courses:
            self.comboBox.addItem(course.name)

    def course_table_select(self):
        selected_row = self.tableWidget_3.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار مادة من الجدول")
            return
        
        try:
            # جلب البيانات من الجدول
            course_id = int(self.tableWidget_3.item(selected_row, 0).text())
            course_code = self.tableWidget_3.item(selected_row, 1).text()
            course_name = self.tableWidget_3.item(selected_row, 2).text()
            grade_name = self.tableWidget_3.item(selected_row, 5).text()
            grade_scetion = self.tableWidget_3.item(selected_row, 6).text()
            teacher_name = self.tableWidget_3.item(selected_row, 7).text()
            
            # تعبئة الحقول في الواجهة
            self.lineEdit_14.setText(course_code)
            self.lineEdit_15.setText(course_name)
            self.comboBox_7.setCurrentText(teacher_name)
            self.comboBox_8.setCurrentText(grade_name)
            self.spinBox_7.setValue(int(grade_scetion) if grade_scetion.isdigit() else 1)  # تعيين قيمة القسم

            # جلب كائن المادة من قاعدة البيانات
            course = Course.get(Course.id == course_id)
            
            # جلب بيانات الصف المرتبط
            grade = Grade.get(Grade.id == course.grade.id)  # أو Grade.grade_code == course.grade.grade_id
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
                QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار معلم من الجدول")
                return
            course_id = int(self.tableWidget_3.item(selected_row, 0).text())            
            
            # جلب البيانات من الواجهة
            course_code = self.lineEdit_14.text().strip()
            course_name = self.lineEdit_15.text().strip()
            teacher_code = self.comboBox_7.currentData()
            grade_name = self.comboBox_8.currentText()
            level = self.comboBox_9.currentText()
            term = self.comboBox_10.currentText()
            # التحقق من الحقول الإجبارية
            if not all([course_code, course_name]):
                QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول الإجبارية")
                return
            # الحصول على grade_code من الجداول المرتبطة
            grade = Grade.get(
                (Grade.name == grade_name) & 
                (Grade.level == level) & 
                (Grade.term == term))
            
            teacher = Teacher.get(Teacher.teacher_code == teacher_code) if teacher_code else None
            # استدعاء دالة التحديث
            success, message = self.course_manager.update_course(
                course_id=course_id, 
                course_code=course_code,  
                name=course_name,
                grade_id=grade.id,
                teacher_id=teacher.id
            )

            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_courses()
                self.clear_course_form()
            else:
                QtWidgets.QMessageBox.critical(self, "خطأ", message)

        except DoesNotExist:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")
        
    def handle_course_delete(self):
        selected_row = self.tableWidget_3.currentRow()
        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار مادة من الجدول")
            return
        
        course_id = int(self.tableWidget_3.item(selected_row, 0).text())        
        reply = QtWidgets.QMessageBox.question(
            self, "تأكيد", "هل أنت متأكد من حذف هذه المادة؟",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.course_manager.delete_course(course_id)
            if success:
                QtWidgets.QMessageBox.information(self, "نجاح", message)
                self.load_courses()
                self.clear_course_form()
            else:
                QtWidgets.QMessageBox.warning(self, "خطأ", message)
    
    
    def grade_course_search(self):
    # This Python code snippet is retrieving data from a database based on the selected values from
    # combo boxes and a spin box in a GUI application. Here is a breakdown of what the code is doing:
        term = self.comboBox_23.currentText()
        level = self.comboBox_17.currentText()
        grade_name = self.comboBox_22.currentText()       

        grades = Grade.select().where(
            (Grade.name == grade_name) &
            (Grade.level == level) &
            (Grade.term == term)
        ).order_by(Grade.section.asc())

        if not grades.exists():
            QtWidgets.QMessageBox.warning(self, "تنبيه", "الصف المحدد غير موجود")
            return

        self.tableWidget_3.setRowCount(0)
        row_index = 0  # عداد صفوف الجدول

        for grade in grades:
            courses = Course.select().where(Course.grade == grade)
            for course in courses:
                self.tableWidget_3.insertRow(row_index)
                self.tableWidget_3.setItem(row_index, 0, QtWidgets.QTableWidgetItem(str(course.id)))
                self.tableWidget_3.setItem(row_index, 1, QtWidgets.QTableWidgetItem(course.course_code))
                self.tableWidget_3.setItem(row_index, 2, QtWidgets.QTableWidgetItem(course.name))
                self.tableWidget_3.setItem(row_index, 3, QtWidgets.QTableWidgetItem(course.grade.term))
                self.tableWidget_3.setItem(row_index, 4, QtWidgets.QTableWidgetItem(course.grade.level))
                self.tableWidget_3.setItem(row_index, 5, QtWidgets.QTableWidgetItem(course.grade.name))
                self.tableWidget_3.setItem(row_index, 6, QtWidgets.QTableWidgetItem(str(course.grade.section)))
                self.tableWidget_3.setItem(row_index, 7, QtWidgets.QTableWidgetItem(course.teacher.name if course.teacher else ""))
                row_index += 1

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
            student_code = self.lineEdit_18.text().strip()
            name = self.lineEdit_19.text().strip()
            age = self.spinBox.value()
            section = self.spinBox_3.value()
            grade_name = self.comboBox_11.currentText()
            level = self.comboBox_12.currentText()
            reg_date = self.dateEdit.date().toPyDate()

            # الحصول على ID الصف بدلاً من الكائن
            grade = Grade.get_or_none(Grade.name == grade_name, Grade.level == level, Grade.section == section)
            if not grade:
                QtWidgets.QMessageBox.warning(self, "خطأ", "الصف المحدد غير موجود")
                return

            if not all([student_code, name]):
                QtWidgets.QMessageBox.warning(self, "خطأ", "يرجى تعبئة جميع الحقول الإجبارية")
                return

            success, message = self.student_manager.register_student(
                student_code=student_code,
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
        student_code = self.lineEdit_18.text().strip()
        name = self.lineEdit_19.text().strip()
        age = self.spinBox.value()
        section = self.spinBox_3.value()
        grade_name = self.comboBox_11.currentText()
        level = self.comboBox_12.currentText()
        reg_date = self.dateEdit.date().toPyDate()
        # الحصول على ID الصف بدلاً من الكائن
        grade = Grade.get_or_none(Grade.name == grade_name, Grade.level == level, Grade.section == section)
        
        if not grade:
            QtWidgets.QMessageBox.warning(self, "خطأ", "الصف المحدد غير موجود")
            return

        success, message = self.student_manager.student_update(
            student_id=student_id,
            student_code=student_code,
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
        student = Student.get(Student.id == student_id)        
        self.lineEdit_18.setText(student.student_code)
        self.lineEdit_19.setText(student.name)
        self.spinBox.setValue(student.age)
        self.spinBox_3.setValue(student.grade.section)  # تعيين القسم من SpinBox
        self.comboBox_11.setCurrentText(student.grade.name)
        self.comboBox_12.setCurrentText(student.grade.level)
        self.dateEdit.setDate(student.registration_date)
    
    def student_search(self):
        try:
            # جلب بيانات البحث
            student_name = self.lineEdit_20.text().strip()
            student_code = self.lineEdit_21.text().strip()            
            # التحقق من المدخلات
            if not (student_name or student_code):
                QtWidgets.QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم الطالب أو رقمه")
                return
            # البحث باستخدام OR للسماح بالبحث بكلا الحقلين معاً
            query = Student.select()
            if student_name and student_code:
                query = query.where(
                    (Student.name.contains(student_name)) &
                    (Student.student_code == student_code)
                )
            elif student_name:
                query = query.where(Student.name.contains(student_name))
            else:
                query = query.where(Student.student_code == student_code)
            student = query.first()
            if not student:
                QtWidgets.QMessageBox.information(self, "تنبيه", "لا يوجد طالب بهذه البيانات")
                return
            item = self.tableWidget_4.findItems(str(student.id), Qt.MatchContains)            
            self.tableWidget_4.setCurrentItem(item[0])
        except DoesNotExist:
            QtWidgets.QMessageBox.warning(self, "خطأ", "الطالب غير موجود")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")

    def section_search(self):
        section = self.spinBox_3.value()
        grade_name = self.comboBox_11.currentText()
        level = self.comboBox_12.currentText()
        
        if not (grade_name and level):
            QtWidgets.QMessageBox.warning(self, "تحذير", "يرجى اختيار الصف والمرحلة")
            return
        grade = Grade.get_or_none(Grade.name == grade_name, Grade.level == level, Grade.section == section)
        
        students = Student.select().where(
            (Student.grade_id == grade.id) if grade else (Student.grade_id.is_null(True)))
        
        if not students.exists():
            QtWidgets.QMessageBox.information(self, "تنبيه", "لا يوجد طلاب في هذا الصف")
            return
        
        self.tableWidget_4.setRowCount(0)
        for row, student in enumerate(students):
            self.tableWidget_4.insertRow(row)
            self.tableWidget_4.setItem(row, 0, QtWidgets.QTableWidgetItem(str(student.id)))
            self.tableWidget_4.setItem(row, 1, QtWidgets.QTableWidgetItem(student.student_code))
            self.tableWidget_4.setItem(row, 2, QtWidgets.QTableWidgetItem(student.name))
            self.tableWidget_4.setItem(row, 3, QtWidgets.QTableWidgetItem(str(student.age)))
            self.tableWidget_4.setItem(row, 4, QtWidgets.QTableWidgetItem(student.grade.name))
            self.tableWidget_4.setItem(row, 5, QtWidgets.QTableWidgetItem(str(student.grade.section)))
            self.tableWidget_4.setItem(row, 6, QtWidgets.QTableWidgetItem(student.grade.level))
            self.tableWidget_4.setItem(row, 7, QtWidgets.QTableWidgetItem(student.registration_date.strftime("%Y-%m-%d")))
    
            
    def setup_student_tab(self):
                # تحميل الصفوف في Combobox
        grades = Grade.select(fn.DISTINCT(Grade.name)).where(Grade.name.is_null(False))
        self.comboBox_11.clear()
        for grade in grades: #Grade.select():            
            self.comboBox_11.addItem(grade.name, grade.grade_code)
        
        levels = Grade.select(fn.DISTINCT(Grade.level)).where(Grade.level.is_null(False))
        self.comboBox_12.clear()
        for grade in levels:
            self.comboBox_12.addItem(grade.level)
    def load_students(self):
        self.tableWidget_4.setRowCount(0)
        for row, student in enumerate(Student.select()):
        
            self.tableWidget_4.insertRow(row)
            self.tableWidget_4.setItem(row, 0, QtWidgets.QTableWidgetItem(str(student.id)))
            self.tableWidget_4.setItem(row, 1, QtWidgets.QTableWidgetItem(student.student_code))
            self.tableWidget_4.setItem(row, 2, QtWidgets.QTableWidgetItem(student.name))
            self.tableWidget_4.setItem(row, 3, QtWidgets.QTableWidgetItem(str(student.age)))
            self.tableWidget_4.setItem(row, 4, QtWidgets.QTableWidgetItem(student.grade.name))
            self.tableWidget_4.setItem(row, 5, QtWidgets.QTableWidgetItem(str(student.grade.section)))
            self.tableWidget_4.setItem(row, 6, QtWidgets.QTableWidgetItem(student.grade.level))
            self.tableWidget_4.setItem(row, 7, QtWidgets.QTableWidgetItem(student.registration_date.strftime("%Y-%m-%d")))
    # =================== Students End =========================        
    # =================== scores =========================
    def open_scores_tab(self):
        self.tabWidget.setCurrentIndex(6)
    

    def load_students_for_scores(self):
        #تحميل الطلاب للصف المحدد
        section = self.spinBox_3.value()
        grade_name = self.comboBox_13.currentText()
        level = self.comboBox_14.currentText()
        term = self.comboBox_15.currentText()
        grade_id = Grade.get(Grade.name == grade_name, Grade.section == section, Grade.level == level, Grade.term == term).id if grade_name and section and level and term else None        
        students = Student.select().where(Student.grade == grade_id)
        
        self.tableWidget_5.setRowCount(0)
        for row, student in enumerate(students):
            
            self.tableWidget_5.insertRow(row)
            self.tableWidget_5.setItem(row, 0, QtWidgets.QTableWidgetItem(student.student_code))
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
            term_type = "midterm_score" if self.radioButton.isChecked() else "final_score"  # تحديد نوع الترم
            academic_year = self.comboBox_16.currentText()  # يجب إضافة Combobox للسنة
            
            grade = self.comboBox_13.currentText()
            level = self.comboBox_14.currentText()
            section = self.spinBox_4.value()
            
            if not all([course, term_type, academic_year, grade, level, section]):
                QtWidgets.QMessageBox.warning(self, "تحذير", "يجب تعبئة جميع الحقول الإجبارية")
                return
            # الحصول على الـ IDs
            grade_id = Grade.get(Grade.name == grade, Grade.level == level, Grade.section == section).id
            course_id = Course.get(Course.name == course, Course.grade == grade_id).id

            # جمع بيانات الدرجات
            score_data = {}
            for row in range(self.tableWidget_5.rowCount()):
                student_id = self.tableWidget_5.item(row, 0).text()
                score = float(self.tableWidget_5.item(row, 2 if term_type == "midterm_score" else 3).text())            
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
                self.final_scores()  # عرض الدرجات المحفوظة
            else:
                QtWidgets.QMessageBox.critical(self, "خطأ", message)

        except DoesNotExist:
            QtWidgets.QMessageBox.critical(self, "خطأ", "بيانات الطالب أو المادة غير موجودة")
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "خطأ", "قيم درجات غير صالحة")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")
        
    
    def final_scores(self):
        try:
            self.tableWidget_5.setRowCount(0)
            course_name = self.comboBox.currentText()
            academic_year = self.comboBox_16.currentText()
            grade_name = self.comboBox_13.currentText()
            level = self.comboBox_14.currentText()
            section = self.spinBox_4.value()

            if not (course_name and academic_year and grade_name and section and level):
                QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار كل الحقول المطلوبة")
                return

            # جلب الصف والمادة
            grade = Grade.get(Grade.name == grade_name, Grade.section == section, Grade.level == level)            
            course = Course.get(Course.name == course_name, Course.grade_id == grade.id)            
            self.lineEdit_23.setText(course.course_code)
            # جلب كل الطلاب في الصف
            students = Student.select().where(Student.grade_id == grade.id)
            for row, student in enumerate(students):
                self.tableWidget_5.insertRow(row)
                self.tableWidget_5.setItem(row, 0, QtWidgets.QTableWidgetItem(str(student.id)))
                self.tableWidget_5.setItem(row, 1, QtWidgets.QTableWidgetItem(student.name))

                # محاولة جلب الدرجات إن وُجدت
                try:
                    score = StudentScore.get(
                        (StudentScore.student_id == student.id) &
                        (StudentScore.course_id == course.id) &
                        (StudentScore.academic_year == academic_year)
                    )
                    mid = score.midterm_score
                    final = score.final_score
                except StudentScore.DoesNotExist:
                    mid = final = None
                # إدراج الدرجات في الجدول
                self.tableWidget_5.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mid if mid is not None else "")))
                self.tableWidget_5.setItem(row, 3, QtWidgets.QTableWidgetItem(str(final if final is not None else "")))

                # المجموع النهائي
                if mid is not None and final is not None:
                    total = round((mid + final) / 2, 2)
                    total_item = QtWidgets.QTableWidgetItem(str(total))
                    total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
                    self.tableWidget_5.setItem(row, 4, total_item)
                else:
                    self.tableWidget_5.setItem(row, 4, QtWidgets.QTableWidgetItem(""))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل الدرجات:\n{str(e)}")

    def midterm_scores(self):
        try:            
            self.tableWidget_5.setRowCount(0)
            course_name = self.comboBox.currentText()
            academic_year = self.comboBox_16.currentText()
            grade_name = self.comboBox_13.currentText()
            level = self.comboBox_14.currentText()
            section = self.spinBox_4.value()

            if not (course_name and academic_year and grade_name and section and level):
                QtWidgets.QMessageBox.warning(self, "تنبيه", "يرجى اختيار كل الحقول المطلوبة")
                return

            # جلب الصف والمادة
            grade = Grade.get(Grade.name == grade_name, Grade.section == section, Grade.level == level)                        
            course = Course.get(Course.name == course_name, Course.grade == grade.id)            
            self.lineEdit_23.setText(course.course_code)            
            # جلب كل الطلاب في الصف
            students = Student.select().where(Student.grade_id == grade.id)
            for row, student in enumerate(students):
                self.tableWidget_5.insertRow(row)
                self.tableWidget_5.setItem(row, 0, QtWidgets.QTableWidgetItem(str(student.id)))                
                self.tableWidget_5.setItem(row, 1, QtWidgets.QTableWidgetItem(student.name))
                # محاولة جلب الدرجات إن وُجدت
                try:
                    score = StudentScore.get(
                        (StudentScore.student_id == student.id) &
                        (StudentScore.course_id == course.id) &
                        (StudentScore.academic_year == academic_year)
                    )
                    if score is None:
                        print("No score found for student:", student.name)
                        mid = None
                    else:
                        mid = score.midterm_score                    
                except StudentScore.DoesNotExist:
                    mid = None

                # إدراج الدرجات في الجدول
                self.tableWidget_5.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mid if mid is not None else "")))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل الدرجات:\n{str(e)}")            
    
    def calculate_totals(self):
        #حساب الدرجات النهائية وعرضها
        for row in range(self.tableWidget_5.rowCount()):
            try:
                midterm = float(self.tableWidget_5.item(row, 2).text() or 0)
                final = float(self.tableWidget_5.item(row, 3).text() or 0)
                total = (midterm * 0.5) + (final * 0.5)
                self.tableWidget_5.item(row, 4).setText(f"{total:.2f}")
            except:
                self.tableWidget_5.item(row, 4).setText("0.00")
    
    def open_student_score_tab(self):
        self.tabWidget.setCurrentIndex(7)
    
    def load_student_in_combo(self):
        self.comboBox_2.clear()
        for student in Student.select():
            self.comboBox_2.addItem(student.name)
    
    def student_score_search(self):
        try:
            # جلب بيانات البحث
            student_name = self.lineEdit_29.text().strip()
            student_code = self.lineEdit_30.text().strip()            
            # التحقق من المدخلات
            if not (student_name or student_code):
                QtWidgets.QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم الطالب أو رقمه")
                return
            # البحث باستخدام OR للسماح بالبحث بكلا الحقلين معاً
            query = Student.select()
            if student_name and student_code:
                query = query.where(
                    (Student.name.contains(student_name)) &
                    (Student.student_code == student_code)
                )
            elif student_name:
                query = query.where(Student.name.contains(student_name))
            else:
                query = query.where(Student.student_code == student_code)
            student = query.first()
            if not student:
                QtWidgets.QMessageBox.information(self, "تنبيه", "لا يوجد طالب بهذه البيانات")
                return
            # عرض بيانات الطالب
            self.display_student_info(student)            
            # عرض الدرجات
            self.display_student_scores(student)
        except DoesNotExist:
            QtWidgets.QMessageBox.warning(self, "خطأ", "الطالب غير موجود")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ غير متوقع: {str(e)}")

    def display_student_info(self, student):
        """عرض معلومات الطالب في الحقول المخصصة"""
        self.lineEdit_24.setText(student.student_code)
        self.comboBox_2.setCurrentText(student.name)
        
        grade = student.grade  # الاستفادة من العلاقة المباشرة
        self.lineEdit_28.setText(grade.name)
        self.lineEdit_43.setText(grade.level)
    
    def on_show_midterm_clicked(self):
        self.result_type = 'midterm'
        self.display_midterm_results()

    def on_show_final_clicked(self):
        self.result_type = 'final'
        self.display_final_results()

    def on_show_top_ten_clicked(self):
        self.result_type = 'top_ten'
        self.display_top_ten()

    def refresh_result_for_selected_grade(self):
        if self.result_type == 'midterm':
            self.display_midterm_results()
        elif self.result_type == 'final':
            self.display_final_results()
        elif self.result_type == 'top_ten':
            self.display_top_ten()

    def display_midterm_results(self):
        try:
            academic_year = self.comboBox_20.currentText()
            term = self.comboBox_19.currentText()
            level = self.comboBox_21.currentText()
            grade_name = self.comboBox_18.currentText()
            if not (academic_year and term and level and grade_name):
                QtWidgets.QMessageBox.warning(self, "تحذير", "يرجى اختيار جميع الحقول المطلوبة")
                return
            grade_id = Grade.get(
                (Grade.name == grade_name) & 
                (Grade.level == level) & 
                (Grade.term == term) &
                (Grade.academic_year == academic_year)
            ).id                    
            # جلب الطلاب مصنفين مع معلومات الصف
            students = (Student
                    .select(Student, Grade)
                    .join(Grade)
                    .where(
                        (Student.grade == grade_id) &
                        (Student.midterm_total > 0)
                    )
                    .order_by(Student.midterm_total.desc()))
            
            # إعداد الجدول
            self.tableWidget_13.setRowCount(0)
            self.tableWidget_13.setColumnCount(7)  # عدد الأعمدة
            headers = [
                "الترتيب", "كود الطالب", "اسم الطالب", 
                "درجة نصف العام", "درجة نهاية العام", 
                "المعدل العام", "التقدير"
            ]
            self.tableWidget_13.setHorizontalHeaderLabels(headers)
            
            # تعبئة البيانات
            for row, student in enumerate(students):
                self.tableWidget_13.insertRow(row)
                
                items = [
                    QtWidgets.QTableWidgetItem(str(row + 1)),
                    QtWidgets.QTableWidgetItem(student.student_code),
                    QtWidgets.QTableWidgetItem(student.name),
                    QtWidgets.QTableWidgetItem(f"{student.midterm_total:.2f}"),
                    QtWidgets.QTableWidgetItem("-"),
                    QtWidgets.QTableWidgetItem("-"),
                    QtWidgets.QTableWidgetItem(self.get_grade_letter(student.midterm_total))
                ]
                
                # تعبئة الخلايا
                for col, item in enumerate(items):
                    self.tableWidget_13.setItem(row, col, item)
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    # تنسيق الصفوف الأولى
                    if row < 3:
                        item.setBackground(QtGui.QColor(255, 235, 156))  # تأكد من استيراد QtGui
                    elif student.midterm_total < 50:
                        item.setBackground(QtGui.QColor(255, 200, 200))
                    # ضبط إعدادات الجدول
            self.tableWidget_13.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tableWidget_13.setSortingEnabled(True)
            
            # إضافة إحصاءات أسفل الجدول
            self.textEdit.setText(
                f"إحصاءات الصف: {grade_name}\n"
                f"عدد الطلاب: {students.count()} \n "
                f"أعلى معدل: {students[0].midterm_total:.2f} \n "
                f"أقل معدل: {students[-1].midterm_total:.2f} \n "                
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

    
    
    def display_student_scores(self, student):
        """عرض درجات الطالب في الجدول"""
        self.tableWidget_6.setRowCount(0)
        
        # جلب الدرجات مع معلومات المادة في استعلام واحد (JOIN)
        scores = (StudentScore
                .select(StudentScore, Course)
                .join(Course)
                .where(StudentScore.student == student))
        
        for row, score in enumerate(scores):
            self.tableWidget_6.insertRow(row)
            course = score.course
            
            # إنشاء العناصر مرة واحدة
            items = [
                QtWidgets.QTableWidgetItem(course.course_code),
                QtWidgets.QTableWidgetItem(course.name),
                QtWidgets.QTableWidgetItem(str(score.midterm_score or "-")),
                QtWidgets.QTableWidgetItem(str(score.final_score or "-")),
                self.create_total_item(score)
            ]
            
            for col, item in enumerate(items):
                self.tableWidget_6.setItem(row, col, item)

    def create_total_item(self, score):
        """إنشاء عنصر الدرجة النهائية مع التنسيق"""
        total = (score.midterm_score * 0.5 + score.final_score * 0.5) if score.midterm_score and score.final_score else None
        item = QtWidgets.QTableWidgetItem(f"{total:.2f}" if total else "-")
        
        # تنسيق الخلية إذا كانت الدرجة أقل من النجاح
        if total and total < 50:  # افترضنا أن 50 هي درجة النجاح
            item.setBackground(QtGui.QColor(255, 200, 200))
        return item

    def print_settings(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            
            # إعداد حجم الورق والاتجاه (محدث)
            page_layout = QPageLayout()
            page_layout.setPageSize(QPageSize(QPageSize.A4))
            page_layout.setOrientation(QPageLayout.Portrait)  # أو QPageLayout.Landscape
            printer.setPageLayout(page_layout)
            
            print_dialog = QPrintDialog(printer, self)
            
            if print_dialog.exec_() == QPrintDialog.Accepted:
                document = QTextDocument()
                document.setDefaultStyleSheet("""
                    body { direction: rtl; font-family: Arial; margin: 30px; }
                    table { width: 100%; border-collapse: collapse; direction: rtl; }
                """)
                if self.tabWidget.currentIndex() == 7:
                    document.setHtml(self.student_grades_print())
                elif self.tabWidget.currentIndex() == 5:
                    document.setHtml(self.class_names_print())
                else:
                    document.setHtml(self.class_grades_print())
                document.print_(printer)
                
                QtWidgets.QMessageBox.information(self, "نجاح", "تم إرسال التقرير إلى الطابعة")
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الطباعة: {str(e)}")
            
    def class_names_print(self):
        font_settings = {
        'header_font': 'Arial',  # خط العناوين الرئيسية
        'header_size': '20pt',
        'body_font': 'Times New Roman',  # خط النص العادي
        'body_size': '16pt',
        'table_header_font': 'Arial',
        'table_header_size': '14pt',
        'table_body_font': 'Arial',
        'table_body_size': '14pt',
        'signature_font': 'Arial',
        'signature_size': '10pt'
        }

        level = self.comboBox_12.currentText()
        name = self.comboBox_11.currentText()
        section = self.spinBox_3.value()

        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">        
            <style>
                body {{
                    font-family: {font_settings['body_font']}, sans-serif;
                    font-size: {font_settings['body_size']};
                    margin: 0;
                    padding: 20px;
                    direction: rtl;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    font-family: '{font_settings['header_font']}';
                    font-size: {font_settings['header_size']};
                    color: #0066cc;
                }}
                .section-info {{
                    margin-bottom: 20px;
                    border: 1px solid #ddd;
                    padding: 15px;                    
                    font-family: '{font_settings['body_font']}';
                    font-size: {font_settings['body_size']};
                }}
                strong {{                
                    float: right;
                    display: block;
                    color: black;
                    margin-left: 100px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    direction: rtl;
                    text-align: center;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    direction: rtl;
                    text-align: center;
                    font-family: '{font_settings['table_header_font']}';
                    font-size: {font_settings['table_header_size']};
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                    text-align: left;
                    font-family: '{font_settings['table_body_font']}';
                    font-size: {font_settings['table_body_size']};
                    direction: rtl;                    
                }}
                .total {{
                    font-weight: bold;
                    color: #0066cc;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    float: left;
                    font-family: '{font_settings['signature_font']}';
                    font-size: {font_settings['signature_size']};
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>كشف أسماء الطلاب</h1>
            </div>

            <div class="section-info">
                <p>
                    <strong>: المرحلة</strong> {level}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
                    <strong>: الصف</strong> {name}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  
                    <strong>: الفصل</strong> {section}
                </p>
            </div>

            <table>
                <tr>
                    <th>تاريخ التسجيل</th>
                    <th>العمر</th>
                    <th>اسم الطالب</th>
                    <th>كود الطالب</th>
                </tr>
        """

        for row in range(self.tableWidget_4.rowCount()):
            html += f"""
            <tr>
                <td class="total">{self.tableWidget_4.item(row, 7).text()}</td>
                <td>{self.tableWidget_4.item(row, 3).text()}</td>
                <td>{self.tableWidget_4.item(row, 2).text()}</td>
                <td>{self.tableWidget_4.item(row, 1).text()}</td>
            </tr>
            """

        html += f"""
            </table>

            <div class="footer">
                <p>:  تاريخ الطباعة   {QDate.currentDate().toString("yyyy/MM/dd")}</p>
            </div>
        </body>
        </html>
        """

        return html

    
    def student_grades_print(self):        
        font_settings = {
        'header_font': 'Arial',  # خط العناوين الرئيسية
        'header_size': '20pt',
        'body_font': 'Times New Roman',  # خط النص العادي
        'body_size': '16pt',
        'table_header_font': 'Arial',
        'table_header_size': '16pt',
        'table_body_font': 'Arial',
        'table_body_size': '11pt',
        'signature_font': 'Arial',
        'signature_size': '16pt'
    }
        student_code = self.lineEdit_24.text()
        student_name = self.comboBox_2.currentText()
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: {font_settings['body_font']};
                    font-size: {font_settings['body_size']};
                    margin: 0;
                    padding: 20px;
                    direction: rtl;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                font-family: '{font_settings['header_font']}';
                font-size: {font_settings['header_size']};
                color: #0066cc;
                }}
                .student-info {{
                margin-bottom: 20px;
                border: 1px solid #ddd;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 5px;
                font-family: '{font_settings['body_font']}';
                font-size: {font_settings['body_size']};
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 12px;
                    text-align: right;
                    font-family: '{font_settings['table_header_font']}';
                    font-size: {font_settings['table_header_size']};
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                    text-align: right;
                    font-family: '{font_settings['table_body_font']}';
                    font-size: {font_settings['table_body_size']};
                }}
                .total {{
                    font-weight: bold;
                    color: #0066cc;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    float: left;
                    font-family: '{font_settings['signature_font']}';
                    font-size: {font_settings['signature_size']};
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="color: #0066cc;">كشف درجات الطالب</h1>
                <p>:  تاريخ الطباعة   {QDate.currentDate().toString("yyyy/MM/dd")}</p>
            </div>
            
            <div class="student-info">
                <p><strong>:  اسم الطالب </strong>  {student_name}</p>
                <p><strong>:  رقم الطالب </strong>  {student_code}</p>
                <p><strong>:  الصف </strong>  {self.lineEdit_28.text()}</p>
                <p><strong>:  المرحلة </strong>  {self.lineEdit_43.text()}</p>
            </div>
            
            <table>
                <tr>
                    <th>المجموع</th>
                    <th>درجة نهاية العام</th>
                    <th>درجة نصف العام</th>
                    <th>اسم المادة</th>
                    <th>كود المادة</th>
                </tr>
        """
        
        for row in range(self.tableWidget_6.rowCount()):
            html += f"""
            <tr>
                <td class="total">{self.tableWidget_6.item(row, 4).text()}</td>
                <td>{self.tableWidget_6.item(row, 3).text()}</td>
                <td>{self.tableWidget_6.item(row, 2).text()}</td>
                <td>{self.tableWidget_6.item(row, 1).text()}</td>
                <td>{self.tableWidget_6.item(row, 0).text()}</td>
            </tr>
            """
        
        html += """
            </table>
            
            <div class="footer">
                <p>: توقيع المسئول </p>
                <p>: التاريخ </p>
            </div>
        </body>
        </html>
        """        
        return html
    
# =================== scores End =========================

# =================== النتائج النهائية =========================

    def display_top_ten(self, grade_id=None):
        """عرض العشرة الأوائل (لصف معين أو للمدرسة ككل)"""
        try:
            term = self.comboBox_19.currentText()
            level = self.comboBox_21.currentText()
            grade_name = self.comboBox_18.currentText()
            academic_year = self.comboBox_20.currentText()
            
            grade_id = Grade.get(
            (Grade.name == grade_name) & 
            (Grade.level == level) & 
            (Grade.term == term) &
            (Grade.academic_year == academic_year)).id            
            if grade_id:
                rankings = ScoreService.calculate_class_rankings(grade_id, academic_year)
                title = "أوائل الصف"            
            self.tableWidget_13.setRowCount(0)
            
            for row, record in enumerate(rankings[:10]):  # عرض أول 10 فقط
                student = record['student'] if grade_id else record
                
                self.tableWidget_13.insertRow(row)
                self.tableWidget_13.setItem(row, 0, QtWidgets.QTableWidgetItem(str(row+1)))
                self.tableWidget_13.setItem(row, 1, QtWidgets.QTableWidgetItem(student.student_code))
                self.tableWidget_13.setItem(row, 2, QtWidgets.QTableWidgetItem(student.name))
                
                avg = record['overall_average'] if grade_id else student.overall_average
                self.tableWidget_13.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{avg:.2f}"))
                
                # تلوين الصفوف الثلاثة الأولى
                #if row < 3:
                #    for col in range(self.tableWidget_13.columnCount()):
                #        self.tableWidget_13.item(row, col).setStyleSheet(
                #                "background-color: rgb(255, 200, 200);"
                #            )
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

    def on_update_class_grades(self):
        academic_year = self.comboBox_20.currentText()
        term = self.comboBox_19.currentText()
        level = self.comboBox_21.currentText()
        grade_name = self.comboBox_18.currentText()
        if not (academic_year and term and level and grade_name):
            QtWidgets.QMessageBox.warning(self, "تحذير", "يرجى اختيار جميع الحقول المطلوبة")
            return
        grade_id = Grade.get(
            (Grade.name == grade_name) & 
            (Grade.level == level) & 
            (Grade.term == term) &
            (Grade.academic_year == academic_year)).id        
        # استدعاء الخدمة
        success, message = ScoreService.update_class_totals(grade_id, academic_year)
        
        # عرض النتيجة
        if success:
            QtWidgets.QMessageBox.information(self, "نجاح", message)
            self.refresh_class_results()  # تحديث الواجهة
        else:
            QtWidgets.QMessageBox.critical(self, "خطأ", message)
            
            
    def display_final_results(self):
        """عرض نتائج جميع طلاب الصف مع التصنيف"""
        try:
            academic_year = self.comboBox_20.currentText()
            term = self.comboBox_19.currentText()
            level = self.comboBox_21.currentText()
            grade_name = self.comboBox_18.currentText()
            if not (academic_year and term and level and grade_name):
                QtWidgets.QMessageBox.warning(self, "تحذير", "يرجى اختيار جميع الحقول المطلوبة")
                return
            grade_id = Grade.get(
                (Grade.name == grade_name) & 
                (Grade.level == level) & 
                (Grade.term == term) &
                (Grade.academic_year == academic_year)
            ).id                    
            # جلب الطلاب مصنفين مع معلومات الصف
            students = (Student
                    .select(Student, Grade)
                    .join(Grade)
                    .where(
                        (Student.grade == grade_id) &
                        (Student.overall_average > 0)
                    )
                    .order_by(Student.overall_average.desc()))
            
            # إعداد الجدول
            self.tableWidget_13.setRowCount(0)
            self.tableWidget_13.setColumnCount(7)  # عدد الأعمدة
            headers = [
                "الترتيب", "كود الطالب", "اسم الطالب", 
                "درجة نصف العام", "درجة نهاية العام", 
                "المعدل العام", "التقدير"
            ]
            self.tableWidget_13.setHorizontalHeaderLabels(headers)
            
            # تعبئة البيانات
            for row, student in enumerate(students):
                self.tableWidget_13.insertRow(row)
                
                items = [
                    QtWidgets.QTableWidgetItem(str(row + 1)),
                    QtWidgets.QTableWidgetItem(student.student_code),
                    QtWidgets.QTableWidgetItem(student.name),
                    QtWidgets.QTableWidgetItem(f"{student.midterm_total:.2f}"),
                    QtWidgets.QTableWidgetItem(f"{student.final_total:.2f}"),
                    QtWidgets.QTableWidgetItem(f"{student.overall_average:.2f}"),
                    QtWidgets.QTableWidgetItem(self.get_grade_letter(student.overall_average))
                ]
                
                # تعبئة الخلايا
                for col, item in enumerate(items):
                    self.tableWidget_13.setItem(row, col, item)
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    # تنسيق الصفوف الأولى
                    if row < 3:
                        item.setBackground(QtGui.QColor(255, 235, 156))  # تأكد من استيراد QtGui
                    elif student.overall_average < 50:
                        item.setBackground(QtGui.QColor(255, 200, 200))
                    # ضبط إعدادات الجدول
            self.tableWidget_13.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.tableWidget_13.setSortingEnabled(True)
            
            # إضافة إحصاءات أسفل الجدول
            self.textEdit.setText(
                f"إحصاءات الصف: {grade_name}\n"
                f"عدد الطلاب: {students.count()} \n "
                f"أعلى معدل: {students[0].overall_average:.2f} \n "
                f"أقل معدل: {students[-1].overall_average:.2f} \n "
                f"المعدل العام: {self.calculate_class_average(students):.2f}"
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

    def get_grade_letter(self, score):
        """تحويل المعدل إلى تقدير"""
        if score >= 270: return "ممتاز"
        elif score >= 240: return "جيد جداً"
        elif score >= 210: return "جيد"
        elif score >= 180: return "مقبول"
        else: return "راسب"


    def calculate_class_average(self, students):
        """حساب المعدل العام للصف"""
        total = sum(s.overall_average for s in students)
        return total / len(students) if students else 0
    

    def print_class_results(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        #if dialog.exec_():
            # ... (كود الطباعة المشابه للدالة السابقة)
    
    def final_results_tab(self):
        self.tabWidget.setCurrentIndex(8)        
# ==================== نهاية  النتائج النهائية =========================
# =================== Permissions =========================
    
    def open_permission_tab(self):
        self.tabWidget.setCurrentIndex(9)
        
    def save_permissions(self):
        user_name = self.comboBox_3.currentText()

        try:
            user = User.get(User.fullname == user_name)

            if user.is_admin:
                users_tab = 1
                teachers_tab = 1
                courses_tab = 1
                students_tab = 1
                student_score_tab = 1
                grades_tab = 1
                score_tab = 1
                final_results_tab = 1
                permissions_tab = 1
            else:
                users_tab = 1 if self.checkBox_15.isChecked() else 0
                teachers_tab = 1 if self.checkBox_18.isChecked() else 0
                students_tab = 1 if self.checkBox_25.isChecked() else 0
                courses_tab = 1 if self.checkBox_16.isChecked() else 0
                grades_tab = 1 if self.checkBox_21.isChecked() else 0
                score_tab = 1 if self.checkBox_26.isChecked() else 0
                student_score_tab = 1 if self.checkBox_28.isChecked() else 0
                final_results_tab = 1 if self.checkBox_33.isChecked() else 0
                permissions_tab = 1 if self.checkBox_27.isChecked() else 0

            permission, created = Permissions.get_or_create(
                user=user,
                defaults={
                    "users_tab": users_tab,
                    "teachers_tab": teachers_tab,
                    "students_tab": students_tab,
                    "courses_tab": courses_tab,
                    "grades_tab": grades_tab,
                    "score_tab": score_tab,
                    "student_score_tab": student_score_tab,
                    "final_results_tab": final_results_tab,
                    "permissions_tab": permissions_tab
                }
            )

            if not created:
                permission.users_tab = users_tab
                permission.teachers_tab = teachers_tab
                permission.students_tab = students_tab
                permission.courses_tab = courses_tab
                permission.grades_tab = grades_tab
                permission.score_tab = score_tab
                permission.student_score_tab = student_score_tab
                permission.final_results_tab = final_results_tab
                permission.permissions_tab = permissions_tab
                permission.save()

            QtWidgets.QMessageBox.information(self, "تم", "تم حفظ الصلاحيات بنجاح")

        except User.DoesNotExist:
            QtWidgets.QMessageBox.warning(self, "خطأ", f"المستخدم '{user_name}' غير موجود")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"فشل في الحفظ:\n{e}")

    def apply_permissions(self):        
        if not self.user_manager.logged_user:
            return

        try:
            permission = Permissions.get(Permissions.user == self.user_manager.logged_user)

            self.pushButton.setEnabled(permission.users_tab)
            self.pushButton_2.setEnabled(permission.teachers_tab)
            self.pushButton_3.setEnabled(permission.courses_tab)
            self.pushButton_4.setEnabled(permission.students_tab)
            self.pushButton_5.setEnabled(permission.score_tab)
            self.pushButton_6.setEnabled(permission.permissions_tab)
            self.pushButton_36.setEnabled(permission.student_score_tab)
            self.pushButton_67.setEnabled(permission.grades_tab)
            self.pushButton_72.setEnabled(permission.final_results_tab)

        except Permissions.DoesNotExist:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "لا توجد صلاحيات محددة لهذا المستخدم")

    def toggle_all_permissions(self):
        # هل جميع الصلاحيات مفعلة؟
        all_checked = all(cb.isChecked() for cb in self.permission_checkboxes)

        for cb in self.permission_checkboxes:
            cb.setChecked(not all_checked)

    def show_permissions(self):
        user_name = self.comboBox_3.currentText()
        if not user_name:
            return

        try:
            user = User.get(User.fullname == user_name)
            permission = Permissions.get(Permissions.user == user)

            self.checkBox_15.setChecked(permission.users_tab)
            self.checkBox_18.setChecked(permission.teachers_tab)
            self.checkBox_25.setChecked(permission.students_tab)
            self.checkBox_16.setChecked(permission.courses_tab)
            self.checkBox_21.setChecked(permission.grades_tab)
            self.checkBox_28.setChecked(permission.student_score_tab)
            self.checkBox_26.setChecked(permission.score_tab)
            self.checkBox_27.setChecked(permission.permissions_tab)
            self.checkBox_33.setChecked(permission.final_results_tab)
        except Permissions.DoesNotExist:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "لا توجد صلاحيات محددة لهذا المستخدم")
            for cb in self.permission_checkboxes:
                cb.setChecked(False)
        except User.DoesNotExist:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "المستخدم غير موجود")
    
    def logout(self):        
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_5.setEnabled(False)
        self.pushButton_6.setEnabled(False)
        self.pushButton_36.setEnabled(False)
        self.pushButton_67.setEnabled(False)
        self.pushButton_72.setEnabled(False)
        self.pushButton_8.setEnabled(True)
        self.tabWidget.setCurrentIndex(0)
    
    
    def upgrade_grade_scores(self):
        try:
            academic_year = self.comboBox_20.currentText()
            term = self.comboBox_19.currentText()
            level = self.comboBox_21.currentText()
            grade_name = self.comboBox_18.currentText()

            if not (academic_year and term and level and grade_name):
                QtWidgets.QMessageBox.warning(self, "تحذير", "يرجى اختيار جميع الحقول المطلوبة")
                return

            grade = Grade.get(
                (Grade.name == grade_name) & 
                (Grade.level == level) & 
                (Grade.term == term) & 
                (Grade.academic_year == academic_year)
            )

            students = Student.select().where(Student.grade == grade)

            if not students.exists():
                QtWidgets.QMessageBox.warning(self, "تحذير", "لا يوجد طلاب في هذا الصف")
                return
            
            self.tableWidget_13.setRowCount(0)
            for student in students:
                scores = StudentScore.select().where(
                    (StudentScore.student == student) & 
                    (StudentScore.academic_year == academic_year)
                )

                if not scores.exists():
                    continue  # الطالب ليس لديه درجات، ننتقل للطالب التالي

                # حساب المجموع
                midterm_total = sum([s.midterm_score or 0 for s in scores])
                final_total = sum([s.final_score or 0 for s in scores])
                average = (midterm_total + final_total) / 2

                # تحديث الطالب
                student.midterm_total = midterm_total
                student.final_total = final_total
                student.overall_average = average
                student.save()
            
            # إضافة صف إلى جدول العرض
                row = self.tableWidget_13.rowCount()
                self.tableWidget_13.insertRow(row)
                
                self.tableWidget_13.setItem(row, 0, QtWidgets.QTableWidgetItem(student.student_code))
                self.tableWidget_13.setItem(row, 1, QtWidgets.QTableWidgetItem(student.name))
                self.tableWidget_13.setItem(row, 2, QtWidgets.QTableWidgetItem(str(midterm_total)))
                self.tableWidget_13.setItem(row, 3, QtWidgets.QTableWidgetItem(str(final_total)))
                avg_item = QtWidgets.QTableWidgetItem(f"{average:.2f}")
                # تحديد اللون حسب المتوسط
                if average >= 270:
                    avg_item.setBackground(QtGui.QColor("lightgreen"))  # ممتاز
                elif average >= 150:
                    avg_item.setBackground(QtGui.QColor("khaki"))       # مقبول
                else:
                    avg_item.setBackground(QtGui.QColor("salmon"))      # راسب

    # إضافة الخلية إلى العمود الرابع (المتوسط)
                self.tableWidget_13.setItem(row, 4, avg_item)
                

            QtWidgets.QMessageBox.information(self, "تم", "تم تحديث درجات الطلاب بنجاح")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")
            
    
    def class_grades_print(self):
        font_settings = {
        'header_font': 'Arial',  # خط العناوين الرئيسية
        'header_size': '20pt',
        'body_font': 'Times New Roman',  # خط النص العادي
        'body_size': '16pt',
        'table_header_font': 'Arial',
        'table_header_size': '12pt',
        'table_body_font': 'Arial',
        'table_body_size': '12pt',
        'signature_font': 'Arial',
        'signature_size': '16pt'
    }
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: {font_settings['body_font']};
                    font-size: {font_settings['body_size']};
                    margin: 0;
                    padding: 20px;
                    direction: rtl;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                font-family: '{font_settings['header_font']}';
                font-size: {font_settings['header_size']};
                color: #0066cc;
                }}
                .student-info {{
                margin-bottom: 20px;
                border: 1px solid #ddd;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 5px;
                font-family: '{font_settings['body_font']}';
                font-size: {font_settings['body_size']};
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 12px;
                    text-align: right;
                    font-family: '{font_settings['table_header_font']}';
                    font-size: {font_settings['table_header_size']};
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                    text-align: right;
                    font-family: '{font_settings['table_body_font']}';
                    font-size: {font_settings['table_body_size']};
                }}
                .total {{
                    font-weight: bold;
                    color: #0066cc;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    float: left;
                    font-family: '{font_settings['signature_font']}';
                    font-size: {font_settings['signature_size']};
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="color: #0066cc;">كشف درجات الصف</h1>
                <p>:  تاريخ الطباعة   {QDate.currentDate().toString("yyyy/MM/dd")}</p>
            </div>
            
            <div class="student-info">
                <p><strong>:  العام الدراسي </strong>  {self.comboBox_20.currentText()}</p>
                <p><strong>:  الفصل الدراسي </strong>  {self.comboBox_19.currentText()}</p>
                <p><strong>:  المرحلة </strong>  {self.comboBox_21.currentText()}</p>
                <p><strong>:  الصف </strong>  {self.comboBox_18.currentText()}</p>
            </div>
            
            <table>
                <tr>
                    <th>التقدير</th>
                    <th>المعدل العام</th>
                    <th>درجة نهاية العام</th>
                    <th>درجة نصف العام</th>
                    <th>اسم الطالب</th>
                    <th>كود الطالب</th>
                    <th>الترتيب</th
                </tr>
        """
        
        for row in range(self.tableWidget_13.rowCount()):
            html += f"""
            <tr>
                <td>{self.tableWidget_13.item(row, 6).text()}</td>
                <td class="total">{self.tableWidget_13.item(row, 5).text()}</td>
                <td>{self.tableWidget_13.item(row, 4).text()}</td>
                <td>{self.tableWidget_13.item(row, 3).text()}</td>
                <td>{self.tableWidget_13.item(row, 2).text()}</td>
                <td>{self.tableWidget_13.item(row, 1).text()}</td>
                <td>{self.tableWidget_13.item(row, 0).text()}</td>
            </tr>
            """
        
        html += """
            </table>
            
            <div class="footer">
            </div>
        </body>
        </html>
        """        
        return html

            

def main():
    app = QtWidgets.QApplication(sys.argv)
    Window = Main()
    Window.show()
    app.exec_()
if __name__ == '__main__':
    main()
    