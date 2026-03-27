from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from model.Auth import LoginLDAP, User
from model.Log import LogHelper

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        loginData = LoginLDAP(request)

        if loginData.isValidLogin:

            if loginData.isDefaultCredentials:
                LogHelper.log_action('Login', f"User {loginData.username} logged in (static user)")
            else:
                LogHelper.log_action('Login', f"User {loginData.username} logged in (LDAP)")

            session['username'] = loginData.username

            login_user(User(loginData.username))

            return redirect(url_for('index'))

        else:
            flash(loginData.errorMessage, 'danger')

    return render_template("login.html")


@auth_bp.route('/logout')
@login_required
def logout():

    LogHelper.log_action('Logout', f"User {current_user.id} logged out")

    logout_user()

    flash('You have been logged out.', 'info')

    return redirect(url_for('auth.login'))