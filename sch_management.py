from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
import sys
from sch_management_db import User, Student, Teacher, Course, StudentCourse, Permissions # استيراد الجداول من Peewee


class UserManager:
    def __init__(self):
        self.logged_user = None  # المستخدم الحالي بعد تسجيل الدخول

    def login(self, username, password):
                        
        try:
            user = User.get(User.user_name == username)            
            if user.password == password:
                self.logged_user = user
                return True, user
            else:
                return False, "كلمة المرور غير صحيحة"
        except User.DoesNotExist:
            return False, "المستخدم غير موجود"

    def get_permissions(self):
        if not self.logged_user:
            return []
        return list(Permissions.select().where(Permissions.user == self.logged_user))


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi('school_management.ui', self)  # تحميل ملف التصميم
        
        self.tabWidget.tabBar().setVisible(False)
        self.user_manager = UserManager()
                
        self.pushButton_8.clicked.connect(self.handle_login)
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


def main():

    app = QtWidgets.QApplication(sys.argv)

    Window = Main()
    Window.show()
    app.exec_()
if __name__ == '__main__':
    main()