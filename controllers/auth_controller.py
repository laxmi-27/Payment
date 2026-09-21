from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from model.Auth import LoginLDAP, User, DefaultCredentials
from model.Log import LogHelper

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        loginData = LoginLDAP(request)

        if loginData.isValidLogin:
            if loginData.isDefaultCredentials:
                LogHelper.log_action('Login', f"User {loginData.username} logged in (static user)")
                session['role']      = 'System Administrator'
                session['auth_type'] = 'default'
            else:
                LogHelper.log_action('Login', f"User {loginData.username} logged in (LDAP)")
                session['role']      = 'LDAP User'
                session['auth_type'] = 'ldap'

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


@auth_bp.route('/profile_info')
@login_required
def profile_info():
    return jsonify({
        'username': current_user.id,
        'role':     session.get('role', 'System Administrator'),
    })


@auth_bp.route('/profile')
@login_required
def profile():
    user_data = {
        'username':    current_user.id,
        'role':        session.get('role', 'System Administrator'),
        'auth_type':   session.get('auth_type', 'default'),
        'status':      'Active',
    }
    return render_template('admin_profile.html', user=user_data)


@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if session.get('auth_type') != 'default':
        flash('Password changes are managed by your organisation directory service.', 'info')
        return redirect(url_for('auth.profile'))

    current_pw  = request.form.get('current_password', '')
    new_pw      = request.form.get('new_password', '')
    confirm_pw  = request.form.get('confirm_password', '')

    if current_pw != DefaultCredentials.password:
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('auth.profile'))

    if not new_pw or len(new_pw) < 6:
        flash('New password must be at least 6 characters.', 'danger')
        return redirect(url_for('auth.profile'))

    if new_pw != confirm_pw:
        flash('New password and confirmation do not match.', 'danger')
        return redirect(url_for('auth.profile'))

    # Update in-memory credentials so current session validates new password immediately
    DefaultCredentials.password = new_pw

    # Persist to .env file
    import os, re
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    try:
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                content = f.read()
            content = re.sub(
                r'^(DEFAULT_PASSWORD\s*=\s*).*$',
                rf'\g<1>{new_pw}',
                content, flags=re.MULTILINE
            )
            with open(env_path, 'w') as f:
                f.write(content)
    except Exception as e:
        print(f"Warning: could not update .env file: {e}")

    LogHelper.log_action('Change Password', f"User {current_user.id} changed their password")
    flash('Password changed successfully.', 'success')
    return redirect(url_for('auth.profile'))
