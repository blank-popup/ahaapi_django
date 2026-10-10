# Django REST API Server

A practical architecture guide and implementation checklist for a Django REST API server built with `uv`, Django REST Framework, JWT authentication, structured logging, automatic API documentation, and production-oriented practices.

> **Checklist notation:** `[x]` is an illustrative completed-item
> example; `[ ]` means an item remains to be implemented or verified.
> These marks do not assert that a feature is already implemented in
> your project. Installing a package alone does not configure every
> feature described below.

## 1. Technology Stack

Install the core packages:

``` powershell
uv add django djangorestframework
uv add --dev pytest pytest-django ruff
uv add djangorestframework-simplejwt
uv add drf-spectacular
uv add django-filter
uv add "psycopg[binary]"
```

  -----------------------------------------------------------------------
  Package                             Purpose
  ----------------------------------- -----------------------------------
  `django`                            Web framework, settings, ORM, and admin

  `djangorestframework`               REST API views, serializers, authentication, and permissions

  `djangorestframework-simplejwt`     JWT creation, validation, and refresh

  `drf-spectacular`                   OpenAPI schema, Swagger UI, and ReDoc

  `django-filter`                     Declarative API filtering

  `psycopg[binary]`                   PostgreSQL database driver

  `pytest`                            Test runner

  `pytest-django`                     Django testing integration

  `ruff`                              Linting and code formatting
  -----------------------------------------------------------------------

## 2. Project Checklist

Example checklist usage:

-   [x] Initialize the project and install the core dependencies.
-   [x] Document the intended architecture and implementation plan.
-   [ ] Configure JWT authentication and token lifetimes.
-   [ ] Implement user, group, role, and object-level authorization.
-   [ ] Configure console, file, email, and database logging.
-   [ ] Generate and secure OpenAPI documentation.
-   [ ] Add validation, consistent error responses, filtering, and pagination.
-   [ ] Configure database migrations, backups, and recovery procedures.
-   [ ] Add automated tests and Ruff checks.
-   [ ] Separate development and production settings.
-   [ ] Configure security controls, health checks, monitoring, and deployment.

The checked items are examples of checklist formatting. Update them to
reflect the actual state of your project.

## 3. Recommended Project Structure (A: `src/ahaapi/config/`)

Keep the Django project configuration and application modules inside the importable `ahaapi` package. Keep `manage.py` at the repository root.

``` text
ahaapi/
├── .venv/
├── src/
│   └── ahaapi/
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── asgi.py
│       │   ├── wsgi.py
│       │   ├── urls.py
│       │   └── settings/
│       │       ├── __init__.py
│       │       ├── base.py
│       │       ├── development.py
│       │       └── production.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── apps.py
│       │   ├── models.py
│       │   ├── serializers.py
│       │   ├── urls.py
│       │   └── views.py
│       ├── users/
│       │   ├── __init__.py
│       │   ├── apps.py
│       │   ├── models.py
│       │   ├── serializers.py
│       │   ├── urls.py
│       │   └── views.py
│       └── common/
├── tests/
├── .env.example
├── .gitignore
├── manage.py
├── pyproject.toml
├── uv.lock
└── README.md
```

Responsibilities:

-   `src/ahaapi/config/settings/base.py`: shared settings
-   `src/ahaapi/config/settings/development.py`: development-specific settings
-   `src/ahaapi/config/settings/production.py`: production-specific settings
-   `src/ahaapi/config/urls.py`: root URL configuration
-   `src/ahaapi/config/asgi.py`: ASGI entry point
-   `src/ahaapi/config/wsgi.py`: WSGI entry point
-   `src/ahaapi/api/`: API endpoints and domain features
-   `src/ahaapi/users/`: users, groups, roles, and permission-related features
-   `src/ahaapi/common/`: shared exception handling, response formats, and utilities
-   `tests/`: automated tests
-   `manage.py`: project management command entry point

### Important import-path rule

Because the Django configuration package is `ahaapi.config`, use fully qualified module paths consistently:

