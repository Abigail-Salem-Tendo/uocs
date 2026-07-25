from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models.user import User, UtilityProvider
from models.utility_type import UtilityType

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_admin():
    if current_user.user_type != "admin":
        abort(403)


@admin_bp.route("/users")
@login_required
def users():
    _require_admin()

    role_filter = request.args.get("role")
    query = User.query
    if role_filter in ("citizen", "provider", "admin"):
        query = query.filter_by(user_type=role_filter)

    all_users = query.order_by(User.created_at.desc()).all()
    utility_types = UtilityType.query.order_by(UtilityType.name).all()

    return render_template(
        "admin/users.html",
        users=all_users,
        utility_types=utility_types,
        current_role=role_filter,
    )


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
def toggle_active(user_id):
    _require_admin()

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You can't deactivate your own account.", "danger")
        return redirect(url_for("admin.users"))

    user.active = not user.active
    db.session.commit()

    state = "activated" if user.active else "deactivated"
    flash(f"{user.username} was {state}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/assign-utility", methods=["POST"])
@login_required
def assign_utility(user_id):
    _require_admin()

    provider = UtilityProvider.query.get_or_404(user_id)

    utility_type_id = request.form.get("utility_type_id")
    if not utility_type_id:
        flash("Select a utility type.", "danger")
        return redirect(url_for("admin.users"))

    utility_type = UtilityType.query.get_or_404(int(utility_type_id))
    provider.utility_type = utility_type
    db.session.commit()

    flash(f"{provider.username} assigned to {utility_type.name}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/create-provider", methods=["GET", "POST"])
@login_required
def create_provider():
    _require_admin()

    utility_types = UtilityType.query.order_by(UtilityType.name).all()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        utility_type_id = request.form.get("utility_type_id")

        errors = []
        if not username or not email or not password:
            errors.append("Username, email, and password are required.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/create_provider.html", utility_types=utility_types)

        provider = UtilityProvider(username=username, email=email)
        provider.set_password(password)
        if utility_type_id:
            provider.utility_type_id = int(utility_type_id)

        db.session.add(provider)
        db.session.commit()

        flash(f"Provider account created for {username}.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/create_provider.html", utility_types=utility_types)