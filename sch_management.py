from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
import sys
from user_controller import UserManager  # استيراد وحدة التحكم للمستخدم
from sch_management_db import User, Student, Teacher, Course, StudentCourse, Permissions # استيراد الجداول من Peewee
from werkzeug.security import generate_password_hash, check_password_hash




class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi('school_management.ui', self)  # تحميل ملف التصميم
        
        self.tabWidget.tabBar().setVisible(False)
        self.user_manager = UserManager()
        self.tableWidget.itemClicked.connect(self.user_table_select)
        self.pushButton.clicked.connect(self.open_users_tab)        
        self.pushButton_8.clicked.connect(self.handle_login)
        self.pushButton_9.clicked.connect(self.clear_user_form)
        self.pushButton_10.clicked.connect(self.handle_user_creation)
        self.pushButton_11.clicked.connect(self.handle_user_update)
        self.pushButton_12.clicked.connect(self.handle_user_delete)
        self.load_users()  # تحميل المستخدمين عند بدء التشغيل
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
        
def main():

    app = QtWidgets.QApplication(sys.argv)

    Window = Main()
    Window.show()
    app.exec_()
if __name__ == '__main__':
    main()