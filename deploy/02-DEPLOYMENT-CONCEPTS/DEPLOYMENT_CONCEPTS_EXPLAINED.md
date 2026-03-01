# 🚀 Deployment Concepts Explained — Advaitam Project

> This document explains **Gunicorn**, **deploy.sh**, **storages.py**, and **Nginx**
> in the context of your **Advaitam Django project** — step by step, with simple analogies.

---

## 📋 Table of Contents

> 📌 **Sections are ordered in the sequence they happen in real life** —
> from setting up the server, to a user's request hitting your live site.

1. [What does deploy.sh do?](#1-what-does-deploysh-do) ← *Runs first — builds the entire server*
2. [What does storages.py do?](#2-what-does-storagespy-do) ← *Sets up S3/CloudFront during deploy*
3. [What is Nginx and where is it used in this project?](#3-what-is-nginx-and-where-is-it-used-in-this-project) ← *First to receive every live request*
4. [What is Gunicorn?](#4-what-is-gunicorn) ← *Nginx hands off to Gunicorn*
5. [How everything works together (Big Picture)](#5-how-everything-works-together-big-picture) ← *Full flow end to end*
6. [Pre-Deployment Checklist](#6-pre-deployment-checklist--before-going-live) ← *Verify before going live*
7. [How `.env` Fills the Gap Between Settings and Secrets](#7-how-env-fills-the-gap-between-settings-and-secrets) ← *Secrets management*
8. [Database Switchover — SQLite → PostgreSQL](#8-database-switchover--sqlite-dev--postgresql-prod) ← *Dev vs prod database*
9. [Sessions & Cache Strategy](#9-sessions--cache-strategy) ← *How logins are stored*
10. [Security Settings](#10-security-settings--what-your-settingspy-enables-in-production) ← *HTTPS, HSTS, Sentry*
11. [Logging — What Gets Recorded and Where](#11-logging--what-gets-recorded-and-where) ← *All log files explained*
12. [collectstatic — What Actually Happens in Production](#12-collectstatic--what-actually-happens-in-production) ← *S3 upload flow*
13. [Post-Deployment Health Checks](#13-post-deployment-health-checks--verifying-the-server-works) ← *10 checks to verify live server*
14. [Re-Deploying After Code Changes](#14-re-deploying-after-code-changes) ← *Every-day deploy process*
15. [SSL Certificate Auto-Renewal](#15-ssl-certificate-auto-renewal--never-let-it-expire) ← *Prevent certificate expiry*
16. [Backups & Disaster Recovery](#16-backups--disaster-recovery--protect-your-data) ← *Data protection strategy*
17. [Security Scanning](#17-security-scanning--protect-against-known-vulnerabilities) ← *Find CVEs before they find you*
18. [Monitoring, Alerting & Maintenance Mode](#18-monitoring-alerting--maintenance-mode) ← *24/7 uptime monitoring*
19. [Database Maintenance](#19-database-maintenance--keep-postgresql-healthy) ← *Monthly DB optimization*
20. [Secrets Rotation](#20-secrets-rotation--change-passwords-safely) ← *90-day password rotation*
21. [Important Production Settings](#21-important-production-settings-not-yet-covered) ← *Critical fixes for settings.py*
22. [Deployment Checklist](#22-deployment-checklist-final-pre-production) ← *72-hour verification before going live*

---

## 1. What does deploy.sh do?

### 🤔 Simple Analogy

> `deploy.sh` is like an **instruction manual + robot** combined.
> Instead of you manually typing 50+ commands on the server one by one,
> this script **runs them all automatically in the correct order**.

### 📖 What is deploy.sh?

`deploy.sh` is a **Bash shell script** — a file containing a list of Linux commands.
When you run `bash deploy.sh` on your **AWS EC2 server**, it sets up your **entire production environment from scratch** — automatically.

### 📋 Step-by-Step Breakdown of YOUR `deploy.sh`

#### Step 1 — Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
```
- Updates all installed Linux software to the latest versions.
- Ensures security patches are applied.

#### Step 2 — Install System Dependencies
```bash
sudo apt install -y python3.12 python3.12-venv nginx certbot postgresql-16 ...
```
- Installs everything your project needs:
  - `python3.12` → to run your Django code
  - `nginx` → the web server (explained in Section 3)
  - `certbot` → to get a free **SSL/HTTPS certificate** from Let's Encrypt
  - `postgresql-16` → the production database (not SQLite)
  - `supervisor`, `build-essential` → system tools

#### Step 3 — Create App User
```bash
sudo useradd -m -s /bin/bash advaitam
```
- Creates a **dedicated Linux user** called `advaitam` to run your app.
- Running as a separate user (not `root`) is a **security best practice**.
- If your app is hacked, the attacker only has `advaitam` user access, not full root access.

#### Step 4 — Setup PostgreSQL Database
```bash
sudo -u postgres psql -c "CREATE DATABASE advaitam_db;"
sudo -u postgres psql -c "CREATE USER advaitam_user WITH PASSWORD '...';"
```
- Creates the production **PostgreSQL database** and user.
- Production uses PostgreSQL (not SQLite which you use in development).

#### Step 5 — Clone or Update Your Project from GitHub
```bash
git clone https://github.com/YOUR_USERNAME/advaitam.git /home/advaitam/app
# OR if already cloned:
git pull origin main
```
- Downloads your latest code from GitHub onto the server.
- If code already exists, it just pulls the latest changes.

#### Step 6 — Python Virtual Environment
```bash
python3.12 -m venv /home/advaitam/venv
pip install -r requirements-prod.txt
```
- Creates an isolated Python environment just for your project.
- Installs all Python packages listed in `requirements-prod.txt`.

#### Step 7 — Check `.env` File
```bash
if [ ! -f "$PROJECT_DIR/.env" ]; then
    exit 1   # Stop if .env is missing
fi
```
- Checks that your **secret configuration file** (`.env`) exists.
- This file contains secret keys, database passwords, AWS keys etc.
- If missing, the script **stops** and asks you to create it.

#### Step 8 — Django Setup
```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```
- `migrate` → Creates/updates all database tables from your Django models.
- `collectstatic` → Gathers all CSS/JS/images into one folder (or uploads to S3 in production).

#### Step 9 — Create Gunicorn Socket Directory
```bash
sudo mkdir -p /run/advaitam
sudo chown advaitam:www-data /run/advaitam
```
- Creates the folder where the **Gunicorn Unix socket file** will live.
- Gives Nginx (`www-data` group) permission to read the socket.

#### Step 10 — Configure Gunicorn as a systemd Service
```bash
sudo tee /etc/systemd/system/advaitam.service ...
sudo systemctl enable advaitam.service
sudo systemctl start advaitam.socket
```
- Registers Gunicorn as a **Linux background service** (systemd).
- This means Gunicorn will:
  - **Start automatically** when the server boots.
  - **Restart automatically** if it crashes (`Restart=on-failure`).
- The service runs: `gunicorn --config gunicorn.conf.py webProject.wsgi:application`

#### Step 11 — Configure Nginx
```bash
sudo tee /etc/nginx/sites-available/advaitam > /dev/null <<'NGINXEOF'
...Nginx configuration...
NGINXEOF
sudo nginx -t        # Test config for errors
sudo systemctl restart nginx
```
- Writes the Nginx config file for your project.
- Nginx is set up to:
  - Redirect HTTP → HTTPS
  - Proxy requests to Gunicorn via the Unix socket
  - Serve static files
  - Add security headers
- (Nginx is explained in detail in Section 3)

#### Step 12 — SSL Certificate (Manual Step)
```bash
sudo certbot --nginx -d origin.advaitam.info
```
- Gets a **free HTTPS certificate** from Let's Encrypt.
- This is run **manually after DNS is set up** (automated setup is not possible before DNS).
- Makes your site accessible via `https://` instead of insecure `http://`.

### 📊 Summary — What deploy.sh Does in One Diagram

```
bash deploy.sh
      │
      ├── [1]  Update Linux packages
      ├── [2]  Install Nginx, Python, PostgreSQL, Certbot
      ├── [3]  Create 'advaitam' Linux user
      ├── [4]  Create PostgreSQL database
      ├── [5]  Clone/update code from GitHub
      ├── [6]  Setup Python virtual environment + install packages
      ├── [7]  Verify .env secret file exists
      ├── [8]  Run Django migrations + collectstatic
      ├── [9]  Create Gunicorn socket directory
      ├── [10] Register Gunicorn as systemd service (auto-start)
      ├── [11] Configure + start Nginx
      └── [12] Remind you to get SSL certificate manually
```

---

## 2. What does storages.py do?

### 🤔 Simple Analogy

> By default, Django saves your files (CSS, images, audio) on the **same hard disk** as your server.
> But what if the server restarts? Or you need files available **globally fast**?
> **storages.py** tells Django: *"Don't save files on the local disk — save them in **Amazon S3** (cloud storage) and serve them through **CloudFront** (global CDN)."*

### 📖 What is storages.py?

`storages.py` defines **two custom storage backends** for your Django project:
1. **StaticStorage** — for ALL files **you deploy** as part of the project (CSS, JS, images, audio, PDFs, fonts)
2. **MediaStorage** — reserved for **user-uploaded** content only (currently unused in this project)

Both use **Amazon S3** (cloud object storage) as the actual storage location, and **CloudFront** as the delivery network.

### 🪣 Where files are stored

```
S3 Bucket: advaitam-assets
│
├── /static/    ← Everything YOU deploy (not user uploads)
│                  static/css/         → home.css etc.
│                  static/js/          → audio.js etc.
│                  static/images/      → adishankaracharya.jpg, India.png, SrinivasaRao.png, USA.png
│                  static/audio/       → bhagavadgita/, grantha/, sutra/, upanisad/, vidyaranya/
│                  static/books/       → Django.pdf etc.
│                  static/fonts/       → web fonts (if added)
│                  static/admin/       → Django admin CSS/JS (auto-added by collectstatic)
│                  Served via: https://<cloudfront-domain>/static/
│
└── /media/     ← User-uploaded files ONLY (currently NOT used in this project)
                   Reserved for future features like profile photo uploads etc.
                   Served via: https://<cloudfront-domain>/media/
```

> ⚠️ **Important distinction:**
> Your `audio/`, `images/`, and `books/` folders are files **you provide** as part of the app — they go to `StaticStorage`.
> `MediaStorage` is only for files that **users upload through your app** (e.g. a profile picture form), which this project does not have yet.

### ⚙️ StaticStorage — Explained Line by Line

```python
class StaticStorage(S3Boto3Storage):
    location = 'static'          # Files go to s3://advaitam-assets/static/
    default_acl = None           # No public ACL — CloudFront OAC controls access
    querystring_auth = False     # No signed/expiring URLs — files are publicly accessible via CloudFront
    file_overwrite = True        # When you run collectstatic again, overwrite existing files (intended)
```

- Used for **CSS, JS, images, audio recitations, PDFs, fonts, Django admin styles** — everything in your `static/` folder.
- These files **never change per user** — same file for everyone.
- `file_overwrite = True` → every time you run `collectstatic`, the latest version overwrites the old one on S3.
- Cached for **1 year** (immutable) because they are versioned by Django's `ManifestStaticFilesStorage`.

### ⚙️ MediaStorage — Explained Line by Line

```python
class MediaStorage(S3Boto3Storage):
    location = 'media'           # Files go to s3://advaitam-assets/media/
    default_acl = None           # No public ACL — CloudFront controls access
    querystring_auth = False     # No signed URLs — public content
    file_overwrite = False       # DON'T overwrite — add unique suffix to keep all uploads safe
```

- **Currently NOT used** — this project has no user file upload features yet.
- `file_overwrite = False` → if a user uploads `photo.jpg` twice, both are kept as `photo.jpg` and `photo_abc123.jpg` — **no accidental data loss**.
- Ready to use the moment you add an upload feature (e.g. `models.ImageField(upload_to=...)`  will automatically use this).

### 🌍 Why use S3 + CloudFront instead of local disk?

| Feature | Local Disk | S3 + CloudFront |
|--------|-----------|-----------------|
| Survives server restart | ❌ No | ✅ Yes |
| Scales to millions of users | ❌ No | ✅ Yes |
| Fast delivery globally | ❌ No | ✅ Edge caching |
| Separate from app server | ❌ No | ✅ Yes |
| Cost | Cheap | Pay-per-use (very cheap) |

### 🔗 How storages.py connects to settings.py

In `settings.py`, when `USE_S3=True` in your `.env` file:
```python
STATICFILES_STORAGE = 'webapp.storages.StaticStorage'
DEFAULT_FILE_STORAGE = 'webapp.storages.MediaStorage'
```
This tells Django to **use your custom storage classes** instead of the default local file system.

---

## 3. What is Nginx and Where is it Used in This Project?

### 🤔 Simple Analogy

> Think of your server as a **large office building**.
> **Nginx** is the **security guard + receptionist** at the front door.
> - Every visitor (browser request) goes through Nginx first.
> - Nginx checks if you need a **static file** (CSS/image) → handles it directly.
> - Nginx checks if you need a **dynamic page** → passes you to the right department (Gunicorn → Django).
> - Nginx also ensures all visitors use the **secure entrance (HTTPS)**.

### 📖 What is Nginx?

**Nginx** (pronounced "Engine-X") is a **high-performance web server** and **reverse proxy**.

It does two main jobs in your project:

| Job | What it means |
|-----|--------------|
| **Web Server** | Serves static files (CSS, JS) directly — very fast |
| **Reverse Proxy** | Forwards dynamic requests to Gunicorn (Django) |

### 🏗️ Where Nginx is Configured in YOUR Project

Nginx is configured **inside `deploy.sh`** (Step 11). The config is written to:
```
/etc/nginx/sites-available/advaitam
```

### 📋 Step-by-Step: What YOUR Nginx Config Does

#### Part 1 — Redirect HTTP to HTTPS
```nginx
server {
    listen 80;
    server_name origin.advaitam.info;
    return 301 https://$host$request_uri;
}
```
- Any request coming on **port 80 (HTTP)** is immediately redirected to **HTTPS (port 443)**.
- `301` is a permanent redirect — browsers and search engines remember this.
- This ensures **no one accidentally browses your site over insecure HTTP**.

#### Part 2 — Main HTTPS Server Block
```nginx
server {
    listen 443 ssl http2;
    server_name origin.advaitam.info;
    ...
}
```
- Listens on **port 443** (HTTPS) with **HTTP/2** support (faster than HTTP/1.1).
- `origin.advaitam.info` is your **origin domain** (direct to EC2, not the public CloudFront domain).

#### Part 3 — SSL Certificate Setup
```nginx
ssl_certificate     /etc/letsencrypt/live/origin.advaitam.info/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/origin.advaitam.info/privkey.pem;
ssl_protocols       TLSv1.2 TLSv1.3;
```
- Points to your **Let's Encrypt SSL certificate** files (set up by Certbot).
- Only allows **TLS 1.2 and 1.3** — older insecure versions (TLS 1.0, 1.1) are blocked.
- This is what gives your site the **green padlock 🔒** in browsers.

#### Part 4 — Trust CloudFront for Real IP
```nginx
real_ip_header    CloudFront-Viewer-Address;
real_ip_recursive on;
```
- Your traffic flow is: **User → CloudFront → Nginx**.
- Without this, Nginx would log CloudFront's IP, not the real visitor's IP.
- This setting reads the real IP from the `CloudFront-Viewer-Address` header.

#### Part 5 — Proxy Requests to Gunicorn (THE MOST IMPORTANT PART)
```nginx
location / {
    proxy_pass http://unix:/run/advaitam/gunicorn.sock;
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;
    proxy_read_timeout  120s;
}
```
- For **every URL** (`/`), Nginx forwards the request to Gunicorn via the **Unix socket file**.
- `proxy_set_header` lines pass important information to Django:
  - `Host` → which domain was requested
  - `X-Real-IP` → the real visitor's IP address
  - `X-Forwarded-Proto` → whether original request was HTTP or HTTPS (Django needs this for `request.is_secure()`)
- `proxy_read_timeout 120s` → matches Gunicorn's timeout (important for audio streaming in your app).

#### Part 6 — Serve Static Files Locally (Fallback)
```nginx
location /static/ {
    alias /home/advaitam/app/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```
- If a request comes for `/static/css/home.css`, Nginx serves it **directly from disk** — extremely fast.
- In production, your static files normally go to **S3/CloudFront** (via `storages.py`), but this is a **fallback**.
- `expires 30d` → browser caches the file for 30 days (no repeated downloads).

#### Part 7 — Gzip Compression
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript ...;
gzip_min_length 1024;
```
- Compresses responses before sending to the browser.
- Makes your site **load faster** (smaller file sizes over the network).
- E.g., a 100KB CSS file becomes ~20KB after gzip.

#### Part 8 — Security Headers
```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```
- `X-Content-Type-Options: nosniff` → Prevents browsers from guessing file types (security).
- `X-Frame-Options: DENY` → Prevents your site from being loaded inside an `<iframe>` (stops clickjacking attacks).
- `Referrer-Policy` → Controls what URL is sent as the referrer when users click links.

#### Part 9 — Logging
```nginx
access_log /home/advaitam/app/logs/nginx_access.log;
error_log  /home/advaitam/app/logs/nginx_error.log;
```
- All HTTP access logs saved to your `logs/nginx_access.log`.
- All Nginx errors saved to `logs/nginx_error.log`.

### 🗺️ Where Nginx Fits in the Full Architecture

```
User's Browser
      │
      ↓
CloudFront CDN (advaitam.info)
      │
      ├── Static files (CSS/JS/Audio) → Directly from S3 bucket
      │
      └── Dynamic requests → EC2 Server
                                  │
                                  ↓
                              Nginx (port 443)
                                  │
                                  ├── /static/ → Local staticfiles/ folder (fallback)
                                  │
                                  └── Everything else → Unix Socket
                                                             │
                                                             ↓
                                                      Gunicorn (2 workers)
                                                             │
                                                             ↓
                                                      Django App
                                                   (views, models, DB)
                                                             │
                                                             ↓
                                                      PostgreSQL DB
```

---

## 4. What is Gunicorn?

### 🤔 Simple Analogy

> Think of your Django app as a **chef** in a kitchen.
> The chef knows how to cook (handle requests), but **can't talk to customers directly**.
> **Gunicorn** is the **restaurant manager** who takes orders from customers (via Nginx)
> and passes them to the right chef (Django worker).

### 📖 What is Gunicorn?

**Gunicorn** stands for **Green Unicorn**. It is a **WSGI (Web Server Gateway Interface) server** for Python web applications.

When you run Django with `python manage.py runserver` — that is only for **development** (your local machine). It is slow and handles only **one request at a time**.

In **production** (live server), you use **Gunicorn** instead because:
- It can handle **multiple requests at the same time** using workers.
- It is **fast, stable, and production-ready**.
- It acts as a **bridge** between your Django code and the web server (Nginx).

### ⚙️ How Gunicorn is configured in YOUR project (`gunicorn.conf.py`)

```python
bind = "unix:/run/advaitam/gunicorn.sock"
```
- Gunicorn **listens on a Unix socket file** (not a port).
- A **Unix socket** is a special file used for fast communication between two programs on the **same machine** (Nginx and Gunicorn here).
- It is faster than using a TCP port (like `localhost:8000`) when both Nginx and Gunicorn are on the same server.

```python
workers = 2
threads = 2
```
- **2 workers** = 2 separate Python processes running your Django app.
- **2 threads per worker** = each worker can handle 2 requests at the same time.
- Total: **4 requests handled simultaneously** — safe for your EC2 t4g.micro (1GB RAM).
- If you used the default formula `2 × CPU + 1 = 5 workers`, your server would **run out of memory (OOM crash)**.

```python
timeout = 120
```
- If a request takes longer than **120 seconds**, the worker is killed.
- This is needed for **audio streaming** in your app which may take longer.

```python
max_requests = 1000
preload_app = True
```
- Each worker is **recycled after 1000 requests** to prevent memory leaks.
- `preload_app = True` loads Django **once before forking** workers — saves ~60MB of RAM using Python's copy-on-write mechanism.

```python
accesslog = "/home/advaitam/app/logs/gunicorn_access.log"
errorlog  = "/home/advaitam/app/logs/gunicorn_error.log"
```
- All request logs and errors are saved to your `logs/` folder.

### 🔁 Gunicorn Request Flow

```
Browser Request
      ↓
   Nginx (port 443)
      ↓
   Unix Socket (/run/advaitam/gunicorn.sock)
      ↓
   Gunicorn Worker (Python process)
      ↓
   Django App (views.py, models.py, etc.)
      ↓
   Response sent back the same way
```

---

## 5. How Everything Works Together (Big Picture)

Here is the **complete picture** of all components working together in your Advaitam project:

### 🔁 When a user visits `advaitam.info/about/`

```
Step 1: User types advaitam.info in browser
          ↓
Step 2: DNS → CloudFront (CDN edge server closest to user)
          ↓
Step 3: CloudFront checks cache → Not cached → forwards to origin.advaitam.info
          ↓
Step 4: Nginx receives the HTTPS request on port 443
          ↓
Step 5: Nginx proxies it to Gunicorn via Unix socket (/run/advaitam/gunicorn.sock)
          ↓
Step 6: Gunicorn picks an available worker (Django process)
          ↓
Step 7: Django processes the request → runs your view in views.py
          ↓
Step 8: Django queries PostgreSQL database → gets data
          ↓
Step 9: Django renders HTML template → sends response back
          ↓
Step 10: Response travels back: Django → Gunicorn → Unix Socket → Nginx → CloudFront → User
          ↓
Step 11: CloudFront caches the response (for future users — faster!)
```

### 📁 What Each File Does — Summary Table

| File | Role | Where it Runs |
|------|------|---------------|
| `gunicorn.conf.py` | Configures how many workers, timeouts, socket path for Gunicorn | AWS EC2 server |
| `deploy.sh` | Automates complete server setup — 12 steps from scratch to live | Run once on EC2 |
| `storages.py` | Tells Django to store files in S3 and serve via CloudFront | Django app |
| Nginx config (in deploy.sh) | Receives HTTPS requests, proxies to Gunicorn, serves static files | AWS EC2 server |

### 🧩 Why You Need All Four

- **Without Gunicorn** → Django's dev server crashes under multiple users.
- **Without Nginx** → No HTTPS, no gzip, Gunicorn exposed directly to internet (unsafe).
- **Without storages.py** → Static/media files lost on server restart, no global CDN speed.
- **Without deploy.sh** → You'd have to run 50+ commands manually every deployment.

---

> 💡 **Key Takeaway:**
> Your local `python manage.py runserver` is like a **bicycle** — fine for one person.
> In production: **Nginx + Gunicorn + S3 + CloudFront** is like a **highway system** — handles thousands of users simultaneously, safely and fast.

---

## 6. Pre-Deployment Checklist — Before Going Live

> This is what **every real company** verifies before pressing the deploy button.
> Skipping any of these is how production outages happen.

### ✅ Django Settings to Verify

| Setting | Development Value | Production Value | Where set |
|---------|------------------|------------------|-----------|
| `DEBUG` | `True` | **`False`** ← critical | `.env` |
| `SECRET_KEY` | any string | **long random key** | `.env` |
| `ALLOWED_HOSTS` | `localhost` | `advaitam.info, origin.advaitam.info, <EC2-IP>` | `.env` |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost` | `https://advaitam.info, https://www.advaitam.info` | `.env` |
| `USE_S3` | `False` | **`True`** | `.env` |
| `DATABASE` | SQLite | **PostgreSQL** | auto-switched by `DEBUG` in `settings.py` |

> ⚠️ **Why `DEBUG=False` matters in production:**
> - With `DEBUG=True`, Django shows full error pages with your **source code, env variables, and file paths** to any visitor — a massive security hole.
> - With `DEBUG=False`, visitors see a generic error page. Only your logs know what went wrong.

### ✅ Generate a Secure SECRET_KEY

Run this once and put the output in your `.env`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
- Never reuse your dev `SECRET_KEY` in production.
- Never commit `.env` to GitHub — it contains this secret.

### ✅ Files that must NOT be committed to GitHub

```
.env                  ← contains SECRET_KEY, DB passwords, AWS keys
db.sqlite3            ← local dev database
logs/                 ← log files
__pycache__/          ← compiled Python files
.venv/                ← virtual environment
```
These should all be in your `.gitignore`.

---

## 7. How `.env` Fills the Gap Between Settings and Secrets

### 🤔 Simple Analogy

> Think of `settings.py` as a **car dashboard with labelled controls**.
> The `.env` file is like the **key and fuel** — the dashboard is useless without it.
> The dashboard (settings.py) is committed to GitHub. The key (`.env`) stays private.

### 📖 How it works in YOUR project

Your `settings.py` uses `django-environ` to read values from `.env`:
```python
env = environ.Env(DEBUG=(bool, False))
env.read_env(env_file)   # reads .env file
SECRET_KEY = env("SECRET_KEY")   # pulls from .env
```

### 📋 What each `.env` variable does in production

```bash
# Core Django
SECRET_KEY=...              # Signs cookies, sessions, CSRF tokens — must be secret
DEBUG=False                 # Disables debug mode (see Section 6)
ALLOWED_HOSTS=...           # Only these domains can send requests to Django

# Database — switches settings.py from SQLite to PostgreSQL automatically
DB_NAME=advaitam_db
DB_USER=advaitam_user
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=5432

# S3 + CloudFront — switches staticfiles from local disk to S3
USE_S3=True
AWS_STORAGE_BUCKET_NAME=advaitam-assets
AWS_S3_CUSTOM_DOMAIN=xxxx.cloudfront.net   ← all static/media URLs point here

# Email — used for password reset, contact form etc.
EMAIL_BACKEND=...
EMAIL_HOST=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...

# Anthropic Claude AI — used by claude_chat feature
ANTHROPIC_API_KEY=sk-ant-...

# Sentry — error tracking in production (see Section 10)
SENTRY_DSN=https://...@sentry.io/...

# Sessions
SESSION_COOKIE_AGE=86400    # 24 hours before login expires
```

---

## 8. Database Switchover — SQLite (Dev) → PostgreSQL (Prod)

### 🤔 Simple Analogy

> SQLite is like a **notebook** — fine for one person writing notes.
> PostgreSQL is like a **filing cabinet with locks** — handles multiple people reading and writing simultaneously without corrupting data.

### 📖 How YOUR `settings.py` handles this automatically

```python
if DEBUG:
    # Development: SQLite (zero setup, file-based)
    DATABASES = { 'default': { 'ENGINE': 'sqlite3', 'NAME': BASE_DIR / "db.sqlite3" } }
else:
    # Production: PostgreSQL (reads credentials from .env)
    DATABASES = { 'default': { 'ENGINE': 'postgresql', 'NAME': env('DB_NAME'), ... } }
```

- When `DEBUG=False` (production), Django **automatically switches to PostgreSQL** — no code change needed.
- `CONN_MAX_AGE=600` → Django keeps the database connection open for **10 minutes** instead of opening a new one on every request — much faster.

### ⚠️ Why not use SQLite in production?

| Problem | SQLite | PostgreSQL |
|---------|--------|-----------|
| Multiple users at once | ❌ Locks the whole file | ✅ Row-level locking |
| Data corruption risk | ❌ High under load | ✅ ACID transactions |
| Performance | ❌ Slow at scale | ✅ Fast with indexes |
| Backups | ❌ Manual file copy | ✅ `pg_dump`, automated snapshots |

### 📋 Password Hashing — Extra Security in YOUR project

Your `settings.py` uses **Argon2** as the primary password hasher:
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',   # ← strongest, used first
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ...
]
```
- **Argon2** is the winner of the Password Hashing Competition (2015) — recommended by OWASP.
- Even if your database is stolen, passwords are practically uncrackable.

---

## 9. Sessions & Cache Strategy

### 📖 What is a Session?

When a user logs in, Django creates a **session** — a record that says "this browser is logged in as user X".
This session must be stored somewhere.

### ⚙️ How YOUR project handles sessions (from `settings.py`)

```python
if REDIS_URL:
    # Fast: sessions stored in Redis (in-memory)
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
else:
    # Budget: sessions stored in PostgreSQL database (default for this project)
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

Your project uses **database sessions** by default — this means:
- No Redis/ElastiCache needed → **saves ~$12/month**
- Sessions are stored in the `django_session` table in PostgreSQL
- Slightly slower than Redis but perfectly fine for low-to-medium traffic

> 💡 If traffic grows and login/logout becomes slow, just add `REDIS_URL` to `.env` and it automatically switches to Redis — no code change needed.

### ⚙️ Cache Strategy

```python
# No Redis → local memory cache (free, per-worker)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'advaitam-cache',
    }
}
```
- **Local memory cache** = each Gunicorn worker has its own small cache in RAM.
- Free, no extra setup, works well for 2 workers on t4g.micro.

---

## 10. Security Settings — What YOUR `settings.py` Enables in Production

When `DEBUG=False`, your `settings.py` automatically turns on these security settings:

| Setting | What it does |
|---------|-------------|
| `SECURE_SSL_REDIRECT = True` | Forces all HTTP requests to redirect to HTTPS |
| `SESSION_COOKIE_SECURE = True` | Session cookie only sent over HTTPS, never HTTP |
| `CSRF_COOKIE_SECURE = True` | CSRF token only sent over HTTPS |
| `SESSION_COOKIE_HTTPONLY = True` | JavaScript cannot steal the session cookie |
| `X_FRAME_OPTIONS = 'DENY'` | Stops your site being embedded in `<iframe>` (clickjacking) |
| `SECURE_HSTS_SECONDS = 31536000` | Tells browsers: "always use HTTPS for this domain for 1 year" |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS = True` | HSTS applies to `www.advaitam.info` too |
| `SECURE_HSTS_PRELOAD = True` | Submits your domain to browser HSTS preload lists |
| `SECURE_PROXY_SSL_HEADER` | Tells Django to trust `X-Forwarded-Proto` header from Nginx |

> ⚠️ **`SECURE_PROXY_SSL_HEADER` is critical** for your setup.
> Because traffic flow is: User → CloudFront → Nginx → Gunicorn → Django
> Nginx terminates SSL and forwards requests to Gunicorn as plain HTTP internally.
> Without this setting, Django thinks every request is HTTP and `request.is_secure()` returns `False`,
> causing infinite redirects or broken CSRF.

### 🔒 Sentry Error Tracking

Your `settings.py` integrates **Sentry** for error monitoring:
```python
if _SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=_SENTRY_DSN,
        traces_sample_rate=0.2,   # Monitors 20% of requests for performance
        environment='production',
    )
```
- When any unhandled exception occurs in production, Sentry **instantly emails you** with the full stack trace, user info, and request details.
- Free tier: 5,000 errors/month — enough for a small production site.
- Set `SENTRY_DSN` in your `.env` to activate it.
- Sign up at https://sentry.io (free).

---

## 11. Logging — What Gets Recorded and Where

### 📖 How YOUR logging works (`settings.py`)

```python
'file': {
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': LOGS_DIR / 'django.log',
    'maxBytes': 1024 * 1024 * 15,   # 15MB max per file
    'backupCount': 10,               # Keep 10 old log files
}
```

| Log file | What it contains | Max size |
|---------|-----------------|----------|
| `logs/django.log` | Django warnings, errors, DB errors | 15MB × 10 = 150MB total |
| `logs/gunicorn_access.log` | Every HTTP request (method, URL, status, time) | Managed by Gunicorn |
| `logs/gunicorn_error.log` | Gunicorn worker errors, crashes | Managed by Gunicorn |
| `logs/nginx_access.log` | Every request Nginx received | Managed by Nginx |
| `logs/nginx_error.log` | Nginx errors (bad config, upstream failures) | Managed by Nginx |

### 📋 Useful commands to read logs on the server

```bash
# Watch Django errors in real time
tail -f /home/advaitam/app/logs/django.log

# Watch Gunicorn errors in real time
tail -f /home/advaitam/app/logs/gunicorn_error.log

# Check Nginx errors
tail -f /home/advaitam/app/logs/nginx_error.log

# Check systemd service status
sudo systemctl status advaitam.service

# See last 50 lines of service logs
sudo journalctl -u advaitam.service -n 50
```

---

## 12. collectstatic — What Actually Happens in Production

### 🤔 Simple Analogy

> `collectstatic` is like a **moving company**.
> Your CSS, JS, images, audio, PDFs are scattered across your project folders (`static/`).
> `collectstatic` **packs them all up and delivers them** to one final destination — in production, that destination is your **S3 bucket**.

### 📋 What happens step by step

```
python manage.py collectstatic --noinput
         │
         ├── Scans: static/css/, static/js/, static/images/,
         │          static/audio/, static/books/,
         │          and all installed apps (e.g. Django admin's static files)
         │
         ├── USE_S3=True → uses StaticStorage (storages.py)
         │
         ├── Uploads EVERY file to:
         │      s3://advaitam-assets/static/css/home.css
         │      s3://advaitam-assets/static/js/audio.js
         │      s3://advaitam-assets/static/images/adishankaracharya.jpg
         │      s3://advaitam-assets/static/audio/bhagavadgita/...
         │      s3://advaitam-assets/static/books/Django.pdf
         │      s3://advaitam-assets/static/admin/css/...  ← Django admin styles
         │
         └── Django generates hashed filenames (ManifestStaticFilesStorage):
                home.css  →  home.abc123de.css
                audio.js  →  audio.ff98ab12.js
                (hash changes only when file content changes — enables 1-year browser cache)
```

> 💡 **Why hashed filenames?**
> If you update `home.css`, the hash changes → new filename → browser downloads the new version immediately.
> If the hash is the same → browser uses its cached copy → zero network request → faster page load.

---

## 13. Post-Deployment Health Checks — Verifying the Server Works

> After running `deploy.sh`, always verify these one by one before announcing the site is live.

### ✅ Step-by-Step Verification

#### Check 1 — Gunicorn service is running
```bash
sudo systemctl status advaitam.service
# Expected: ● advaitam.service - Advaitam Django Gunicorn
#              Active: active (running)
```

#### Check 2 — Nginx is running
```bash
sudo systemctl status nginx
# Expected: Active: active (running)
```

#### Check 3 — Nginx config has no errors
```bash
sudo nginx -t
# Expected: nginx: configuration file /etc/nginx/nginx.conf test is successful
```

#### Check 4 — Socket file exists
```bash
ls -la /run/advaitam/gunicorn.sock
# Expected: srw-rw---- 1 advaitam www-data ... gunicorn.sock
```

#### Check 5 — Django can reach the database
```bash
sudo -u advaitam /home/advaitam/venv/bin/python /home/advaitam/app/manage.py dbshell
# Expected: psql prompt opens → type \q to exit
```

#### Check 6 — Test HTTP response locally on the server
```bash
curl -I http://localhost
# Expected: HTTP/1.1 301 Moved Permanently  (redirect to HTTPS)
```

#### Check 7 — Test HTTPS response
```bash
curl -I https://origin.advaitam.info
# Expected: HTTP/2 200
```

#### Check 8 — Static files are on S3
```bash
# Open in browser:
# https://<cloudfront-domain>/static/css/home.css
# Should load your CSS file
```

#### Check 9 — Check Django logs for errors
```bash
tail -20 /home/advaitam/app/logs/django.log
# Expected: empty or only WARNING level messages — no ERRORs
```

#### Check 10 — SSL certificate is valid
```bash
sudo certbot certificates
# Expected: Certificate Name: origin.advaitam.info
#           Expiry Date: ... (VALID)
```

---

## 14. Re-Deploying After Code Changes

> The **first deploy** uses `deploy.sh`. After that, for every code update, you only need these steps — not the full script.

### 📋 Standard Re-deploy Process (every time you push new code)

```bash
# 1. SSH into your EC2 server
ssh -i your-key.pem ubuntu@<EC2-IP>

# 2. Pull latest code from GitHub
cd /home/advaitam/app
sudo -u advaitam git pull origin main

# 3. Activate virtual environment
source /home/advaitam/venv/bin/activate

# 4. Install any new packages (if requirements-prod.txt changed)
pip install -r requirements-prod.txt

# 5. Run any new database migrations
python manage.py migrate --noinput

# 6. Upload updated static files to S3 (if CSS/JS/images changed)
python manage.py collectstatic --noinput

# 7. Restart Gunicorn to load new code
sudo systemctl restart advaitam.service

# 8. Verify it's running
sudo systemctl status advaitam.service
```

> ✅ You do **NOT** need to restart Nginx unless you changed the Nginx config.
> ✅ You do **NOT** need to restart PostgreSQL unless you changed database config.
> Only Gunicorn needs restarting — it's the one running your Django code.

### ⚡ Quick one-liner re-deploy (after SSH in)
```bash
cd /home/advaitam/app && sudo -u advaitam git pull origin main && sudo systemctl restart advaitam.service
```

---

## 15. SSL Certificate Auto-Renewal — Never Let It Expire

> SSL certificates from Let's Encrypt expire every **90 days**.
> Certbot automatically renews them — but you must verify it's working.

### 📖 How renewal is set up in YOUR project

Your `deploy.sh` (Step 11) installs **Certbot** and `deploy/.env.prod.template` has:
```bash
sudo certbot --nginx -d origin.advaitam.info
```

Certbot automatically adds a **systemd timer** that renews certificates 30 days before expiry.

### ✅ Verify Auto-Renewal is Working

```bash
# Check if renewal systemd timer is active
sudo systemctl status certbot.timer
# Expected: ● certbot.timer - Run certbot twice daily
#              Active: active (running)

# Manually trigger a test renewal (doesn't actually renew, just tests)
sudo certbot renew --dry-run

# Check certificate expiry date
sudo certbot certificates
# Expected: Expiry Date: YYYY-MM-DD ... (should be ~90 days in future)

# See renewal history
sudo journalctl -u certbot.service --no-pager | tail -20
```

### ⚠️ If Renewal Fails

```bash
# Renew manually
sudo certbot renew --force-renewal

# Restart Nginx to load new certificate
sudo systemctl restart nginx

# Check Nginx can read the new certificate
sudo nginx -t
```

> 💡 **Pro tip:** Set up Sentry alerts (Section 10) to notify you of certificate expiry. Search Sentry for "certbot" errors.

---

## 16. Backups & Disaster Recovery — Protect Your Data

> A production site without backups is like a car without brakes.
> **You WILL lose data eventually** — plan for it now.

### 🗄️ What needs backing up?

| What | Where | Why | How often |
|-----|-------|-----|-----------|
| PostgreSQL database | `advaitam_db` | User data, content | Daily |
| S3 bucket (audio, images) | `advaitam-assets` | Static assets | Daily (versioning) |
| `.env` file | `/home/advaitam/app/.env` | Secrets, passwords | After changes |
| Source code | GitHub repo | App logic | Automatic (Git) |

### 📋 PostgreSQL Daily Backup Strategy

```bash
# Create a backup script: /home/advaitam/backups/backup-db.sh
#!/bin/bash
BACKUP_DIR="/home/advaitam/backups/postgresql"
mkdir -p "$BACKUP_DIR"

# Create timestamped backup
pg_dump -U advaitam_user advaitam_db | gzip > "$BACKUP_DIR/advaitam_db_$(date +%Y%m%d_%H%M%S).sql.gz"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR"
```

### 📋 Schedule daily backups with Cron

```bash
# Add to crontab (runs every day at 2 AM)
sudo crontab -e

# Add this line:
0 2 * * * /home/advaitam/backups/backup-db.sh
```

### 📋 S3 Versioning (Built-in Protection)

Enable S3 versioning so all object versions are kept:
```bash
aws s3api put-bucket-versioning \
  --bucket advaitam-assets \
  --versioning-configuration Status=Enabled
```
Now if a file is accidentally deleted, you can recover it from history.

### 📋 Test Restore Procedure (DO THIS MONTHLY)

```bash
# 1. Restore from backup to a test database
gunzip < advaitam_db_20250222_020000.sql.gz | psql -U advaitam_user advaitam_db_test

# 2. Verify data is there
psql -U advaitam_user advaitam_db_test -c "SELECT COUNT(*) FROM auth_user;"

# 3. Delete test database
dropdb -U advaitam_user advaitam_db_test
```

> ⚠️ **The only backup that matters is one you've successfully restored.**
> Test your backups at least once a month.

---

## 17. Security Scanning — Protect Against Known Vulnerabilities

> Your `requirements-prod.txt` has 20+ packages, each with their own security history.
> Companies regularly scan for vulnerabilities.

### 📋 Scan Python Packages for CVEs

```bash
# Install safety (detects vulnerable packages)
pip install safety

# Scan your environment
safety check --requirements requirements-prod.txt

# Expected output: If vulnerabilities found, it lists them with links to CVE databases
```

### 📋 GitHub Dependabot (Automatic Scanning)

GitHub automatically scans your repository for vulnerable dependencies:
1. Go to your GitHub repo → **Settings → Security & analysis**
2. Enable **Dependabot alerts** → GitHub notifies you of vulnerabilities
3. Enable **Dependabot security updates** → GitHub auto-creates PRs to fix vulnerabilities

### 📋 Regular Update Schedule

On your EC2 server, patch OS and Python packages monthly:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages to latest versions
pip install --upgrade pip
pip install -r requirements-prod.txt --upgrade

# Test nothing broke
python manage.py test

# Restart Django if anything changed
sudo systemctl restart advaitam.service
```

---

## 18. Monitoring, Alerting & Maintenance Mode

> Real companies monitor their sites 24/7. You don't need fancy tools — just the basics.

### 📊 Essential Monitoring Checklist

| What to monitor | Tool | Action |
|---|---|---|
| Is the site up? | Uptime robot (uptimerobot.com) | Email alert if down |
| Are errors increasing? | Sentry (already set up) | Email on spike |
| Is Nginx running? | systemd health | Auto-restarts on crash |
| Is Gunicorn running? | systemd health | Auto-restarts on crash |
| Is PostgreSQL responsive? | `pg_isready` cron check | Alert if down |
| Disk space | cron `df -h` check | Alert at 80% full |
| Memory usage | cron `free -h` check | Alert at 85% used |

### 📋 Uptime Monitoring (Free)

Create a free UptimeRobot account: https://uptimerobot.com

```
Monitor: https://advaitam.info
Frequency: Every 5 minutes
Alert email: your-email@gmail.com
Expected: HTTP 200
```

If your site is down for >5 minutes, you get an email instantly.

### 📋 Emergency Maintenance Mode (Without Downtime)

If you need to deploy something big and want to show a "Under Maintenance" page:

Edit `/etc/nginx/sites-available/advaitam` (on the server):

```nginx
# Add before the main location block
if (-f /tmp/maintenance.lock) {
    return 503;
}

error_page 503 /maintenance.html;

location = /maintenance.html {
    root /home/advaitam/app/templates;
    internal;
}
```

Then when deploying:

```bash
# 1. Enable maintenance mode
sudo touch /tmp/maintenance.lock
sudo systemctl reload nginx

# 2. Do your deployment
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart advaitam.service

# 3. Disable maintenance mode
sudo rm /tmp/maintenance.lock
sudo systemctl reload nginx
```

Visitors see "Under Maintenance" page instead of errors. Seamless!

---

## 19. Database Maintenance — Keep PostgreSQL Healthy

> PostgreSQL is not a fire-and-forget database.
> It needs periodic maintenance to stay fast.

### 📋 Monthly Maintenance Tasks

```bash
# 1. VACUUM — reclaims space from deleted rows
sudo -u postgres psql advaitam_db -c "VACUUM ANALYZE;"

# 2. Check for unused indexes
sudo -u postgres psql advaitam_db -c "
    SELECT indexrelname FROM pg_stat_user_indexes 
    WHERE idx_scan = 0 ORDER BY relpages DESC;"

# 3. Check table sizes
sudo -u postgres psql advaitam_db -c "
    SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
    AS size FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema') 
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# 4. Check connection count
sudo -u postgres psql advaitam_db -c "SELECT count(*) FROM pg_stat_activity;"
```

### 📋 Automate Monthly Maintenance with Cron

```bash
# Create: /home/advaitam/backups/maintenance-db.sh
#!/bin/bash
sudo -u postgres psql advaitam_db -c "VACUUM ANALYZE;"
echo "$(date): Database maintenance completed" >> /var/log/db-maintenance.log
```

Schedule it:
```bash
sudo crontab -e
# Add: 0 3 1 * * /home/advaitam/backups/maintenance-db.sh
# (Runs at 3 AM on the 1st of each month)
```

---

## 20. Secrets Rotation — Change Passwords Safely

> Company best practice: rotate secrets every 90 days.
> This means changing `.env` values without breaking production.

### 🔐 How to rotate DATABASE PASSWORD safely

```bash
# 1. On EC2 server, generate new password
NEW_PASSWORD=$(openssl rand -base64 32)
echo $NEW_PASSWORD

# 2. Update PostgreSQL user with new password
sudo -u postgres psql -c "ALTER USER advaitam_user WITH PASSWORD '$NEW_PASSWORD';"

# 3. Update .env file on server
sudo nano /home/advaitam/app/.env
# Change: DB_PASSWORD=<old_password> → DB_PASSWORD=<new_password>

# 4. Restart Gunicorn (uses new password from .env)
sudo systemctl restart advaitam.service

# 5. Verify it works
sudo systemctl status advaitam.service
# Should show: Active: active (running)
```

### 🔐 How to rotate AWS SECRET ACCESS KEY

```bash
# 1. In AWS Console → IAM → Users → advaitam-deploy
#    Create a NEW access key (you can have 2 active at once)

# 2. Copy the new key ID and secret to a safe place

# 3. Update .env on EC2 server
sudo nano /home/advaitam/app/.env
# Change:
#   AWS_ACCESS_KEY_ID=<new_key_id>
#   AWS_SECRET_ACCESS_KEY=<new_secret>

# 4. Restart Gunicorn
sudo systemctl restart advaitam.service

# 5. Verify S3 still works
python manage.py collectstatic --noinput

# 6. Delete the OLD access key from AWS Console
#    (only after confirming new one works)
```

### 🔐 How to rotate SECRET_KEY (the safest approach)

> ⚠️ Rotating `SECRET_KEY` invalidates all existing sessions (all users logged out).
> Do this during low-traffic hours only.

```bash
# 1. Generate new secret key
NEW_SECRET=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo $NEW_SECRET

# 2. Update .env
sudo nano /home/advaitam/app/.env
# Change: SECRET_KEY=<old> → SECRET_KEY=$NEW_SECRET

# 3. Restart Gunicorn
sudo systemctl restart advaitam.service

# 4. Clear all sessions (force re-login)
python manage.py clearsessions
```

---

## 21. Important Production Settings Not Yet Covered

> **UPDATE (Feb 23, 2026):** Audited settings.py - 80% complete. 3 critical fixes needed before deployment.
> See: `deploy/02-DEPLOYMENT-CONCEPTS/PRODUCTION_SETTINGS_AUDIT.md` for detailed audit report.

### ✅ VERIFIED: SESSION_COOKIE_AGE is CORRECT

Your `settings.py` correctly has:
```python
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=86400)  # 24 hours ✅
```

**Status:** GOOD! Users logged out after 24 hours of inactivity (standard for community sites).

> Note: Banking/high-security sites use 30 minutes. Adjust if needed in `.env.production.bak`.

---

### 🔴 CRITICAL #1: ALLOWED_HOSTS is INCOMPLETE

Your `settings.py` has:
```python
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[
    "127.0.0.1",
    "localhost",
    "www.advaitam.info",  # ❌ Missing root domain!
])
```

**Problem:** Missing critical domains!

**Fix Required:** Update `.env.production.bak`:
```bash
ALLOWED_HOSTS=127.0.0.1,localhost,advaitam.info,www.advaitam.info,origin.advaitam.info,<YOUR-EC2-IP>
```

**Why Critical:**
- ❌ If domain NOT in ALLOWED_HOSTS → Django returns 400 Bad Request
- ❌ Common first-deploy gotcha
- ❌ Users can't access your site!

**Domains You Need:**
1. `advaitam.info` - Root domain (MISSING!)
2. `www.advaitam.info` - With www subdomain ✅
3. `origin.advaitam.info` - EC2 direct access (MISSING!)
4. `<YOUR-EC2-IP>` - For debugging without DNS (MISSING!)

---

### 🔴 CRITICAL #2: WhiteNoise Middleware is MISSING

Your `settings.py` MIDDLEWARE list has:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ❌ WHITENOISE MISSING!
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]
```

**Problem:** No static file fallback if S3/CloudFront fails!

**Fix Required:** Add WhiteNoise to MIDDLEWARE:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← ADD THIS LINE
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]
```

Also update STATICFILES_STORAGE in S3 section:
```python
if USE_S3:
    # ...existing S3 config...
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

**Why Critical:**
- ✅ Serves CSS/JS as Nginx fallback if S3 down
- ✅ Prevents "missing stylesheet" production errors
- ✅ Improves reliability
- ✅ Already installed (in requirements-prod.txt)

---

### 🔴 CRITICAL #3: Content Security Policy (CSP) is WRONG

Your `settings.py` incorrectly has:
```python
SECURE_CONTENT_SECURITY_POLICY = True  # ❌ WRONG! This is just a boolean
```

**Problem:** 
- Boolean doesn't DEFINE any CSP rules
- CSP needs dictionary with security rules
- Currently not providing actual protection

**Fix Required:** Replace with proper CSP dictionary:

```python
if not DEBUG:
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'", "https://cdn.jsdelivr.net"),  # Allow CDN if needed
        'style-src': ("'self'", "'unsafe-inline'"),  # Safe for your app
        'img-src': ("'self'", "https:", "data:"),  # Allow images anywhere
        'font-src': ("'self'",),  # Fonts from same origin only
        'connect-src': ("'self'",),  # AJAX/WebSocket from same origin
        'media-src': ("'self'", "https://d-xxxxx.cloudfront.net"),  # CloudFront audio/video
    }
```

**Why Critical:**
- 🛡️ Prevents XSS attacks (malicious scripts injection)
- 🛡️ Protects against clickjacking
- 🛡️ Restricts where resources can be loaded from
- 🛡️ Industry best practice for security

---

### ✅ VERIFIED: Email Configuration is FLEXIBLE

Your `settings.py` has:
```python
EMAIL_BACKEND = env("EMAIL_BACKEND", default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env("EMAIL_HOST", default='smtp.gmail.com')
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default='')
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default='')
```

**Status:** Good! Supports both Gmail and Amazon SES.

**Recommendation:** Use **Amazon SES** in production (cheaper, better deliverability):

```bash
# In .env.production.bak
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_HOST_USER=<SES_SMTP_USERNAME>
EMAIL_HOST_PASSWORD=<SES_SMTP_PASSWORD>
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@advaitam.info
ADMIN_EMAIL=kalyan.py28@gmail.com
```

See `deploy/06-TEMPLATES/.env.prod.template` for details.

---

## Summary of Section 21 Fixes

| Item | Status | Time | Priority |
|------|--------|------|----------|
| SESSION_COOKIE_AGE | ✅ CORRECT | - | - |
| ALLOWED_HOSTS | ❌ INCOMPLETE | 1 min | CRITICAL |
| WhiteNoise Middleware | ❌ MISSING | 2 min | CRITICAL |
| CSP Dictionary | ❌ WRONG | 3 min | CRITICAL |
| Email Config | ✅ FLEXIBLE | - | Good |

**Total Time to Fix:** 7 minutes  
**Impact:** Prevents 400 errors, improves reliability, fixes security

See: `deploy/02-DEPLOYMENT-CONCEPTS/PRODUCTION_SETTINGS_AUDIT.md` for complete audit report.

---

## 22. Deployment Checklist (Final Pre-Production)

> 72 hours before your site goes live, verify every single one of these.

### ⚠️ Code & Configuration

- [ ] `DEBUG=False` in production `.env`
- [ ] `SECRET_KEY` is a long random string (not dev key)
- [ ] `ALLOWED_HOSTS` includes all your domains + EC2 IP
- [ ] `SESSION_COOKIE_AGE=86400` (not 300)
- [ ] `USE_S3=True`
- [ ] `AWS_S3_CUSTOM_DOMAIN` points to CloudFront domain
- [ ] `CSRF_TRUSTED_ORIGINS` lists your HTTPS domains
- [ ] All secrets (AWS keys, Anthropic API, Sentry DSN) are in `.env`, NOT in code
- [ ] `.env` file is in `.gitignore` (never committed)
- [ ] `requirements-prod.txt` is up to date

### ⚠️ Infrastructure

- [ ] EC2 security group allows ports 80, 443, 22 only
- [ ] EC2 has an Elastic IP (public IP won't change)
- [ ] Route 53 DNS records are created (advaitam.info → CloudFront, origin.advaitam.info → EC2)
- [ ] CloudFront is set up with S3 origin (OAC enabled, not public ACLs)
- [ ] S3 bucket has versioning enabled
- [ ] S3 bucket is NOT publicly readable

### ⚠️ SSL & Security

- [ ] SSL certificate obtained: `sudo certbot certificates` shows VALID
- [ ] `SECURE_SSL_REDIRECT = True` in production
- [ ] `SECURE_HSTS_SECONDS = 31536000` set
- [ ] `SECURE_PROXY_SSL_HEADER` set to trust Nginx

### ⚠️ Database

- [ ] PostgreSQL is running: `sudo systemctl status postgresql`
- [ ] Database user created with strong password
- [ ] Database is NOT publicly accessible (no inbound on 5432 from anywhere)
- [ ] Backup script is in place: `/home/advaitam/backups/backup-db.sh`
- [ ] Test restore has been done successfully

### ⚠️ Monitoring & Alerts

- [ ] Sentry DSN is in `.env` and active (test: visit `/error-test/` and check Sentry)
- [ ] Email alerts configured in Sentry
- [ ] Uptime robot monitoring configured (uptimerobot.com)
- [ ] Email notifications enabled for failed checks
- [ ] CloudWatch alarms set (CPU, memory, disk space)

### ⚠️ Deployment & Rollback

- [ ] `deploy.sh` has been tested end-to-end on a test EC2
- [ ] Git repo is public or has deploy credentials set up
- [ ] You have a rollback plan (know how to `git revert` and restart)
- [ ] You have a maintenance window time window (2 AM, low traffic)

### ⚠️ Testing

- [ ] `curl https://advaitam.info/` returns 200
- [ ] `curl https://www.advaitam.info/` redirects correctly
- [ ] Static CSS loads: `https://<cloudfront-domain>/static/css/home.css`
- [ ] Login page works
- [ ] File download works (if applicable)
- [ ] Email sending works (password reset email)
- [ ] Sentry receives test errors
- [ ] All 10 health checks from Section 13 pass

---



