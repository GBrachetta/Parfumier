from werkzeug.security import check_password_hash
from app import login_manager, mongo


class User():
    def __init__(self, username, first_name, last_name, email, _id, is_admin, avatar):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self._id = _id
        self.is_admin = is_admin
        self.avatar = avatar

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)


@login_manager.user_loader
def load_user(email):
    user = mongo.db.users.find_one({'email': email})
    if not user:
        return None
    return User(user['username'], user['first_name'], user['last_name'], user['email'], user['_id'], user['is_admin'], user['avatar'])
