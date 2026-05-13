from app import app, db, bcrypt
from flask import render_template, send_from_directory, jsonify, request, redirect, url_for, flash
from app.db_classes import User
from flask_login import login_required, login_user, logout_user
from app.forms import LoginForm

#region login

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect('/')
        flash('Login invalid', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#endregion login