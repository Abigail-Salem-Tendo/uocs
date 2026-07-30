from datetime import datetime, timedelta

import click
from flask.cli import with_appcontext

from extensions import db
from models.user import Citizen, UtilityProvider, Admin
from models.location import Location
from models.utility_type import UtilityType
from models.outage_report import OutageReport, ReportStatus


def _get_or_create_location(area_name, address=None, latitude=None, longitude=None):
    loc = Location.query.filter(Location.area_name.ilike(area_name)).first()
    if loc:
        return loc
    loc = Location(
        area_name=area_name,
        address=address,
        latitude=latitude,
        longitude=longitude,
    )
    db.session.add(loc)
    db.session.flush()
    return loc


def _get_or_create_user(model, email, username, user_type, password, **extra_fields):
    user = model.query.filter_by(email=email).first()
    if user:
        return user

    user = model(email=email, username=username, user_type=user_type, **extra_fields)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def _refresh_demo_hotspot_cluster(citizens, electricity, ntinda):
    demo_descriptions = {
        "Power out since evening, whole street affected.",
        "No electricity, transformer might be down.",
        "Confirming outage, been out for hours.",
    }

    OutageReport.query.filter(
        OutageReport.location_id == ntinda.id,
        OutageReport.utility_type_id == electricity.id,
        OutageReport.description.in_(demo_descriptions),
    ).delete(synchronize_session=False)

    now = datetime.utcnow()
    hotspot_reports = [
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

    db.session.add_all(hotspot_reports)


@click.command("seed-db")
@with_appcontext
def seed_db():
    """Seed dev data: admin, providers, citizens, locations, and reports
    (including a deliberate hotspot cluster). Safe to re-run — checks for
    existing seed marker (admin email) before inserting."""

    seed_exists = Admin.query.filter_by(email="admin@uocs.local").first() is not None

    electricity = UtilityType.query.filter_by(name="Electricity").first()
    if not electricity:
        electricity = UtilityType(name="Electricity")
        db.session.add(electricity)
        db.session.flush()

    admin = _get_or_create_user(Admin, "admin@uocs.local", "Seed Admin", "admin", "password123")

    provider1 = _get_or_create_user(
        UtilityProvider,
        "provider1@uocs.local",
        "Umeme Provider 1",
        "provider",
        "password123",
        utility_type_id=electricity.id,
    )

    provider2 = _get_or_create_user(
        UtilityProvider,
        "provider2@uocs.local",
        "Umeme Provider 2",
        "provider",
        "password123",
        utility_type_id=electricity.id,
    )

    citizens = []
    for i in range(1, 5):
        c = _get_or_create_user(
            Citizen,
            f"citizen{i}@uocs.local",
            f"Citizen {i}",
            "citizen",
            "password123",
        )
        citizens.append(c)
    db.session.flush()

    # Approximate real-world coordinates for these Kampala suburbs — precise
    # enough for the map/hotspot demo, not surveyed exact addresses.
    ntinda = _get_or_create_location("Ntinda", latitude=0.3476, longitude=32.6122)
    bugolobi = _get_or_create_location("Bugolobi", latitude=0.3213, longitude=32.6183)
    kansanga = _get_or_create_location("Kansanga", latitude=0.2865, longitude=32.6058)
    db.session.flush()

    if seed_exists:
        _refresh_demo_hotspot_cluster(citizens, electricity, ntinda)
        db.session.commit()
        click.echo("Seed data already present — refreshed the demo hotspot cluster.")
        return

    now = datetime.utcnow()

    # Deliberate hotspot cluster: 3 reports, same location + utility type,
    # within a 12hr window -> should trip HotspotService's threshold later.
    _refresh_demo_hotspot_cluster(citizens, electricity, ntinda)

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

    db.session.add_all(other_reports)
    db.session.commit()

    click.echo("Seeded: 1 admin, 2 providers, 4 citizens, 3 locations, 5 reports (3-report Ntinda cluster).")
    click.echo("Login: admin@uocs.local / provider1@uocs.local / citizen1@uocs.local — password: password123")