-   `DJANGO_SETTINGS_MODULE`: `ahaapi.config.settings.development` or `ahaapi.config.settings.production`
-   `ROOT_URLCONF`: `ahaapi.config.urls`
-   `WSGI_APPLICATION`: `ahaapi.config.wsgi.application`
-   `ASGI_APPLICATION`: `ahaapi.config.asgi.application`

Do not use `config.settings` or `config.urls` with this layout.

### `pyproject.toml` package configuration

Ensure the project uses a `src` layout and that the `ahaapi` package is included when building/installing the project. With a recent `uv` project using `uv_build`, the package configuration may be set explicitly, for example:

``` toml
[tool.uv.build-backend]
module-name = "ahaapi"
module-root = "src"
```

Check the `uv_build` documentation and the existing `pyproject.toml` before adding or changing build configuration. Keep the existing `[project]`, dependency, and `[build-system]` sections intact unless there is a specific reason to change them.

## 4. Django Management Commands

With `manage.py` in the repository root and the package correctly available in the environment, use:

``` powershell
uv run python manage.py check
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

If Python cannot import `ahaapi`, verify that the project package is installed in the environment and that the `src` layout is configured correctly. Do not work around import errors by mixing root-level and package-level `config` paths.

## 5. Environment-Specific Settings

Use a shared base settings module plus environment-specific modules:

-   `base.py`: shared configuration
-   `development.py`: local development
-   `production.py`: production security and service configuration

The `manage.py`, `asgi.py`, and `wsgi.py` entry points should provide a sensible default settings module. An environment variable can override that default. Avoid hard-coding different environments into separate entry points.

Example default in `manage.py`, `asgi.py`, and `wsgi.py`:

``` python
import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "ahaapi.config.settings.development",
)
```

Set the environment explicitly when needed.

``` powershell
# Development
$env:DJANGO_SETTINGS_MODULE = "ahaapi.config.settings.development"
uv run python manage.py runserver

