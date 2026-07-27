from datetime import datetime, timedelta

from sqlalchemy import func

from extensions import db
from models.location import Location
from models.outage_report import OutageReport, ReportStatus
from models.utility_type import UtilityType
from models.user import UtilityProvider
from models.notification import Notification, NotificationType

HOTSPOT_WINDOW_HOURS = 12
HOTSPOT_THRESHOLD = 3


class HotspotService:
    """
    FR3.2 -- detects clusters of unresolved outage reports.
    FR3.3 -- notifies the relevant utility provider when a new hotspot forms.

    A hotspot is (location_id, utility_type_id) with >= HOTSPOT_THRESHOLD
    reports, all with reported_at within the last HOTSPOT_WINDOW_HOURS,
    and status != RESOLVED. Uses the ix_hotspot_lookup composite index
    on OutageReport for this exact (location_id, utility_type_id,
    reported_at) query shape.
    """

    @staticmethod
    def get_hotspots(window_hours=HOTSPOT_WINDOW_HOURS, threshold=HOTSPOT_THRESHOLD):
        """
        Returns a list of dicts, one per active hotspot cluster:
        {"location": Location, "utility_type": UtilityType, "report_count": int}
        """
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)

        clusters = (
            db.session.query(
                OutageReport.location_id,
                OutageReport.utility_type_id,
                func.count(OutageReport.id).label("report_count"),
            )
            .filter(
                OutageReport.reported_at >= cutoff,
                OutageReport.status != ReportStatus.RESOLVED,
            )
            .group_by(OutageReport.location_id, OutageReport.utility_type_id)
            .having(func.count(OutageReport.id) >= threshold)
            .all()
        )

        hotspots = []
        for location_id, utility_type_id, report_count in clusters:
            hotspots.append(
                {
                    "location": db.session.get(Location, location_id),
                    "utility_type": db.session.get(UtilityType, utility_type_id),
                    "report_count": report_count,
                }
            )

        return hotspots

    @staticmethod
    def is_hotspot(location_id, utility_type_id, window_hours=HOTSPOT_WINDOW_HOURS, threshold=HOTSPOT_THRESHOLD):
        """
        Point-check: is this specific (location, utility_type) pair
        currently a hotspot?
        """
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)

        count = (
            db.session.query(func.count(OutageReport.id))
            .filter(
                OutageReport.location_id == location_id,
                OutageReport.utility_type_id == utility_type_id,
                OutageReport.reported_at >= cutoff,
                OutageReport.status != ReportStatus.RESOLVED,
            )
            .scalar()
        )

        return count >= threshold

    @staticmethod
    def notify_new_hotspots(window_hours=HOTSPOT_WINDOW_HOURS, threshold=HOTSPOT_THRESHOLD):
        """
        FR3.3. Runs get_hotspots(), and for each active cluster that
        doesn't already have a Notification row (i.e. hasn't ever been
        notified -- see Notification's unique constraint), creates one
        for that utility type's provider.

        Returns the list of Notification objects created this run.
        """
        created = []

        for hotspot in HotspotService.get_hotspots(window_hours, threshold):
            location = hotspot["location"]
            utility_type = hotspot["utility_type"]
            report_count = hotspot["report_count"]

            # App-level "already notified" check -- once total per
            # (location, utility_type), regardless of DB constraints,
            # since Notification is now shared with STATUS_UPDATE rows.
            already_notified = Notification.query.filter_by(
                type=NotificationType.HOTSPOT,
                location_id=location.id,
                utility_type_id=utility_type.id,
            ).first()
            if already_notified:
                continue

            provider = UtilityProvider.query.filter_by(
                utility_type_id=utility_type.id
            ).first()

            if provider is None:
                # No provider assigned to this utility type yet -- nothing to notify.
                continue

            notification = Notification(
                type=NotificationType.HOTSPOT,
                recipient_id=provider.id,
                location_id=location.id,
                utility_type_id=utility_type.id,
                message=(
                    f"Hotspot detected: {report_count} unresolved "
                    f"{utility_type.name} reports in {location.area_name} "
                    f"within the last {window_hours}h."
                ),
            )

            db.session.add(notification)
            db.session.commit()
            created.append(notification)

        return created
    