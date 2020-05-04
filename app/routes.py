import os
import secrets
from flask import render_template, redirect, flash, url_for, request
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from PIL import Image
from app import app, mongo
from app.users import User
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm


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
