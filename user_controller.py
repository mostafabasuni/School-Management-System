
from sch_management_db import User, Permissions # استيراد الجداول من Peewee
import bcrypt

class UserManager:
    def __init__(self):
        self.logged_user = None  # المستخدم الحالي بعد تسجيل الدخول

    def verify_password(self, user, password):
        try:
            return bcrypt.checkpw(password.encode(), user.password.encode())
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
    
    def login(self, username, password):
        try:
            user = User.get(User.user_name == username)
            if self.verify_password(user, password):  # استخدام الدالة المخصصة للتحقق
                self.logged_user = user
                return True, user
            else:
                return False, "كلمة المرور غير صحيحة"
        except User.DoesNotExist:
            return False, "المستخدم غير موجود"
        except Exception as e:
            return False, f"حدث خطأ: {str(e)}"   
    
    
    def get_permissions(self):
        if not self.logged_user:
            return []
        return list(Permissions.select().where(Permissions.user == self.logged_user))

    
    @staticmethod
    def create_user(fullname, username, password, job, is_admin=False):
        try:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            user = User.create(
                fullname=fullname,
                user_name=username,
                password=hashed_password,
                job=job,
                is_admin=is_admin
            )
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @staticmethod
    def get_all_users():
        return list(User.select())