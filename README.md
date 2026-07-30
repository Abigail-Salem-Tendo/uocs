# UOCS: Utility Outage Coordination System

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

- Python 3.9–3.12 (Flask 3.1+ requires Python 3.9 or newer)
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
	```

	On Windows:

	```bash
	.venv\Scripts\activate
	```

	On macOS/Linux:

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

	Create a `.env` file in the project root (this is auto-loaded via `python-dotenv`, no need to `export` these manually) with the following keys:

	```
	SECRET_KEY=<your_secret_key>
	DB_USERNAME=<your_mysql_username>
	DB_PASSWORD=<your_mysql_password>
	DB_HOST=<your_mysql_host>
	DB_NAME=<your_mysql_database_name>
	RESET_PASSWORD_TOKEN_EXPIRATION=<optional_token_expiration>
	GOOGLE_MAPS_API_KEY=<optional_google_maps_key>
	```

	`GOOGLE_MAPS_API_KEY` is optional — the app defaults to an empty string if unset, but the map feature won't render pins without it.

	If your deployment uses email delivery, add the relevant mail-related placeholders as well, such as your SMTP host, port, username, password, and TLS/SSL settings.

	**Make sure `.env` is listed in `.gitignore`** so credentials are never committed to the repository.

6. Set the Flask app entry point.

	The app uses a factory pattern (`create_app()` in `app.py`), so set:

	```bash
	export FLASK_APP=app:create_app
	```

	(On Windows: `set FLASK_APP=app:create_app`)

7. Run the database migrations.

	```bash
	flask db upgrade
	```

	Note: this expects the `migrations/` folder (already included in this repo) to exist. You do not need to run `flask db init`.

8. Seed the database with demo data.

	```bash
	flask seed-db
	```

9. Start the development server.

	```bash
	flask run
	```

## Default Seeded Test Accounts

The seed script creates demo accounts for each role. See `utils/seed.py` for the exact usernames and passwords it creates.

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
├── static/              # CSS and other static assets
├── templates/           # Jinja2 templates for the UI
├── utils/               # Seed script and helper utilities
└── requirements.txt     # Python dependencies
```

## Deployment Notes

For production, run the application with Gunicorn behind Nginx and use Certbot to provision HTTPS certificates.

Since the app uses the factory pattern, start Gunicorn with:

```bash
gunicorn "app:create_app()"
```

(not the more common `gunicorn app:app`, which won't work here since there's no module-level `app` object).

Treat this as a deployment pointer only; production hardening, process supervision, and reverse-proxy tuning should follow your hosting environment.

## Troubleshooting

- **`Can't connect to MySQL server`**: confirm MySQL is running locally (`sudo systemctl status mysql` on Linux, or check your MySQL service on Windows/macOS) and that `DB_HOST`, `DB_USERNAME`, and `DB_PASSWORD` in `.env` are correct.
- **`Could not locate a Flask application`**: confirm `FLASK_APP` is set correctly in your current shell session (step 6) before running `flask` commands.