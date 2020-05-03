from flask import render_template, redirect, flash, url_for, request
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
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
                            user['_id'], user['is_admin'])
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
                      'email': form.email.data, 'password': hashed_password, 'is_admin': False})
        flash(f'Account created for {form.username.data}', 'info')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateAccountForm()
    
    return render_template('account.html', title="About", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('So sad to see you go!', 'warning')
    return redirect(url_for('index'))
