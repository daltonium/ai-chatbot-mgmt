from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from .models import User
from . import db

auth_bp = Blueprint('auth', __name__)

def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapped

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role = request.form.get('role', 'user')

        if not username or not password:
            flash('Username and password are required.')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('auth.register'))

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!')
            return redirect(url_for('bot.dashboard'))

        flash('Invalid username or password.')
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('auth.login'))
