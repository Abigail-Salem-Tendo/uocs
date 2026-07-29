# UOCS:  Utility Outage Coordination System

UOCS is a Flask-based utility outage reporting and coordination platform designed to connect citizens, utility providers, and administrators around outage tracking, escalation, and resolution. Citizens can report outages and follow progress, providers can review and update reports, and administrators can oversee the system from end to end.

The project focuses on a practical workflow for collecting outage reports, coordinating responses, and maintaining operational visibility across roles. It also includes seeded demo data and database migrations so the application can be set up locally and exercised quickly.

## Key Features

### Citizen
- Submit outage reports.
- View submitted reports.
- Track notifications related to report status updates.

### Provider
- Access a provider dashboard.
- Review assigned or relevant outage reports.
- Update report status as outages move through the response process.

### Admin
- View an administrative dashboard.
- Manage users and activation status.
- Create provider accounts and assign utility types.
- Delete reports when necessary.

## Tech Stack

- Python / Flask
- Flask-SQLAlchemy
- Flask-Migrate / Alembic
- Flask-Login
- Flask-Bcrypt
- Flask-WTF / CSRF protection
- MySQL
- PyMySQL
- HTML templates with Jinja2
- CSS for styling

## Prerequisites

- Python 3.x
- MySQL Server
- `pip` and `venv`

## Local Setup

1. Clone the repository and move into the project folder.

	```bash
	git clone <repository-url>
	cd uocs
	```

2. Create and activate a virtual environment.

	```bash
	python -m venv .venv
	.venv\\Scripts\\activate
	```

	On macOS/Linux, activate with:

	```bash
	source .venv/bin/activate
	```

3. Install the project dependencies.

	```bash
	pip install -r requirements.txt
	```

4. Create a MySQL database for the application.

	```sql
	CREATE DATABASE <your_database_name>;
	```

5. Set the required environment variables.

	```bash
	SECRET_KEY=<your_secret_key>
	DB_USERNAME=<your_mysql_username>
	DB_PASSWORD=<your_mysql_password>
	DB_HOST=<your_mysql_host>
	DB_NAME=<your_mysql_database_name>
	RESET_PASSWORD_TOKEN_EXPIRATION=<optional_token_expiration>
	```

	If your deployment uses email delivery, add the relevant mail-related placeholders as well, such as your SMTP host, port, username, password, and TLS/SSL settings.

6. Run the database migrations.

	```bash
	flask db upgrade
	```

7. Seed the database with demo data.

	```bash
	flask seed-db
	```

8. Start the development server.

	```bash
	flask run
	```

## Default Seeded Test Accounts

The seed script creates demo accounts for each role. The exact credentials are defined in the seed script itself.

| Role | Example account |
| --- | --- |
| Admin | Seed admin account |
| Provider | Seed provider account |
| Citizen | Seed citizen account |

## Project Structure

```text
uocs/
├── app.py              # Flask app factory and CLI registration
├── config.py           # Application configuration and database settings
├── extensions.py       # Shared Flask extensions
├── migrations/         # Alembic migration environment and revision files
├── models/             # Database models and related domain objects
├── routes/             # Blueprint route handlers for each role
├── services/           # Business logic and supporting services
├── static/             # CSS and other static assets
├── templates/          # Jinja2 templates for the UI
├── utils/              # Seed script and helper utilities
└── requirements.txt    # Python dependencies
```

## Deployment Notes

For production, run the application with Gunicorn behind Nginx and use Certbot to provision HTTPS certificates. Treat this as a deployment pointer only; production hardening, process supervision, and reverse-proxy tuning should follow your hosting environment.

