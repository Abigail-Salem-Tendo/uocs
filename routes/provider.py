from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models.outage_report import OutageReport, ReportStatus
from models.location import Location

provider_bp = Blueprint("provider", __name__, url_prefix="/provider")


def _require_provider():
    if current_user.user_type != "provider":
        abort(403)


@provider_bp.route("/dashboard")
@login_required
def dashboard():
    _require_provider()

    query = OutageReport.query.filter_by(utility_type_id=current_user.utility_type_id)

    status_filter = request.args.get("status")
    if status_filter:
        try:
            query = query.filter_by(status=ReportStatus[status_filter])
        except KeyError:
            flash("Invalid status filter.", "warning")
            status_filter = None

    location_filter = request.args.get("location_id", type=int)
    if location_filter:
        query = query.filter_by(location_id=location_filter)

    reports = query.order_by(OutageReport.reported_at.desc()).all()

    # Only show locations that actually have reports for this provider's
    # utility type, so the filter dropdown isn't cluttered with irrelevant areas.
    locations = (
        Location.query.join(OutageReport)
        .filter(OutageReport.utility_type_id == current_user.utility_type_id)
        .distinct()
        .order_by(Location.area_name)
        .all()
    )

    return render_template(
        "provider/dashboard.html",
        reports=reports,
        locations=locations,
        statuses=list(ReportStatus),
        current_status=status_filter,
        current_location=location_filter,
    )


@provider_bp.route("/reports/<int:report_id>/status", methods=["POST"])
@login_required
def update_status(report_id):
    _require_provider()

    report = OutageReport.query.get_or_404(report_id)

    # Server-side re-check: the dashboard list is already scoped, but a
    # direct POST to this endpoint could target any report_id.
    if report.utility_type_id != current_user.utility_type_id:
        abort(403)

    new_status = request.form.get("status")
    try:
        report.status = ReportStatus[new_status]
    except KeyError:
        flash("Invalid status value.", "danger")
        return redirect(url_for("provider.dashboard"))

    db.session.commit()
    flash(f"Report #{report.id} status updated to {report.status.value}.", "success")
    return redirect(url_for("provider.dashboard"))