# Production settings selection (deploy with a production-grade WSGI/ASGI server)
$env:DJANGO_SETTINGS_MODULE = "ahaapi.config.settings.production"
```

The selected module must exist and be importable. Production deployment also needs a WSGI/ASGI server, secure secret management, HTTPS, and appropriate process management. Do not use Django's `runserver` as the production server.

## 6. JWT Authentication

Use `djangorestframework-simplejwt` to implement token-based authentication.

-   [ ] Issue an Access Token and Refresh Token after login.
-   [ ] Configure an appropriate Access Token lifetime.
-   [ ] Review Refresh Token rotation and reuse-detection policies.
-   [ ] Configure a logout/revocation policy, such as the Simple JWT blacklist app where appropriate.
-   [ ] Protect login endpoints against repeated failed attempts.
-   [ ] Send tokens in the `Authorization: Bearer <token>` header, not in URL query strings.
-   [ ] Require HTTPS in production.
-   [ ] Never write passwords, JWTs, or refresh tokens to logs.

Access Tokens are usually short-lived, while Refresh Tokens last longer. Choose lifetimes based on security and usability requirements.

## 7. Authentication and Authorization

Authentication establishes **who the requester is**. Authorization determines **what the requester may do**.

Recommended authorization layers:

1.  **Authentication** --- determine whether the request is anonymous or authenticated.
2.  **Role/group permissions** --- grant capabilities based on groups or roles.
3.  **API-level permissions** --- control access to individual endpoints and operations.
4.  **Object-level permissions** --- verify ownership or access to a specific record or organization.
5.  **Business rules** --- enforce approval flows, state transitions, and domain-specific rules.

Implementation checklist:

-   [ ] Set DRF's `DEFAULT_PERMISSION_CLASSES` explicitly.
-   [ ] Clearly distinguish public endpoints from authenticated endpoints.
-   [ ] Allow a user to belong to multiple groups when required.
-   [ ] Ensure relevant permission changes take effect on subsequent requests.
-   [ ] Invalidate permission caches when permissions change, if caching is used.
-   [ ] Filter list querysets so users only see records they may access.
-   [ ] Do not assume object-level permission checks automatically filter list results.
-   [ ] Use a deny-by-default policy.

Django's built-in user, group, and permission models may cover many needs. For complex authorization, consider a custom user model or dedicated policy layer while keeping permission rules centralized and consistent.

## 8. Structured Logging

Python's `logging` framework supports multiple levels and output handlers.

  Level        Typical use
  ------------ -------------------------------------------------------
  `DEBUG`      Detailed diagnostic information during development
  `INFO`       Normal application events
  `WARNING`    Unexpected or potentially problematic situations
  `ERROR`      A request or operation failed
  `CRITICAL`   A severe failure that may affect service availability

Recommended destinations:

-   **Console:** standard output for development and containerized deployments
-   **File:** persistent logs with rotation and retention policies
-   **Email:** notify maintainers about selected high-severity errors
-   **Database:** persist audit events or important business history

Implementation checklist:

-   [ ] Configure loggers, handlers, formatters, and levels in Django's `LOGGING` setting.
-   [ ] Use different log levels for development and production.
-   [ ] Configure file rotation and retention.
-   [ ] Limit email alerts to selected severities and prevent alert storms.
-   [ ] Store appropriate audit events in the database and define retention policies.
-   [ ] Never log passwords, JWTs, API keys, session cookies, or unnecessary personal data.
-   [ ] Add a request/correlation ID to connect requests, errors, and background tasks.
-   [ ] Sanitize untrusted input to reduce log-injection risks.
-   [ ] Ensure logging failures do not unnecessarily interrupt core API requests.

Database logging is not automatically provided by a standard Django logging setting; it requires a custom model/handler or an audit-event service. Avoid writing every low-value log line to the database because this can increase latency and storage costs.

## 9. Automatic API Documentation

Use `drf-spectacular` to generate an OpenAPI schema and provide Swagger UI and ReDoc.

-   [ ] Configure the OpenAPI schema endpoint.
-   [ ] Configure Swagger UI.
-   [ ] Configure ReDoc.
-   [ ] Verify request and response schemas generated from serializers.
-   [ ] Document JWT Bearer authentication.
-   [ ] Document status codes and error response formats.
-   [ ] Document pagination, filtering, search, and sorting parameters.
-   [ ] Decide whether production documentation requires authentication or internal network access.
-   [ ] Generate and validate the OpenAPI schema in CI.

A documentation page appearing successfully does not guarantee every endpoint is accurately described. Explicitly document complex responses, permission requirements, and error cases, and test the schema.

## 10. Database and ORM

SQLite may be convenient during early development. If PostgreSQL is planned for production, keep development and test environments as similar to production as practical.

-   [ ] Configure `DATABASES` through environment variables.
-   [ ] Generate and review migrations after model changes.
-   [ ] Define when and how migrations run during deployment.
-   [ ] Add appropriate foreign keys, unique constraints, and indexes.
-   [ ] Use `transaction.atomic()` for operations that must succeed or fail as a unit.
-   [ ] Check for N+1 query problems and use `select_related()` / `prefetch_related()` where appropriate.
-   [ ] Establish database backup, restore, and retention procedures.
-   [ ] Give database accounts only the permissions they need.
-   [ ] Never commit database passwords to source control.

## 11. REST API Conventions

-   [ ] Use resource-oriented URLs, such as `/api/v1/users/`.
-   [ ] Follow HTTP method semantics: `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`.
-   [ ] Return appropriate HTTP status codes.
-   [ ] Define an API versioning strategy.
-   [ ] Validate request data with serializers.
-   [ ] Standardize error response formats.
-   [ ] Apply pagination to list endpoints.
-   [ ] Restrict filter, search, and ordering fields to approved fields.
-   [ ] Consider idempotency for operations sensitive to duplicate requests.
-   [ ] Limit request sizes and large responses.
-   [ ] Standardize time zones and date/time formats.
-   [ ] Restrict file upload size and allowed file types.

## 12. Security

-   [ ] Load `SECRET_KEY` and database credentials from environment variables or a secrets manager.
-   [ ] Set `DEBUG = False` in production.
-   [ ] Configure `ALLOWED_HOSTS` explicitly.
-   [ ] Review HTTPS, secure cookies, and reverse-proxy settings.
-   [ ] Allow only required origins in CORS configuration.
-   [ ] Review CSRF protection when using cookie-based authentication.
-   [ ] Apply rate limits to login, password-reset, and sensitive endpoints.
-   [ ] Validate uploaded files and store them safely.
-   [ ] Review dependency updates and known vulnerabilities.
-   [ ] Never expose stack traces or secret information in client-facing errors.
-   [ ] Protect the admin site and operational documentation.
-   [ ] Audit permission changes and important actions.

## 13. Exception Handling and Responses

-   [ ] Configure a shared DRF exception handler.
-   [ ] Distinguish validation, authentication, permission, not-found, and server errors.
-   [ ] Return safe and consistent error structures to clients.
-   [ ] Record useful diagnostic details in server logs while redacting secrets.
-   [ ] Separate expected business errors from unexpected server failures.
-   [ ] Handle external process failures, timeouts, non-zero exit codes, and invalid output.

Do not expose internal file paths, SQL statements, tokens, or stack traces directly in API responses.

## 14. Testing and Code Quality

-   [ ] Write unit tests for models and business logic.
-   [ ] Write API integration tests.
-   [ ] Test JWT issuance, expiration, and refresh.
-   [ ] Test that unauthorized users and object access are denied.
-   [ ] Test filtering, pagination, and validation errors.
-   [ ] Test logging and important audit events.
-   [ ] Validate database migrations.
-   [ ] Run tests with `pytest` and `pytest-django`.
-   [ ] Run `ruff check` and `ruff format --check`.
-   [ ] Run tests and static checks automatically in CI.

Authorization tests must cover not only permitted actions but also actions that **must be denied**.

``` powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## 15. Operations and Deployment

