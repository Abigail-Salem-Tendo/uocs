from datetime import datetime, timedelta

import click
from flask.cli import with_appcontext

from extensions import db
from models.user import Citizen, UtilityProvider, Admin
from models.location import Location
from models.utility_type import UtilityType
from models.outage_report import OutageReport, ReportStatus


def _get_or_create_location(area_name, address=None):
    loc = Location.query.filter(Location.area_name.ilike(area_name)).first()
    if loc:
        return loc
    loc = Location(area_name=area_name, address=address)
    db.session.add(loc)
    db.session.flush()
    return loc


@click.command("seed-db")
@with_appcontext
def seed_db():
    """Seed dev data: admin, providers, citizens, locations, and reports
    (including a deliberate hotspot cluster). Safe to re-run — checks for
    existing seed marker (admin email) before inserting."""

    if Admin.query.filter_by(email="admin@uocs.local").first():
        click.echo("Seed data already present — skipping.")
        return

    electricity = UtilityType.query.filter_by(name="Electricity").first()
    if not electricity:
        electricity = UtilityType(name="Electricity")
        db.session.add(electricity)
        db.session.flush()

    admin = Admin(email="admin@uocs.local", username="Seed Admin", user_type="admin")
    admin.set_password("password123")
    db.session.add(admin)

    provider1 = UtilityProvider(
        email="provider1@uocs.local",
        username="Umeme Provider 1",
        user_type="provider",
        utility_type_id=electricity.id,
    )
    provider1.set_password("password123")

    provider2 = UtilityProvider(
        email="provider2@uocs.local",
        username="Umeme Provider 2",
        user_type="provider",
        utility_type_id=electricity.id,
    )
    provider2.set_password("password123")

    db.session.add_all([provider1, provider2])

    citizens = []
    for i in range(1, 5):
        c = Citizen(email=f"citizen{i}@uocs.local", username=f"Citizen {i}", user_type="citizen")
        c.set_password("password123")
        citizens.append(c)
    db.session.add_all(citizens)
    db.session.flush()

    ntinda = _get_or_create_location("Ntinda")
    bugolobi = _get_or_create_location("Bugolobi")
    kansanga = _get_or_create_location("Kansanga")
    db.session.flush()

    now = datetime.utcnow()

    # Deliberate hotspot cluster: 3 reports, same location + utility type,
    # within a 12hr window -> should trip HotspotService's threshold later.
    cluster_reports = [
        OutageReport(
            citizen_id=citizens[0].id,
            location_id=ntinda.id,
            utility_type_id=electricity.id,
            description="Power out since evening, whole street affected.",
            status=ReportStatus.REPORTED,
            reported_at=now - timedelta(hours=10),
        ),
        OutageReport(
            citizen_id=citizens[1].id,
            location_id=ntinda.id,
            utility_type_id=electricity.id,
            description="No electricity, transformer might be down.",
            status=ReportStatus.REPORTED,
            reported_at=now - timedelta(hours=6),
        ),
        OutageReport(
            citizen_id=citizens[2].id,
            location_id=ntinda.id,
            utility_type_id=electricity.id,
            description="Confirming outage, been out for hours.",
            status=ReportStatus.VERIFIED,
            reported_at=now - timedelta(hours=2),
        ),
    ]

    # Non-cluster reports: different locations / spread out in time,
    # so the filter dropdown and status variety have something to show.
    other_reports = [
        OutageReport(
            citizen_id=citizens[3].id,
            location_id=bugolobi.id,
            utility_type_id=electricity.id,
            description="Flickering power for the past hour.",
            status=ReportStatus.IN_PROGRESS,
            reported_at=now - timedelta(days=1),
        ),
        OutageReport(
            citizen_id=citizens[0].id,
            location_id=kansanga.id,
            utility_type_id=electricity.id,
            description="Outage resolved as of this morning.",
            status=ReportStatus.RESOLVED,
            reported_at=now - timedelta(days=2),
        ),
    ]

    db.session.add_all(cluster_reports + other_reports)
    db.session.commit()

    click.echo("Seeded: 1 admin, 2 providers, 4 citizens, 3 locations, 5 reports (3-report Ntinda cluster).")
    click.echo("Login: admin@uocs.local / provider1@uocs.local / citizen1@uocs.local — password: password123")