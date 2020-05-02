from flask import render_template, redirect, flash, url_for, request
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, mongo
from app.users import User
from app.forms import RegistrationForm


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html', title="About")


@app.route('/login')
def login():
    return render_template('login.html', title='Login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    users = mongo.db.users
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        users.insert({'username': form.username.data, 'first_name': form.first_name.data,
                      'email': form.email.data, 'password': hashed_password, 'is_admin': False})
        flash(f'Account created for {form.username.data}', 'info')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
