# IKF Day-to-Day Deployment Guide

This guide explains exactly what to do after changing the IKF application. It
covers work in local WSL, the automatic GitHub image build, and deployment on
production.

Use this guide for routine updates after the initial server setup is complete.
For rebuilding a server from scratch, use `PRODUCTION_DEPLOYMENT.md` instead.

## How deployment works

```text
Local WSL
  -> test the change
  -> commit and push to GitHub
  -> GitHub Actions builds and validates a private Docker image
  -> GHCR stores the verified image
  -> production pulls the image
  -> production checks, migrates, collects static, and replaces the container
```

The production server does not pull application source with Git. Application
source and Python dependencies arrive inside the immutable Docker image.

The following are outside the image and survive every deployment:

- MySQL databases
- uploaded media in `docker-data/media`
- collected static files in `docker-data/static`
- production `.env`
- Nginx and TLS configuration

## Important locations

Local WSL repository:

```text
/home/indiakhelofootball/football
```

Production deployment directory:

```text
/opt/ikf/football
```

Production image:

```text
ghcr.io/shanukarn11/football
```

## Decide which workflow applies

Use one of these workflows:

| Change | Rebuild image? | Migration required? | Collect static? |
|---|---:|---:|---:|
| Python, template, URL, view, form, admin, or settings code | Yes | No | Automatically run during deploy |
| `models.py` | Yes | Yes | Automatically run during deploy |
| `requirements-py312.txt` or Dockerfile | Yes, including dependencies | Only if models also changed | Automatically run during deploy |
| CSS, JavaScript, image, or other tracked static source | Yes | No | Automatically run during deploy |
| Content edited in Django admin | No | No | No deployment required |
| User-uploaded media | No | No | No deployment required |
| Production `.env` only | No image rebuild | No | Recreate the web container |

## Workflow A: code-only change

Examples:

- `views.py`
- `urls.py`
- templates
- forms
- admin code
- application Python code
- tracked CSS or JavaScript

### A1. Update local WSL first

```bash
cd /home/indiakhelofootball/football
git pull --ff-only
```

Do this before editing when possible. It reduces merge conflicts.

### A2. Start the local development environment

For a normal code change with unchanged dependencies:

```bash
./ikfctl start
```

The development Compose configuration bind-mounts the WSL `ikf` source folder.
Python and template changes normally appear without rebuilding the image.
Django's development server reloads Python changes automatically.

If the development image does not exist yet, or Docker configuration changed:

```bash
./ikfctl dev
```

### A3. Validate locally

```bash
./ikfctl check
./ikfctl test
```

Also open the affected page locally and exercise the changed behavior. Check
the development logs when the change affects requests, uploads, payments,
email, or database queries:

```bash
./ikfctl logs
```

Press `Ctrl+C` to stop following logs; this does not stop the container.

### A4. Review what Git will commit

```bash
git status --short
git diff
```

Do not commit:

- `.env`
- database dumps
- `docker-data/`
- uploaded media
- passwords, tokens, certificates, or private keys
- cache files or logs

Stage only the intended files. For example:

```bash
git add ikf/main/views.py ikf/main/templates/
```

Then review the staged change:

```bash
git diff --cached
```

### A5. Commit and push

```bash
git commit -m "Describe the code change"
git push
```

### A6. Wait for the image build

Open the repository's GitHub Actions page and wait for the newest
**Build and validate IKF** run to finish with a green check.

The workflow must complete these important stages:

- Build test image
- Verify installed dependencies
- Compile Python source
- Run Django system checks
- Log in to GitHub Container Registry
- Publish verified image

Do not deploy a red, cancelled, queued, or still-running workflow.

### A7. Deploy on production

SSH into production, then:

```bash
su - ikfdeploy
cd /opt/ikf/football
./ikfctl deploy
```

The production command pulls the verified image, runs deployment checks,
applies any committed migrations, collects static files, and replaces the web
container.

### A8. Verify production

```bash
docker compose ps
docker compose logs --tail=100 web
curl -I https://indiakhelofootball.com/
```

Expected results:

- container status includes `(healthy)`
- no traceback or HTTP 500 in logs
- domain returns HTTP 200 or an intentional redirect

