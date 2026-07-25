from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from extensions import db
from models import Location, UtilityType, OutageReport
from models.hotspot_service import HotspotService
from models.notification import Notification

citizen_bp = Blueprint("citizen", __name__, url_prefix="/citizen")


def _require_citizen():
    """
    Inline role check — Citizen-only routes.
    TODO: promote to a @citizen_required decorator in utils/decorators.py
    once a second citizen-only route exists.
    """
    if current_user.user_type != "citizen":
        abort(403)


@citizen_bp.route("/report-outage", methods=["GET", "POST"])
@login_required
def report_outage():
    _require_citizen()

    utility_types = UtilityType.query.order_by(UtilityType.name).all()
    existing_locations = Location.query.order_by(Location.area_name).all()

    if request.method == "POST":
        area_name_raw = request.form.get("area_name", "").strip()
        address = request.form.get("address", "").strip() or None
        utility_type_id = request.form.get("utility_type_id")
        description = request.form.get("description", "").strip()

        # --- Validation ---
        errors = []
        if not area_name_raw:
            errors.append("Area/location is required.")
        if not utility_type_id:
            errors.append("Utility type is required.")
        if not description:
            errors.append("Description is required.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "citizen/submit_report.html",
                utility_types=utility_types,
                existing_locations=existing_locations,
            )

        # --- Find-or-create Location (case-insensitive match on area_name) ---
        location = Location.query.filter(
            db.func.lower(Location.area_name) == area_name_raw.lower()
        ).first()

        if not location:
            location = Location(area_name=area_name_raw, address=address)
            db.session.add(location)
            db.session.flush()  # get location.id without a full commit yet

        # --- Create the report ---
        report = OutageReport(
            citizen_id=current_user.id,
            location_id=location.id,
            utility_type_id=int(utility_type_id),
            description=description,
        )
        db.session.add(report)
        db.session.commit()

        # --- FR3.3: check if this report just formed/joined a hotspot, notify provider ---
        # Cheap to run on every submission — get_hotspots() is a single grouped
        # query, and notify_new_hotspots() is a no-op for clusters already
        # notified (enforced by Notification's unique constraint).
        HotspotService.notify_new_hotspots()

        flash("Outage report submitted successfully.", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template(
        "citizen/submit_report.html",
        utility_types=utility_types,
        existing_locations=existing_locations,
    )

@citizen_bp.route("/my-reports")
@login_required
def my_reports():
    _require_citizen()

    reports = (
        OutageReport.query.filter_by(citizen_id=current_user.id)
        .order_by(OutageReport.reported_at.desc())
        .all()
    )

    return render_template("citizen/my_reports.html", reports=reports)

@citizen_bp.route("/notifications")
@login_required
def notifications():
    _require_citizen()

    my_notifications = (
        Notification.query.filter_by(recipient_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return render_template("citizen/notifications.html", notifications=my_notifications)