# IKF Django Docker Workflow

This document records the agreed Docker workflow for the IKF Django application.

## Target stack

- Host: Ubuntu 24.04 LTS
- Python: latest patch release in the Python 3.12 series
- Django: 5.2.16 LTS
- Database: external MySQL 8.4 LTS
- Application server: Gunicorn
- Reverse proxy: Nginx on the host
- Container management: Docker Compose

## Core design

The project uses one Dockerfile with separate development and production Compose behavior.

### Development

- The Git repository stays on the WSL host.
- `./ikf` is bind-mounted at `/app` inside the container.
- Django's development server is used.
- Source changes are visible without rebuilding the image.
- Migration files generated in the container persist in the host Git repository.

### Production

- Application code is copied into an immutable Docker image.
- No Git repository or source-code bind mount is used in the container.
- Gunicorn serves the Django WSGI application.
- MySQL remains outside Docker.
- Secrets are supplied through environment variables.
- Media and collected static files use persistent storage.

## Planned repository layout

```text
football/
|-- Dockerfile
|-- compose.yaml
|-- compose.dev.yaml
|-- .dockerignore
|-- .env                   # local only; never commit
|-- requirements-py312.txt
`-- ikf/
    |-- manage.py
    |-- main/
    |-- internal/
    `-- ikf/
```

## Local WSL workflow

Start the development environment:

```bash
docker compose -f compose.yaml -f compose.dev.yaml up --build
```

After code-only changes or a Git pull, the bind mount makes the new code available to the container. Restart the web service if necessary:

```bash
git pull --ff-only
docker compose -f compose.yaml -f compose.dev.yaml restart web
```

If `requirements-py312.txt`, the Dockerfile, or system dependencies change, rebuild:

```bash
git pull --ff-only
docker compose -f compose.yaml -f compose.dev.yaml up -d --build
```

## Django management commands

Run management commands inside the container so they use the same Python and dependency versions as the application.

During development:

```bash
docker compose -f compose.yaml -f compose.dev.yaml exec web python manage.py check
docker compose -f compose.yaml -f compose.dev.yaml exec web python manage.py makemigrations main
docker compose -f compose.yaml -f compose.dev.yaml exec web python manage.py migrate
docker compose -f compose.yaml -f compose.dev.yaml exec web python manage.py collectstatic --noinput
```

`makemigrations` is a development operation. Generated migration files must be reviewed and committed to Git.

Production must never generate migrations. It only applies committed migrations:

```bash
docker compose run --rm web python manage.py check --deploy
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py collectstatic --noinput
docker compose up -d
```

## Deployment flow

The portable deployment artifact is the Docker image, not a running container and not the Git directory.

```text
Git source
    -> build and test image
    -> push image to registry (or export it)
    -> production pulls image
    -> migrations and collectstatic run
    -> web container is replaced
```

The eventual production update commands are:

```bash
docker compose pull
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py collectstatic --noinput
docker compose up -d
```

Until a registry/CI pipeline is configured, the build machine may use:

```bash
git pull --ff-only
docker compose build web
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py collectstatic --noinput
docker compose up -d --no-deps web
```

## Persistent and external state

The following must not depend on a container's writable layer:

- MySQL databases
- uploaded media
- collected static files served by host Nginx
- secrets and environment configuration
- backups and logs that must survive container replacement

Replacing or rebuilding the web container must not delete database records or uploaded files.

## Locked decisions

1. Git will not run inside production containers.
2. Production application code will be contained in an immutable image.
3. Development will use a source bind mount for fast iteration.
4. Dependency changes require an image rebuild.
5. `makemigrations` runs only in development.
6. Production runs only committed migrations.
7. MySQL 8.4 remains external to Docker.
8. Nginx remains on the host and proxies to Gunicorn in Docker.
9. `.env` files and credentials will not be copied into images or committed.
10. Docker and compatibility testing will be completed before production deployment work.

## Command helper

Routine operations are wrapped by `ikfctl`. Run `./ikfctl help` to see all
commands. The common workflow is:

```bash
./ikfctl init
# Edit .env once.
./ikfctl setup
./ikfctl makemigrations main
./ikfctl migrate
./ikfctl logs
```

`./ikfctl setup` performs the repetitive non-destructive preparation in one
command: it builds and starts the development container, reports Python and
Django versions, checks installed dependencies, runs Django system checks,
verifies the default MySQL connection, and prints container status. Migration
generation, schema changes, data import, and administrator creation remain
explicit commands because they modify persistent state.

If application dependencies change:

```bash
./ikfctl update
```

Production deployment uses:

```bash
./ikfctl deploy
```

## CI/CD

`.github/workflows/ci.yml` performs the following for pull requests and pushes:

1. Builds the production Docker image.
2. Verifies installed Python dependencies.
3. Compiles the Python source.
4. Runs Django system checks.
5. On `main`, publishes the verified image to GitHub Container Registry as both
   the commit SHA and `latest`.

`.github/workflows/deploy.yml` is a manually triggered, production-environment
protected deployment. It copies only the Compose definition and command helper
to the server, then deploys the chosen image tag.

Configure these GitHub production-environment secrets before using deployment:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_KNOWN_HOSTS`

Configure the production-environment variable `DEPLOY_PATH`, for example
`/opt/ikf/football`. The target directory must already contain a production
`.env`, and Docker must already be authenticated to GHCR if the image package is
private.
