"""
Imports necessary to check the hashed password,
the serializer to allow to create a reset password token, mongodb,
current_app for the above and login_manager to deal with user session
"""
from werkzeug.security import check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from parfumier import login_manager, mongo


class User:
    """
    Initialises the User class and its methods that deal with
    session, password check and reset email.
    """

    def __init__(
            self, username,
            first_name,
            last_name,
            email,
            _id,
            is_admin,
            avatar,
    ):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self._id = _id
        self.is_admin = is_admin
        self.avatar = avatar

    def is_authenticated(self):
        """
        One of the required parameters needed by flask_login
        to deal with user session
        """
        return True

    def is_active(self):
        """
        One of the required parameters needed by flask_login
        to deal with user session
        """
        return True

    def is_anonymous(self):
        """
        One of the required parameters needed by flask_login
        to deal with user session
        """
        return False

    def get_id(self):
        """
        One of the required parameters needed by flask_login
        to deal with user session
        """
        return self.email

    @staticmethod
    def check_password(password_hash, password):
        """
        Uses check_password_hash to check the hashed password against
        the entered password to find or not a match.
        """
        return check_password_hash(password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        """
        Deals with the token to reset the password.
        This token has a life of 1800ms, after which it becomes invalid.
        It serialises it (SECRET_KEY is required too) and passes the
        life length.
        Returns a serialised token, decoded.
        """
        ser = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return ser.dumps({"email": self.email}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        """
        Veryfies the validity of the token generated above.
        """
        ser = Serializer(current_app.config["SECRET_KEY"])
        try:
            email = ser.loads(token)["email"]
        except Exception:
            return None
        return mongo.db.users.find_one({"email": email})


class Perfume:
    """
    Initialises the Perfume class
    """

    def __init__(
            self,
            author,
            brand,
            name,
            description,
            date_updated,
            public,
            picture,
            perfume_type,
    ):
        self.author = author
        self.brand = brand
        self.name = name
        self.descritpion = description
        self.date_updated = date_updated
        self.public = public
        self.picture = picture
        self.perfume_type = perfume_type


class Types:
    """
    Initialises the Types class
    """

    def __init__(self, type_name, description, author):
        self.type_name = type_name
        self.description = description
        self.author = author


@login_manager.user_loader
def load_user(email):
    """
    Queries the user by their email address, if it exists, returns a User
    object to keep logged in the session.
    """
    user = mongo.db.users.find_one({"email": email})
    if not user:
        return None
    return User(
        user["username"],
        user["first_name"],
        user["last_name"],
        user["email"],
        user["_id"],
        user["is_admin"],
        user["avatar"],
    )
