# KTL ISP Billing Project

This is a Django project for managing ISP billing, with a modular app structure and environment-specific settings for development and production.

## Project Structure

```
ktl_isp_billing/
├── manage.py
├── apps/
│   └── organizations/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations/
│       ├── models.py
│       ├── tests.py
│       ├── views.py
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── development.py
│   │   ├── production.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
├── requirements.txt
├── README.md
```

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- Installed dependencies (see [Installation](#installation))

## Installation

1. **Clone the Repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd ktl_isp_billing
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Install the required packages:
   ```bash
   pip install djangorestframework djangorestframework-simplejwt django-cors-headers drf-yasg django-filter django-extensions django-debug-toolbar
   ```
   Or, if a `requirements.txt` file exists:
   ```bash
   pip install -r requirements.txt
   ```

## Creating a New App

To create a new Django app (e.g., `new_app`) inside the `apps/` directory:

1. **Navigate to the Project Root**:
   Ensure you're in the directory containing `manage.py`:
   ```bash
   cd /path/to/ktl_isp_billing
   ```

2. **Run the `startapp` Command**:
   Create the app in the `apps/` directory:
   ```bash
   python manage.py startapp new_app apps/new_app
   ```
   This creates a directory `apps/new_app/` with the standard Django app structure:
   ```
   apps/new_app/
   ├── __init__.py
   ├── admin.py
   ├── apps.py
   ├── migrations/
   │   └── __init__.py
   ├── models.py
   ├── tests.py
   ├── views.py
   ```

3. **Register the App**:
   Add the app to `INSTALLED_APPS` in `config/settings/development.py` (and `production.py` if needed):
   ```python
   INSTALLED_APPS = [
       # Other apps...
       'apps.new_app',
       'apps.organizations',
       'rest_framework',
       'rest_framework_simplejwt',
       'rest_framework_simplejwt.token_blacklist',
       'corsheaders',
       'drf_yasg',
       'django_filters',
       'django_extensions',
       'debug_toolbar',  # Development only
   ]
   ```

## Running Migrations for Specific Apps

After creating or modifying models in an app (e.g., `apps/organizations/models.py`), you need to create and apply migrations to update the database schema.

1. **Navigate to the Project Root**:
   ```bash
   cd /path/to/ktl_isp_billing
   ```

2. **Create Migrations for a Specific App**:
   Use the `makemigrations` command with the app name to generate migration files for that app only. For example, for the `organizations` app:
   ```bash
   python manage.py makemigrations organizations --settings=config.settings.development
   ```
   This creates migration files in `apps/organizations/migrations/`.

3. **Review Migration Files**:
   Check the generated migration files (e.g., `apps/organizations/migrations/0001_initial.py`) to ensure they reflect your model changes correctly.

4. **Apply Migrations**:
   Apply the migrations to update the database:
   ```bash
   python manage.py migrate organizations --settings=config.settings.development
   ```
   This applies only the migrations for the `organizations` app. To apply migrations for all apps, omit the app name:
   ```bash
   python manage.py migrate --settings=config.settings.development
   ```

5. **Optional: Dry Run**:
   To preview migrations without applying them:
   ```bash
   python manage.py migrate organizations --settings=config.settings.development --plan
   ```

6. **Troubleshooting Migrations**:
   - If migrations fail, check for errors in `models.py` or ensure the database is accessible.
   - To reset migrations for an app (use with caution):
     ```bash
     python manage.py migrate organizations zero --settings=config.settings.development
     ```
     Then recreate migrations:
     ```bash
     python manage.py makemigrations organizations --settings=config.settings.development
     python manage.py migrate organizations --settings=config.settings.development
     ```

## Running the Development Server

The project uses environment-specific settings: `config/settings/development.py` for local development and `config/settings/production.py` for production.

### Development Environment

1. **Navigate to the Project Root**:
   ```bash
   cd /path/to/ktl_isp_billing
   ```

2. **Activate Virtual Environment** (if used):
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Set the Settings Module** (optional):
   You can set the `DJANGO_SETTINGS_MODULE` environment variable:
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.development
   ```
   Alternatively, specify the settings file directly in the command.

4. **Run the Server**:
   Start the Django development server:
   ```bash
   python manage.py runserver --settings=config.settings.development
   ```
   The server will run at `http://127.0.0.1:8000/`.

5. **Verify Debug Toolbar** (if used):
   Ensure `DEBUG = True` in `development.py` and access the site from `127.0.0.1` to see the debug toolbar.

### Production Environment

**Note**: The development server (`runserver`) is not suitable for production. Use a WSGI server like Gunicorn with a reverse proxy like Nginx.

1. **Set the Settings Module**:
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.production
   ```

2. **Collect Static Files**:
   ```bash
   python manage.py collectstatic --settings=config.settings.production
   ```

3. **Run with Gunicorn**:
   Install Gunicorn:
   ```bash
   pip install gunicorn
   ```
   Start the server:
   ```bash
   gunicorn ktl_isp_billing.wsgi:application --bind 0.0.0.0:8000
   ```

4. **Configure Nginx** (optional):
   Set up Nginx as a reverse proxy to forward requests to Gunicorn. Example Nginx config:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Configuration Notes

- **Development Settings** (`config/settings/development.py`):
  - `DEBUG = True`
  - Uses SQLite by default (or configure as needed)
  - Includes `debug_toolbar` for debugging

- **Production Settings** (`config/settings/production.py`):
  - `DEBUG = False`
  - Configure `ALLOWED_HOSTS` (e.g., `['yourdomain.com', 'ip-address']`)
  - Use a production database (e.g., PostgreSQL)

- **Using `.env` File** (optional):
  Install `python-decouple`:
  ```bash
  pip install python-decouple
  ```
  Create a `.env` file:
  ```
  DJANGO_SETTINGS_MODULE=config.settings.development
  ```
  Update settings to read from `.env`:
  ```python
  from decouple import config
  import os
  os.environ['DJANGO_SETTINGS_MODULE'] = config('DJANGO_SETTINGS_MODULE')
  ```

## Troubleshooting

- **Settings Module Error**:
  If you see `ModuleNotFoundError: No module named 'config.settings.develop'`, use `config.settings.development`:
  ```bash
  python manage.py runserver --settings=config.settings.development
  ```

- **Debug Toolbar Not Showing**:
  Verify:
  - `DEBUG = True` in `development.py`
  - `'debug_toolbar'` in `INSTALLED_APPS`
  - `'debug_toolbar.middleware.DebugToolbarMiddleware'` in `MIDDLEWARE`
  - `INTERNAL_IPS = ['127.0.0.1']`
  - URL pattern: `path('__debug__/', include('debug_toolbar.urls'))`

- **Migration Errors**:
  - Ensure models in `apps/organizations/models.py` are valid.
  - Check database connectivity (e.g., SQLite file exists or PostgreSQL server is running).
  - Use `--plan` to debug migration issues:
    ```bash
    python manage.py migrate organizations --settings=config.settings.development --plan
    ```

- **Database Issues**:
  Check `DATABASES` in the settings file. For SQLite:
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': BASE_DIR / 'db.sqlite3',
      }
  }
  ```

## Contributing

1. Create a new app for your feature (see [Creating a New App](#creating-a-new-app)).
2. Define models and run migrations (see [Running Migrations for Specific Apps](#running-migrations-for-specific-apps)).
3. Write views, URLs, and tests in the app.
4. Submit a pull request with your changes.

## License

[Specify your license, e.g., MIT, or remove this section if not applicable]