from flask import render_template, redirect, flash, url_for, request
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, mongo


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')