-   [ ] Choose a WSGI or ASGI application server.
-   [ ] Configure a reverse proxy and HTTPS.
-   [ ] Configure static file collection and delivery.
-   [ ] Inject environment variables and secrets securely.
-   [ ] Define process restart and graceful shutdown behavior.
-   [ ] Provide health and readiness checks.
-   [ ] Monitor error rates, latency, CPU/memory usage, and database connections.
-   [ ] Configure log rotation, centralized collection, and retention.
-   [ ] Document migration and rollback procedures.
-   [ ] Test backup restoration regularly.
-   [ ] Define incident-response ownership and alert routes.

## 16. Extensible Features

Add these when service requirements justify them:

-   Background task queue for email, reports, and long-running jobs
-   Caching for frequently read data, with explicit invalidation rules
-   File storage for uploads and generated results
-   External executable integration with allowlists, validated arguments, timeouts, resource limits, exit-code checks, and output validation
-   Audit trails for permission changes, logins, and data changes
-   Notifications through email or operational messaging platforms
-   Observability through metrics, distributed tracing, and slow-query analysis

When launching external programs, do not concatenate user input into shell command strings. Prefer passing an argument list, and enforce allowlists and timeouts.

## 17. Suggested Implementation Order

-   [ ] Establish the `src/ahaapi/config/` layout and split development/production settings.
-   [ ] Verify package configuration and Python import paths.
-   [ ] Configure PostgreSQL and migrations.
-   [ ] Implement the user model and JWT authentication.
-   [ ] Design group, role, and object-level authorization.
-   [ ] Add shared serializers, exception handling, and pagination.
-   [ ] Configure OpenAPI documentation.
-   [ ] Start with console/file logging, then add email alerts and database audit logging.
-   [ ] Automate tests and Ruff checks.
-   [ ] Configure security and production deployment.
-   [ ] Validate monitoring, backups, and incident-response procedures.

## References

-   Django: https://www.djangoproject.com/
-   Django documentation: https://docs.djangoproject.com/
-   Django REST Framework: https://www.django-rest-framework.org/
-   Simple JWT: https://django-rest-framework-simplejwt.readthedocs.io/
-   drf-spectacular: https://drf-spectacular.readthedocs.io/
-   django-filter: https://django-filter.readthedocs.io/
-   uv: https://docs.astral.sh/uv/
-   pytest-django: https://pytest-django.readthedocs.io/
-   Ruff: https://docs.astral.sh/ruff/
