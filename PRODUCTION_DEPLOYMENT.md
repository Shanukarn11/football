# IKF Production Deployment Runbook

This runbook documents the production deployment of India Khelo Football. It is
intended to make future server rebuilds, deployments, verification, and rollback
repeatable without relying on shell history.

Never place real passwords, API keys, email credentials, TLS private keys, or
GitHub tokens in this document or in Git.

## Target architecture

```text
Visitor
  -> Cloudflare
  -> HTTPS on host Nginx
  -> http://127.0.0.1:8000
  -> Django/Gunicorn container
  -> host MySQL 8.4
```

- Host OS: Ubuntu 24.04 LTS, x86_64
- Python: 3.12 inside the image
- Django: 5.2 LTS
- Database: MySQL 8.4 LTS on the host
- Application: Gunicorn inside Docker
- Reverse proxy and static/media server: Nginx on the host
- Image registry: private GitHub Container Registry (GHCR)
- Production directory: `/opt/ikf/football`
- Persistent static files: `/opt/ikf/football/docker-data/static`
- Persistent media files: `/opt/ikf/football/docker-data/media`

Application source is built into an immutable image. The production directory
does not require a Git checkout.

## Deployment completion record

The first production deployment completed successfully with the following
verified results:

- Ubuntu 24.04 LTS host
- MySQL 8.4 listening only on loopback and Docker's host bridge
- UFW enabled with public access limited to SSH, HTTP, and HTTPS
- private GHCR image pulled successfully
- Django migrations applied successfully
- legacy SQL data imported successfully
- 225 database tables present
- 19 migration records present at initial import time
- one `DonateSettings` singleton row present
- approximately 1.6 GB of legacy media synchronized into persistent storage
- static files collected into persistent storage
- Gunicorn container reported healthy
- Nginx returned HTTP 200 for application, static, and media requests
- fresh Let's Encrypt certificate issued for the apex and `www` hostnames
- simulated certificate renewal succeeded through Cloudflare DNS validation
- Django `check --deploy` completed without security warnings after HTTPS
  hardening
- Cloudflare proxy enabled and the public site brought live

Record the actual deployment date, deployed commit SHA, image digest, database
backup identifier, and operator in a private change log. Do not put credentials
in Git.

## Services managed by systemd

Nginx, MySQL, and Docker are host services:

```bash
systemctl status nginx
systemctl status mysql
systemctl status docker
```

The Django container is managed by Docker Compose and uses
`restart: unless-stopped`. A separate Gunicorn systemd service and Unix socket
are not used.

## Initial server audit

Run these read-only checks before changing a new server:

```bash
whoami
cat /etc/os-release
uname -m
free -h
df -h /
systemctl is-active nginx
systemctl is-active mysql
systemctl is-active docker
nginx -v
mysql --version
docker --version
docker compose version
ss -lntp
```

Confirm that ports 22, 80, and 443 are intended to be public. MySQL must not be
publicly reachable.

## Host firewall

The production firewall permits only SSH, HTTP, and HTTPS from the Internet:

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status verbose
```

Do not add a public rule for ports 3306 or 33060.

After Compose creates its private network, allow only that subnet to connect to
MySQL. Inspect the subnet rather than assuming it:

```bash
docker network inspect football_default --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}'
```

For the current deployment the subnet is `172.18.0.0/16`, Docker's host bridge
is `172.17.0.1`, and the rule is:

```bash
ufw allow from 172.18.0.0/16 to 172.17.0.1 port 3306 proto tcp comment 'IKF Docker to MySQL'
```

If Docker assigns a different subnet during a server rebuild, use the reported
subnet and update the rule accordingly.

## MySQL network restriction

MySQL listens only on loopback and Docker's host bridge. Create:

`/etc/mysql/mysql.conf.d/99-ikf-network.cnf`

with:

```ini
[mysqld]
bind-address = 127.0.0.1,172.17.0.1
mysqlx-bind-address = 127.0.0.1
```

Validate and restart:

```bash
mysqld --validate-config
systemctl restart mysql
systemctl is-active mysql
ss -lntp | grep -E ':(3306|33060)\b'
```

Expected listeners:

- `3306` on `127.0.0.1` and `172.17.0.1`
- `33060` on `127.0.0.1` only

## Databases and accounts

Create two UTF-8 databases:

- `indiakhelofootball`
- `latmfks`

Use `utf8mb4` with `utf8mb4_0900_ai_ci`. Application accounts need a
`172.%` host entry for Docker. A `localhost` entry is optional for host-side
imports. Grant privileges only on the matching database, never globally.

Example structure with placeholders:

```sql
CREATE DATABASE IF NOT EXISTS `DATABASE_NAME`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS 'APP_USER'@'172.%'
  IDENTIFIED WITH caching_sha2_password BY 'PRIVATE_PASSWORD';
