import os
import secrets
from flask import render_template, redirect, flash, url_for, request
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from PIL import Image
from app import app, mongo, mail
from app.users import User
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flask_mail import Message
import logging

# LOGGING
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(asctime)s %(name)s - %(filename)s :: %(lineno)d - %(levelname)s - %(message)s\n', datefmt='%Y-%m-%d %H:%M:%S')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html', title="About")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'email': form.email.data})
        if user and User.check_password(user['password'], form.password.data):
            user_obj = User(user['username'], user['first_name'], user['last_name'], user['email'],
                            user['_id'], user['is_admin'], user['avatar'])
            login_user(user_obj, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have logged in!', 'info')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Please check your credentials', 'warning')
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    users = mongo.db.users
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        users.insert({'username': form.username.data, 'first_name': form.first_name.data, 'last_name': form.last_name.data,
                      'email': form.email.data, 'password': hashed_password, 'is_admin': False, 'avatar': 'default.png'})
        user = mongo.db.users.find_one({'email': form.email.data})
        user_obj = User(user['username'], user['first_name'], user['last_name'], user['email'],
                        user['_id'], user['is_admin'], user['avatar'])
        login_user(user_obj)
        flash(f'Account created for {form.username.data}. You are now logged in.', 'info')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


def save_avatar(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateAccountForm()
    updated_user = {"username": form.username.data, "first_name": form.first_name.data,
                    "last_name": form.last_name.data, "email": form.email.data}
    if form.validate_on_submit():
        if form.avatar.data:
            avatar = save_avatar(form.avatar.data)
            old_value = mongo.db.users.find_one(
                {'username': current_user.username})
            avatar = {'$set': {'avatar': avatar}}
            mongo.db.users.update_one(old_value, avatar)
            if current_user.avatar != 'default.png':
                os.remove(os.path.join(app.root_path,
                                       'static/images', current_user.avatar))
        mongo.db.users.update_one({"_id": current_user._id}, {
                                  "$set": updated_user})
        user = mongo.db.users.find_one({'email': form.email.data})
        user_obj = User(user['username'], user['first_name'], user['last_name'], user['email'],
                        user['_id'], user['is_admin'], user['avatar'])
        login_user(user_obj)
        flash('You have updated your information', 'info')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    avatar = url_for('static', filename=f"images/{current_user.avatar}")
    return render_template('account.html', title="Account", form=form, avatar=avatar)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('So sad to see you go!', 'warning')
    return redirect(url_for('index'))

# START ATTEMPT TO SEND EMAIL PASSWORD RESET
def send_reset_email(user):
    logging.debug(user)  # LOGGING
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='code@idilettanti.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
    
If you did not make this request then ignore this email and no changes will be made.
'''
    mail.send(msg)


# COREY
# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request',
#                   sender='code@idilettanti.com', recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('users.reset_token', token=token, _external=True)}

# If you did not make this request then ignore this email and no changes will be made.
# '''
#     mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'email': form.email.data})
        send_reset_email(user)
        flash('An email has been sent to reset your email', 'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title="Reset Password", form=form)


# COREY
# @users.route('/reset_password', methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         send_reset_email(user)
#         flash('An email has been sent with instructions to reset your password', 'info')
#         return redirect(url_for('users.login'))
#     return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.update_one({'password': hashed_password})
        flash('Your password has been updated, please log in.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title="Reset Password", form=form)

# COREY
# @users.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     user = User.verify_reset_token(token)
#     if user is None:
#         flash('That is an invalid or expired token', 'warning')
#         return redirect(url_for('users.reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(
#             form.password.data).decode('utf-8')
#         user.password = hashed_password
#         db.session.commit()
#         flash('Your password has been updated. You can now log in', 'success')
#         return redirect(url_for('users.login'))
#     return render_template('reset_token.html', title='Reset Password', form=form)