Open the affected page in a browser and test the actual changed behavior.

## Workflow B: model change

Use this workflow whenever `models.py` changes, including new fields, changed
field lengths, new indexes, relationships, constraints, or deleted models.

### B1. Update and start WSL

```bash
cd /home/indiakhelofootball/football
git pull --ff-only
./ikfctl start
```

### B2. Edit `models.py`

Make the required model change. Check MySQL compatibility while editing:

- MySQL decimal precision cannot exceed 65.
- Avoid indexing very large character fields.
- Use `TextField` for long content that does not need an index.
- Be cautious when making an existing nullable field required.
- Plan data migration when changing the meaning or format of existing data.

### B3. Generate the migration locally

```bash
./ikfctl makemigrations main
```

Production must never run `makemigrations`.

### B4. Review the generated migration

```bash
git status --short ikf/main/migrations
git diff -- ikf/main/models.py ikf/main/migrations
```

Confirm the migration contains only the intended schema operations. Do not
delete an already deployed migration. Create a new migration for every later
schema change.

### B5. Review the migration plan

```bash
./ikfctl migrate --plan
```

The command must say `Planned operations`. It must not unexpectedly apply
migrations.

### B6. Apply locally

Back up important local data first if the migration is destructive. Then run:

```bash
./ikfctl migrate --noinput
./ikfctl check
./ikfctl test
```

Test create, read, update, and delete behavior for the affected model through
the application or Django admin.

### B7. Commit model and migration together

```bash
git add ikf/main/models.py ikf/main/migrations/
git diff --cached
git commit -m "Describe the model and migration change"
git push
```

Never commit only `models.py` while forgetting its migration.

### B8. Wait for green CI

Do not deploy until **Build and validate IKF** is green and the image has been
published to GHCR.

### B9. Back up production before risky migrations

For additive, low-risk migrations such as adding a nullable field, routine
database backups may be sufficient. Before deleting fields/tables, changing
types, adding strict constraints, or transforming important data, take a fresh
database backup and verify its location and size.

Example structure, with a protected backup directory:

```bash
mysqldump -u root -p --single-transaction --routines --triggers \
  indiakhelofootball > /PROTECTED_BACKUP_PATH/indiakhelofootball-before-change.sql
```

Never put a production backup in Git or a publicly served directory.

### B10. Deploy and verify

```bash
su - ikfdeploy
cd /opt/ikf/football
./ikfctl deploy
docker compose ps
docker compose logs --tail=100 web
```

Verify the changed model and admin/page behavior in production.

## Workflow C: requirements or Docker change

Use this workflow after changing:

- `requirements-py312.txt`
- `Dockerfile`
- system libraries required by Python packages
- the Python base image
- Gunicorn configuration in the image

### C1. Update local WSL

```bash
cd /home/indiakhelofootball/football
git pull --ff-only
```

### C2. Edit the dependency definition

Application dependencies belong in `requirements-py312.txt`. Do not replace it
with an unreviewed full-server `pip freeze` output.

Use compatible ranges deliberately. Keep Django on the agreed 5.2 LTS line
until a separately tested framework upgrade is planned.

### C3. Rebuild locally

Dependency or Dockerfile changes require a rebuild:

```bash
./ikfctl dev
```

The first build can take several minutes. Docker should cache unchanged layers
on later builds.

### C4. Run full compatibility verification

```bash
./ikfctl verify
./ikfctl test
```

The verification must confirm:

- expected Python 3.12 version
- expected Django version
- no broken Python requirements
- no Django system-check errors
- successful MySQL 8.4 connection

Exercise application areas that use the changed package. Examples include
image upload for Pillow, spreadsheets for pandas/openpyxl, payment operations
for Razorpay, and MySQL queries for mysqlclient.

### C5. Review, commit, and push

```bash
git status --short
git diff -- requirements-py312.txt Dockerfile
git add requirements-py312.txt Dockerfile
git diff --cached
git commit -m "Describe the dependency change"
git push
```

Stage only files that actually changed.

### C6. Wait for green CI and deploy

CI performs a clean production-image build and `pip check`. After it is green:

