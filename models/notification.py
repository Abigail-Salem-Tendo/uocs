import enum
from datetime import datetime

from extensions import db


class NotificationType(enum.Enum):
    REPORT_RECEIVED = "report_received"
    HOTSPOT = "hotspot"
    STATUS_UPDATE = "status_update"


class Notification(db.Model):
    """
    In-app notification. Two use cases share this table:

    - REPORT_RECEIVED: sent to the citizen who submitted a report.

    - HOTSPOT: sent to a UtilityProvider when a new hotspot cluster forms
      (FR3.3). "Once total" per (location_id, utility_type_id) is enforced
      at the application level in HotspotService.notify_new_hotspots(),
      not by a DB constraint, since a DB-level unique on
      (location_id, utility_type_id) would also block STATUS_UPDATE and
      REPORT_RECEIVED notifications for later reports in the same
      area/utility_type.

    - STATUS_UPDATE: sent to the citizen who filed a report when a
      provider changes that report's status (e.g. to resolved).
      report_id is set for this type, null for HOTSPOT.
    """
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.Enum(NotificationType), nullable=False)

    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    utility_type_id = db.Column(db.Integer, db.ForeignKey("utility_types.id"), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey("outage_reports.id"), nullable=True)

    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    recipient = db.relationship("User", backref="notifications")
    location = db.relationship("Location")
    utility_type = db.relationship("UtilityType")
    report = db.relationship("OutageReport")

    def __repr__(self):
        return f"<Notification {self.id} [{self.type.value}] -> user {self.recipient_id}>"
    