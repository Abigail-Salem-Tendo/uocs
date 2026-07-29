from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User, Citizen

auth_bp = Blueprint('auth', __name__)


def _send_password_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    current_app.logger.info('Password reset link for %s: %s', user.email, reset_url)
    return True


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('auth.register'))

        new_citizen = Citizen(username=username, email=email)
        new_citizen.set_password(password)

        db.session.add(new_citizen)
        db.session.commit()

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

        if not user.active:
            flash('This account has been deactivated. Contact an administrator.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('auth.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def request_password_reset():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            _send_password_reset_email(user)

        flash('If an account exists for that email, password reset instructions have been sent.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/request_password_reset.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(
        token,
        expires_sec=current_app.config.get('RESET_PASSWORD_TOKEN_EXPIRATION', 1800),
    )

    if user is None:
        flash('That password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.request_password_reset'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password:
            flash('Password is required.', 'error')
            return render_template('auth/reset_password.html', token=token)

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html', token=token)

        user.set_password(password)
        db.session.commit()

        flash('Your password has been updated. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    #Role specific landing page instead of a generic one
    if current_user.user_type == 'citizen':
        return redirect(url_for('citizen.report_outage'))
    elif current_user.user_type == 'provider':
        return redirect(url_for('provider.dashboard'))
    elif current_user.user_type == 'admin':
        return redirect(url_for('admin.dashboard'))

    # this is a fallback but remove it 
    return render_template('auth/dashboard.html', user=current_user)