```bash
su - ikfdeploy
cd /opt/ikf/football
./ikfctl deploy
```

Then verify health, logs, and the feature that uses the dependency.

## Workflow D: production `.env` change

Examples:

- rotating Razorpay credentials
- rotating email credentials
- changing an API key
- changing an allowed hostname
- changing a non-code security setting

No image rebuild is required when the application already knows the environment
variable.

On production:

```bash
su - ikfdeploy
cd /opt/ikf/football
nano .env
docker compose config --quiet
docker compose up -d --no-deps --force-recreate web
docker compose ps
docker compose logs --tail=100 web
```

Never display or paste the full production `.env`. If a credential is exposed,
rotate it rather than merely deleting the message or terminal output.

## Workflow E: admin content or uploaded media

Content changes made through Django admin write directly to MySQL. Uploaded
files write to persistent media storage. They do not require a code deployment
or image rebuild.

After important content changes, ensure database and media backups remain
current.

## What `./ikfctl deploy` does

The production command performs the routine deployment sequence:

```text
pull verified image
  -> Django check --deploy
  -> migrate --noinput
  -> collectstatic --noinput
  -> recreate/start web
  -> show service status
```

It does not:

- run `makemigrations`
- import an old database dump
- replace `.env`
- delete media
- place Git source inside the container
- modify Nginx or MySQL configuration

## Production verification checklist

Run after every deployment:

```bash
cd /opt/ikf/football
docker compose ps
docker compose logs --tail=100 web
curl -I https://indiakhelofootball.com/
curl -I https://indiakhelofootball.com/static/admin/css/base.css
```

For changes that affect media paths, also check a known media URL.

Confirm:

- GitHub Actions was green.
- The expected image was pulled.
- Migrations completed successfully.
- Static collection completed successfully.
- Container is healthy.
- No traceback or 500 appears in logs.
- Homepage and changed feature work through Cloudflare HTTPS.
- Admin login and forms do not have CSRF errors.

## Rollback

The safest rollback uses a previously verified commit SHA image tag.

### Find the previous image tag

GitHub Actions publishes images using both `latest` and the full Git commit SHA.
Identify the last known-good SHA from GitHub.

### Deploy the previous tag temporarily

```bash
su - ikfdeploy
cd /opt/ikf/football
IKF_IMAGE=ghcr.io/shanukarn11/football:FULL_COMMIT_SHA ./ikfctl deploy
```

Then verify:

```bash
docker compose ps
docker compose logs --tail=100 web
curl -I https://indiakhelofootball.com/
```

Important: rolling back an image does not reverse database migrations. Do not
roll back across an incompatible schema change without a specific database
rollback plan.

## If a deployment fails

### CI is red

Do not deploy. Open the first failed GitHub Actions step and fix the first real
error. Later failures are often consequences of the first one.

### Image pull fails

Verify the production user is authenticated to private GHCR and its classic
token has only `read:packages`:

```bash
docker login ghcr.io -u shanukarn11
```

Never paste the token into chat or commit it.

### Migration fails

Do not rerun blindly if MySQL partially created or changed schema. Capture the
first error, inspect migration state, and restore from backup if the operation
was destructive.

### Container is unhealthy

```bash
docker compose ps
docker compose logs --tail=200 web
```

Check the first traceback and verify database connectivity, environment values,
and migration status.

### Website shows 502

Confirm Gunicorn is healthy on localhost:

```bash
curl -I -H "Host: indiakhelofootball.com" http://127.0.0.1:8000/
```

Then validate Nginx:

```bash
nginx -t
systemctl status nginx
```

## Recommended normal release habit

For each release:

1. Pull before editing.
2. Make one focused change.
3. Test it in WSL.
4. Review `git diff`.
5. Commit migrations with model changes.
6. Push to GitHub.
7. Wait for green CI.
8. Back up production before risky schema changes.
9. Run `./ikfctl deploy` as `ikfdeploy`.
10. Verify health, logs, HTTPS, and the changed feature.

Do not deploy directly from uncommitted files, use `sudo git`, run Git inside a
container, generate migrations on production, or store persistent data inside
the image.