GRANT ALL PRIVILEGES ON `DATABASE_NAME`.* TO 'APP_USER'@'172.%';
```

Do not record production passwords in this runbook.

## Deployment user and directories

Routine deployments use `ikfdeploy`, not `root`:

```bash
adduser --disabled-password --gecos "" ikfdeploy
usermod -aG docker ikfdeploy
install -d -o ikfdeploy -g www-data -m 2750 /opt/ikf
install -d -o ikfdeploy -g www-data -m 2750 /opt/ikf/football
install -d -o ikfdeploy -g www-data -m 2750 /opt/ikf/football/docker-data/static
install -d -o ikfdeploy -g www-data -m 2750 /opt/ikf/football/docker-data/media
```

Verify:

```bash
id ikfdeploy
ls -ld /opt/ikf /opt/ikf/football /opt/ikf/football/docker-data/*
```

The directories should be owned by `ikfdeploy:www-data` with mode `2750`.
The set-group-ID bit makes newly created files inherit the `www-data` group so
Nginx can read static and media files.

Membership in the Docker group is privileged. Protect the deployment user's SSH
private key and do not enable password login for this account.

## Building and publishing the image

GitHub Actions builds the Docker image from `main`, validates dependencies,
compiles the Django runtime modules, runs Django system checks, and publishes:

```text
ghcr.io/shanukarn11/football:<commit-sha>
ghcr.io/shanukarn11/football:latest
```

The GHCR package should remain private. Production uses a classic GitHub token
with only `read:packages`. Never grant `repo`, `write:packages`, or
`delete:packages` to the production pull token.

Authenticate as `ikfdeploy` without putting the token in shell history:

```bash
read -rsp "GHCR token: " GHCR_TOKEN
printf '%s' "$GHCR_TOKEN" | docker login ghcr.io -u GITHUB_USERNAME --password-stdin
unset GHCR_TOKEN
```

Verify image access:

```bash
docker pull ghcr.io/shanukarn11/football:latest
```

For repeatable releases, prefer deploying the immutable commit SHA tag rather
than `latest`.

## Production deployment files

Only these deployment files are required in `/opt/ikf/football`:

- `compose.yaml`
- `ikfctl`
- `.env`
- `docker-data/static/`
- `docker-data/media/`

The production `.env` must be mode `600`, owned by `ikfdeploy`, and never
committed:

```bash
touch /opt/ikf/football/.env
chmod 600 /opt/ikf/football/.env
```

Important production values include:

```dotenv
DEBUG=False
APP_ALLOWED_URL=indiakhelofootball.com
CSRF_TRUSTED_ORIGINS=https://indiakhelofootball.com,https://www.indiakhelofootball.com
DB_HOST=host.docker.internal
LAT_DB_HOST=host.docker.internal
IKF_IMAGE=ghcr.io/shanukarn11/football:COMMIT_SHA_OR_APPROVED_TAG
```

Keep HTTPS redirect, secure cookies, and HSTS disabled until Nginx HTTPS is
working. Enable them in the HTTPS hardening phase below.

Validate Compose without printing secrets:

```bash
cd /opt/ikf/football
docker compose -f compose.yaml config --quiet
```

## Database connectivity test

Test from the same production image and network used by the application:

```bash
docker compose -f compose.yaml run --rm --no-deps web \
  python manage.py shell -c \
  "from django.db import connection; connection.ensure_connection(); print(connection.mysql_version, connection.settings_dict['NAME'])"
```

Expected database version is MySQL 8.4 and the database name should be
`indiakhelofootball`.

## Deployment sequence

After the database connection succeeds:

```bash
cd /opt/ikf/football
docker compose pull web
docker compose run --rm --no-deps web python manage.py check --deploy
docker compose run --rm --no-deps web python manage.py migrate --noinput
docker compose run --rm --no-deps web python manage.py collectstatic --noinput
docker compose up -d --no-deps web
docker compose ps
docker compose logs --tail=100 web
```

Production never runs `makemigrations`. Migrations must be generated, reviewed,
committed, and built into the image before deployment.

## Persistent data import

Database dumps and media files are not part of the Docker image. They are
one-time state transfers during a server rebuild.

### Correct first-import order

Use this order on a new, empty database:

```text
pull image
  -> migrate schema
  -> confirm permanent web service is stopped
  -> import legacy rows
  -> validate counts
  -> synchronize media
  -> collect static
  -> start web
```

Do not start the website before importing legacy rows. Some application code,
such as `DonateSettings.load()`, can create singleton records when a page is
requested. Starting early caused a duplicate primary-key error during testing.

### Extracting the legacy data dump

The supplied `insert_data.sql` was actually a ZIP archive containing a SQL file
with the same name. Verify before import:

```bash
file insert_data.sql
unzip -l insert_data.sql
```

Extract to a different filename so the archive is not overwritten:

```bash
unzip -p insert_data.sql insert_data.sql > insert_data_extracted.sql
```

Import only after migrations succeed and the permanent web service is stopped:

```bash
mysql -u DATABASE_USER -p DATABASE_NAME < insert_data_extracted.sql
```

Successful `mysql` import normally returns to the prompt without output. If an
error occurs, do not simply rerun the dump: the database may contain a partial
import. Diagnose the first error and recreate or restore the database when
appropriate.

### Database validation after import

The first deployment used:

```bash
mysql -u DATABASE_USER -p DATABASE_NAME -e \
  "SELECT COUNT(*) AS total_tables FROM information_schema.tables WHERE table_schema='DATABASE_NAME' AND table_type='BASE TABLE'; SELECT COUNT(*) AS donate_settings_rows FROM main_donatesettings; SELECT COUNT(*) AS migration_records FROM django_migrations;"
```

The observed initial results were:

- 225 base tables
- one `main_donatesettings` row
- 19 migration records

These are historical baseline values, not permanent invariants. Later releases
can legitimately add tables and migration records.

### Media path preservation

Django file fields store paths relative to `MEDIA_ROOT`. Preserve those paths
exactly. The legacy data included both forms:

```text
home/hero/characters/example.png
media/ui/Team2/example.jpeg
```

Therefore persistent storage can legitimately contain both:

```text
docker-data/media/home/...
docker-data/media/media/ui/...
```

Do not "clean up" the repeated `media/media` appearance without also migrating
the corresponding database values.

The first deployment uploaded media into a temporary
`/opt/ikf/football/media` directory and then merged it safely:

```bash
rsync -a --no-owner --no-group --info=progress2 \
  /opt/ikf/football/media/ \
  /opt/ikf/football/docker-data/media/
```

Verify known files and total size before deleting the temporary source:

```bash
du -sh /opt/ikf/football/docker-data/media
find /opt/ikf/football/docker-data/media -type f -iname 'KNOWN_FILENAME' -print
```

Back up both MySQL databases and `docker-data/media` before every material
production migration.

## Final Nginx configuration

Nginx runs on the host. Gunicorn is not managed by systemd and no Unix socket
is used. Docker publishes Gunicorn only on `127.0.0.1:8000`.

The active site file is:

```text
/etc/nginx/sites-available/ikf
```

enabled by:

```text
/etc/nginx/sites-enabled/ikf
```

The working configuration is:

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name indiakhelofootball.com www.indiakhelofootball.com;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name indiakhelofootball.com www.indiakhelofootball.com;

    ssl_certificate /etc/letsencrypt/live/indiakhelofootball.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/indiakhelofootball.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_timeout 1d;
    ssl_session_cache shared:IKFSSL:10m;
    ssl_session_tickets off;

    client_max_body_size 16M;

    location ^~ /static/ {
        alias /opt/ikf/football/docker-data/static/;
        access_log off;
        expires 7d;
        add_header Cache-Control "public";
        add_header X-Content-Type-Options "nosniff";
    }

    location ^~ /media/ {
        alias /opt/ikf/football/docker-data/media/;
        access_log off;
        expires 7d;
        add_header Cache-Control "public";
        add_header X-Content-Type-Options "nosniff";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 10s;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }
}
```

Directory listing is disabled. The legacy `autoindex on` configuration is not
used for public media.

Validate before every reload:

```bash
nginx -t
systemctl reload nginx
```

Never reload after a failed `nginx -t`.

### Nginx verification without public DNS

Test locally with the intended host header:

```bash
curl -I -H "Host: indiakhelofootball.com" http://127.0.0.1/
```

Test the real certificate before DNS cutover:

```bash
curl -I --resolve indiakhelofootball.com:443:127.0.0.1 \
  https://indiakhelofootball.com/
```

Test static and media through Nginx, not Gunicorn:

```bash
curl -I --resolve indiakhelofootball.com:443:127.0.0.1 \
  https://indiakhelofootball.com/static/admin/css/base.css
curl -I --resolve indiakhelofootball.com:443:127.0.0.1 \
  https://indiakhelofootball.com/media/KNOWN_MEDIA_PATH
```

Expected response is HTTP 200 with `Server: nginx`.

## TLS certificate and automatic renewal

The old server's certificate was not copied because it covered only the apex
hostname and was near expiry. A fresh Let's Encrypt certificate was issued for:

```text
indiakhelofootball.com
www.indiakhelofootball.com
```

DNS validation allowed certificate issuance before public DNS moved to the new
server, avoiding downtime.

Install Certbot and its Cloudflare DNS plugin:

```bash
apt install -y certbot python3-certbot-nginx
apt install -y python3-certbot-dns-cloudflare
```

Create a Cloudflare API token with only:

```text
Zone -> DNS -> Edit
Resource -> Specific zone -> indiakhelofootball.com
```

Store it outside the deployment directory:

```text
/root/.secrets/certbot/cloudflare.ini
```

with mode `600` and content shaped like:

```ini
dns_cloudflare_api_token = PRIVATE_TOKEN
```

Issue the certificate:

```bash
certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials /root/.secrets/certbot/cloudflare.ini \
  --dns-cloudflare-propagation-seconds 30 \
  -d indiakhelofootball.com \
  -d www.indiakhelofootball.com
```

Verify names and expiry:

```bash
openssl x509 \
  -in /etc/letsencrypt/live/indiakhelofootball.com/fullchain.pem \
  -noout -dates -ext subjectAltName
```

Verify the renewal path:

```bash
certbot renew --dry-run
```

The first deployment completed a successful simulated DNS renewal.

### Reload Nginx after future renewals

Because the certificate was obtained with `certonly` and a DNS authenticator,
install an explicit deploy hook so Nginx loads renewed certificates:

```bash
install -d -m 755 /etc/letsencrypt/renewal-hooks/deploy
printf '%s\n' '#!/usr/bin/env bash' 'set -e' 'nginx -t' 'systemctl reload nginx' \
  > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx
chmod 750 /etc/letsencrypt/renewal-hooks/deploy/reload-nginx
```

Then test renewal again:

```bash
certbot renew --dry-run
```

Do not delete `/root/.secrets/certbot/cloudflare.ini`; automatic DNS renewal
depends on it. Rotate the Cloudflare token if it is exposed.

## Cloudflare cutover

The safe cutover sequence is:

1. Finish MySQL, Docker, data, media, static, Nginx, and certificate work on the
   new server while DNS still points to the old server.
2. Test HTTPS locally with `curl --resolve`.
3. Enable Django secure settings and pass `check --deploy`.
4. Change only the apex `A` record to the new server IP.
5. Keep `www` as a CNAME to the apex.
6. Enable the Cloudflare proxy.
7. Set SSL/TLS encryption mode to **Full (strict)**.
8. Verify both public hostnames.
9. Keep the old server available during DNS/cache transition.

Do not use Cloudflare Flexible mode. It breaks end-to-end HTTPS assumptions and
can cause redirect loops when Django enforces HTTPS.

When the proxy is active, public DNS returns Cloudflare addresses rather than
the origin IP. That is expected.

Public verification:

```bash
curl -I https://indiakhelofootball.com/
curl -I https://www.indiakhelofootball.com/
```

Expected public responses come through Cloudflare and reach the new Nginx
origin without 521, 522, or 526 errors.

## HTTPS hardening

Only after HTTPS works correctly through Cloudflare and directly at the origin,
set:

```dotenv
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=3600
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
```

Start HSTS at one hour. Increase it only after sustained verification. Do not
enable preload during the initial deployment.

Recreate the container after changing `.env`:

```bash
docker compose up -d --force-recreate web
```

Then run:

```bash
docker compose run --rm --no-deps web python manage.py check --deploy
```

## Health checks

```bash
docker compose ps
curl -I -H "Host: indiakhelofootball.com" http://127.0.0.1:8000/
docker compose logs --tail=100 web
nginx -t
curl -I https://indiakhelofootball.com/
curl -I https://www.indiakhelofootball.com/
```

Expected container status is `healthy`; HTTP should return 200 or an intentional
redirect, and logs must contain no traceback or HTTP 500 error.

Also verify:

```bash
systemctl is-active nginx
systemctl is-active mysql
systemctl is-active docker
ufw status verbose
certbot renew --dry-run
```

Test a real admin login, a CSRF-protected form, a known static asset, and known
media URLs after cutover.

## Problems encountered and resolutions

### Fresh migration initially contained an invalid decimal precision

**Observed:** MySQL rejected `DecimalField(max_digits=200,
decimal_places=2)` with error 1426 because MySQL permits a maximum decimal
precision of 65.

**Resolution:** Change the price field to a practical precision of 12 with two
decimal places, delete the not-yet-deployed stale `0001_initial.py`, regenerate
the initial migration from corrected models, and recreate the empty test
database before retrying.

Once a migration has been deployed to production, do not delete or rewrite it;
create a new migration instead.

### Oversized indexed character fields exceeded MySQL's key limit

**Observed:** MySQL error 1071 reported that the requested key exceeded the
3072-byte maximum.

**Cause:** Two content fields used `CharField(max_length=10000,
db_index=True)`. A full utf8mb4 index on such a field is not valid or useful.

**Resolution:** Convert long, non-search-key content to `TextField` and remove
the database index, then regenerate the not-yet-deployed initial migration and
retry against a clean test database.

### MySQL DDL failure left a partial test schema

**Observed:** Django system migrations succeeded before `main.0001_initial`
failed. MySQL schema operations are not fully transactional, so retrying against
the same database could encounter existing tables.

**Resolution:** During pre-production testing only, drop and recreate the known
empty test database, regenerate the corrected initial migration, and migrate
again. Never use this reset procedure on a populated production database.

### `ikfctl migrate --plan` originally applied migrations

**Observed:** The helper discarded extra arguments, so `--plan` never reached
Django and the command executed a real migration.

**Resolution:** Forward `"$@"` in the `migrate` branch of `ikfctl`. Confirm a
plan command prints `Planned operations` and does not print `Applying ... OK`.

### Migration package marker had the wrong filename

**Observed:** A file was accidentally created as `**init**.py` rather than
Python's required `__init__.py`.

**Resolution:** Rename it exactly to:

```text
ikf/main/migrations/__init__.py
```

Commit both `__init__.py` and generated migration files. Ignore only migration
cache files, not migration source.

### MySQL was publicly listening

**Observed:** MySQL listened on `*:3306` and `*:33060`, while UFW was inactive.

**Resolution:** Enable UFW, expose only 22/80/443 publicly, bind classic MySQL to
`127.0.0.1,172.17.0.1`, and bind MySQL X to `127.0.0.1`.

### Docker-to-MySQL connection hung

**Observed:** Django printed its shell startup message and then waited
indefinitely during `connection.ensure_connection()`.

**Cause:** UFW correctly blocked the new Compose subnet after the firewall was
enabled.

**Resolution:** Inspect `football_default`, identify `172.18.0.0/16`, and allow
only that subnet to reach `172.17.0.1:3306`. Do not open 3306 publicly.

### Deployment directory ownership was wrong

**Observed:** Some directories were created as `root:root` rather than
`ikfdeploy:www-data`.

**Resolution:** Correct the exact directories with `chown` and mode `2750`.
The application container uses UID 1000, matching `ikfdeploy`, and Nginx reads
through the `www-data` group.

### GitHub Actions failed before publishing GHCR

**Observed:** `compileall /app` failed on `/app/csv/insertscout.py` because the
legacy file began with a shell command rather than Python syntax.

**Resolution:** Limit CI compilation to actual Django runtime code:

```text
/app/manage.py /app/ikf /app/main /app/internal
```

No application runtime code was skipped, and the verified image subsequently
published to private GHCR.

### GHCR required a different token type

**Observed:** A fine-grained repository token was suitable for Git pushes but
not the intended private GHCR pull setup.

**Resolution:** Use a classic PAT with only `read:packages` on production. Enter
it through `docker login --password-stdin`; never store it in `.env` or Git.

### Legacy dump was a ZIP file

**Observed:** A file named `insert_data.sql` was actually a ZIP containing a SQL
file with the same name.

**Resolution:** Inspect with `file`/`unzip -l` and extract using `unzip -p` into
`insert_data_extracted.sql`.

### Duplicate singleton during test import

**Observed:** Import failed with duplicate primary key `1` in
`main_donatesettings`.

**Cause:** The running website called `DonateSettings.load()` and created the
singleton before import.

**Resolution:** Keep the permanent web service stopped, migrate schema, import
legacy data, validate, and only then start Gunicorn.

### Media URLs appeared to contain `media/media`

**Observed:** A database path such as `media/ui/...` produced a URL beginning
`/media/media/ui/...`.

**Cause:** The first `/media/` is the URL prefix and the second `media/` is part
of the value stored in the database.

**Resolution:** Preserve the legacy relative paths and retain the nested
`docker-data/media/media/ui` directory.

### Old TLS certificate was unsuitable

**Observed:** The old Let's Encrypt certificate covered only the apex hostname
and was near expiry.

**Resolution:** Issue a new apex-plus-www certificate on the new server with a
Cloudflare DNS challenge before changing public DNS.

### Django deployment check reported four security warnings

**Observed:** HSTS, HTTPS redirect, secure session cookie, and secure CSRF cookie
warnings appeared before TLS was enabled.

**Resolution:** First prove Nginx HTTPS works, then set secure environment values,
recreate the container, and rerun `check --deploy`. Do not enable HSTS before a
working HTTPS origin exists.

### Razorpay emits a pkg_resources warning

**Observed:** Razorpay imports deprecated `pkg_resources`.

**Resolution:** Keep the compatible Setuptools constraint for now. The warning
does not block deployment. Upgrade Razorpay when an upstream version removes the
deprecated import; do not silence genuine dependency failures.

## Post-deployment cleanup and operations

Do these only after public application, admin, static, media, email, and payment
checks pass and a backup exists.

### Remove the default Nginx site

The initial deployment kept the default site during configuration. Once IKF is
confirmed:

```bash
unlink /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

### Remove temporary import copies

The following can consume substantial disk space:

```text
/opt/ikf/football/media
/opt/ikf/football/insert_data.sql
/opt/ikf/football/insert_data_extracted.sql
```

Before removal, confirm persistent media size, verify known files, and retain a
protected off-server backup. Do not delete `docker-data/media`.

### Establish backups

Back up at minimum:

- `indiakhelofootball`
- `latmfks`
- `/opt/ikf/football/docker-data/media`
- production `.env` in a secure secrets backup
- Nginx site configuration
- Let's Encrypt renewal configuration and Cloudflare credentials through a
  secure secrets process

Use encrypted off-server storage and test restoration. A backup that has never
been restored is not yet proven.

### Monitor

Monitor:

- Cloudflare availability and origin errors
- Nginx 4xx/5xx rates
- container health and restarts
- Gunicorn tracebacks
- disk usage, especially media and Docker layers
- MySQL availability and backup age
- certificate expiry and Certbot timer status
- GitHub Actions and GHCR publishing failures

### Keep the old server temporarily

Do not destroy the old server immediately after DNS cutover. Keep it isolated
and unchanged for a short rollback window. Prevent new writes from diverging if
traffic can still reach it. After the new system and backups are verified,
decommission the old server deliberately and revoke credentials that are no
longer needed.

## Rollback

Use immutable commit SHA image tags. To roll back:

1. Set `IKF_IMAGE` in `.env` to the previously verified SHA tag.
2. Pull that tag.
3. Recreate the web container.
4. Verify health and logs.

```bash
docker compose pull web
docker compose up -d --no-deps web
docker compose ps
docker compose logs --tail=100 web
```

Database migrations are not automatically reversed during an image rollback.
Review migration compatibility before rolling back across schema changes.

## Routine update

The intended routine flow is:

1. Push reviewed source and migrations to GitHub.
2. Wait for the CI image build to pass.
3. Deploy the exact commit SHA image.
4. Run checks, migrations, and collectstatic.
5. Recreate the web container.
6. Verify health, logs, domain, static files, and media.

Never build from uncommitted production source, run Git inside the container,
generate migrations in production, or store persistent data in the container's
writable layer.
