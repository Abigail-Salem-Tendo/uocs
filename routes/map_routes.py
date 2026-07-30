"""
Map data endpoint.

Add this route to whatever blueprint handles your outage reports (adjust
the import paths/model names to match yours — using OutageReport, Location,
UtilityType per your class diagram).

Returns every report that has a location attached, in the shape the
frontend map.js expects. Both the citizen map and the provider dashboard
map hit this same endpoint (citizen map is city-wide/public per your
call).

Hotspot status isn't a column on OutageReport — HotspotService computes
it dynamically, grouped by (location, utility_type). So we pull the
current hotspot set once per request and check each report against it,
rather than reading a field that doesn't exist on the model.
"""

from flask import Blueprint, jsonify
from flask_login import login_required

from models import OutageReport, Location, UtilityType
from models.hotspot_service import HotspotService

map_bp = Blueprint("map", __name__)


@map_bp.route("/api/outages/map-data")
@login_required
def outages_map_data():
    reports = OutageReport.query.join(Location).all()

    # Build a set of (location_id, utility_type_id) currently flagged as
    # hotspots, so we can check membership per report below instead of
    # calling get_hotspots() once per row.
    hotspot_keys = {
        (h["location"].id, h["utility_type"].id)
        for h in HotspotService.get_hotspots()
    }

    data = [
        {
            "id": report.id,
            "lat": report.location.latitude,
            "lng": report.location.longitude,
            "type": report.utility_type.name,
            "status": report.status.name,
            "isHotspot": (report.location_id, report.utility_type_id) in hotspot_keys,
            "description": (report.description or "")[:120],
        }
        for report in reports
        if report.location is not None
    ]

    return jsonify(data)