# 🚀 Advaitam — AWS Production Deployment Guide
## Budget: Under $10/month | Domain: advaitam.info
### ✅ Verified against actual app code — February 2026

---

## 🗺️ BIG PICTURE — Complete Deployment Flow

> **Read this first. Understand the full picture before touching anything.**

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║              YOUR WINDOWS MACHINE  (D:\webProject)                             ║
║                                                                                  ║
║   Django App Code                                                                ║
║   ├── webapp/          (views, models, urls, forms, services/claude_service.py) ║
║   ├── webProject/      (settings.py, wsgi.py, urls.py)                          ║
║   ├── static/          (css, js, images, audio/, books/)                         ║
║   ├── gunicorn.conf.py                                                           ║
║   ├── requirements-prod.txt                                                      ║
║   └── .gitignore       (.env is EXCLUDED from git — never committed)             ║
╚══════════════════════╦═══════════════════════════════════════════════════════════╝
                       ║
                       ║  git push origin main
                       ║  (Phase 3, Step 3.7)
                       ▼
╔══════════════════════════════════════════════════════════════════════════════════╗
║                        GITHUB (private repo)                                    ║
║              https://github.com/KYALLAMRAJU/website                             ║
╚══════════════════════╦═══════════════════════════════════════════════════════════╝
                       ║
                       ║  git clone / git pull
                       ║  (Phase 3, Step 3.8)
                       ▼
╔══════════════════════════════════════════════════════════════════════════════════╗
║                   AWS EC2 t4g.micro  (Ubuntu 24.04 ARM64)                       ║
║                   Elastic IP: XX.XX.XX.XX                                        ║
║                                                                                  ║
║  /home/advaitam/app/          ← your Django project lives here                  ║
║  /home/advaitam/venv/         ← Python 3.12 virtual env + all packages          ║
║  /home/advaitam/app/.env      ← production secrets (chmod 600, never in git)    ║
║  /home/advaitam/app/logs/     ← gunicorn + nginx + django logs                  ║
║                                                                                  ║
║   ┌─────────────────────────────────────────────────────────────────────────┐   ║
║   │  PostgreSQL 16  (localhost:5432)                                         │   ║
║   │  Database: advaitam_db   User: advaitam_user                             │   ║
║   │  Tables: auth_user, webapp_contacus, webapp_wishdata,                    │   ║
║   │          webapp_aboutdetails, webapp_author, webapp_book,                │   ║
║   │          django_session, authtoken_token ...                             │   ║
║   └──────────────────────────────┬──────────────────────────────────────────┘   ║
║                                  │ SQL queries                                   ║
║   ┌──────────────────────────────▼──────────────────────────────────────────┐   ║
║   │  Gunicorn  (2 workers × 2 threads = 4 concurrent requests)              │   ║
║   │  Unix socket: /run/advaitam/gunicorn.sock                                │   ║
║   │  Config: gunicorn.conf.py   (timeout=120 for audio streaming)           │   ║
║   │  Managed by: systemd  (advaitam.service + advaitam.socket)               │   ║
║   └──────────────────────────────┬──────────────────────────────────────────┘   ║
║                                  │ HTTP via Unix socket                          ║
║   ┌──────────────────────────────▼──────────────────────────────────────────┐   ║
║   │  Nginx  (port 80 → redirect, port 443 → proxy to Gunicorn)              │   ║
║   │  SSL cert: Let's Encrypt for origin.advaitam.info                        │   ║
║   │  Origin protection: checks X-CloudFront-Secret header                   │   ║
║   │  (blocks anyone hitting EC2 directly without going through CloudFront)  │   ║
║   └──────────────────────────────┬──────────────────────────────────────────┘   ║
╚══════════════════════════════════╬═══════════════════════════════════════════════╝
                                   ║ HTTPS (port 443)
                                   ║ origin.advaitam.info → EC2 Elastic IP
                                   ║
╔══════════════════════════════════╩═══════════════════════════════════════════════╗
║                         AWS SERVICES  (all in us-east-1)                        ║
║                                                                                  ║
║   ┌──────────────────────────────────────────────────────────────────────────┐  ║
║   │  S3 Bucket: advaitam-assets  (Block Public Access = ON)                  │  ║
║   │                                                                           │  ║
║   │  static/                  ← uploaded by: python manage.py collectstatic  │  ║
║   │  ├── css/home.css                                                         │  ║
║   │  ├── js/   (other JS files)                                               │  ║
║   │  ├── images/  (4 images)                                                  │  ║
║   │  ├── audio/              ← uploaded separately: aws s3 sync (.mp3 only)  │  ║
║   │  │   ├── bhagavadgita/   (NOT via collectstatic — .mp3s not in git)       │  ║
║   │  │   ├── grantha/                                                         │  ║
║   │  │   ├── sutra/                                                           │  ║
║   │  │   ├── upanisad/                                                        │  ║
║   │  │   └── vidyaranya/                                                      │  ║
║   │  ├── books/Django.pdf                                                     │  ║
║   │  └── admin/  (Django admin CSS/JS)                                        │  ║
║   │  media/  (empty now — ready for future user uploads)                     │  ║
║   └──────────────────────────────────────────────────────────────────────────┘  ║
║                      ▲  OAC (Origin Access Control) — private access only       ║
║   ┌──────────────────┴───────────────────────────────────────────────────────┐  ║
║   │  CloudFront CDN  (xxxxxxxxxxxx.cloudfront.net)                            │  ║
║   │                                                                           │  ║
║   │  /static/*  ──────────────────────────────────────► S3 (1-yr cache)      │  ║
║   │  /media/*   ──────────────────────────────────────► S3 (7-day cache)     │  ║
║   │  /*  (all other paths) ────────────────────────────► EC2 Nginx (no cache)│  ║
║   │                                                                           │  ║
║   │  SSL cert: ACM  *.advaitam.info  (must be in us-east-1!)                 │  ║
║   │  CNAMEs: advaitam.info, www.advaitam.info                                 │  ║
║   └──────────────────────────────────────────────────────────────────────────┘  ║
║                      ▲                                                           ║
║   ┌──────────────────┴───────────────────────────────────────────────────────┐  ║
║   │  Route 53 DNS                                                             │  ║
║   │  advaitam.info     ──── A Alias ────► CloudFront                         │  ║
║   │  www.advaitam.info ──── A Alias ────► CloudFront                         │  ║
║   │  origin.advaitam.info ─ A Record ───► EC2 Elastic IP (XX.XX.XX.XX)       │  ║
║   └──────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                  ║
║   ┌──────────────────────────────────────────────────────────────────────────┐  ║
║   │  AWS SES  (Simple Email Service)  — region: us-east-1                    │  ║
║   │                                                                           │  ║
║   │  Triggered by Django when:                                                │  ║
║   │   • User registers → welcome / verification email                        │  ║
║   │   • User requests password reset → reset-link email                      │  ║
║   │   • User submits contact form → notification email to admin              │  ║
║   │                                                                           │  ║
║   │  Transport : SMTP (port 587, STARTTLS)                                   │  ║
║   │  Auth      : SES SMTP credentials (IAM user, NOT AWS access keys)        │  ║
║   │  From addr : noreply@advaitam.info  (domain verified in SES)             │  ║
║   │  Sandbox → Production access must be requested from AWS                  │  ║
║   └──────────────────────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
                                   ▲
                                   ║  HTTPS request to https://advaitam.info/
                                   ║
╔══════════════════════════════════╩═══════════════════════════════════════════════╗
║                        END USER'S BROWSER                                        ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

---

## 🔁 REQUEST FLOW — What Happens When a User Visits Your Site

```
User types: https://advaitam.info/home/
                │
                ▼
        Route 53  ──────────────────────────────────► CloudFront
        (DNS lookup)                                        │
                                                           │
                          ┌────────────────────────────────┤
                          │                                │
                   Is it /static/*                   Is it /*
                   or /media/* ?                   (Django pages)?
                          │                                │
                          ▼                                ▼
                    ──────────                    ──────────────────
                   │    S3      │                │  EC2 Nginx        │
                   │ home.css   │                │  (origin.advai..) │
                   │ audio/...  │                │        │          │
                   │ images/... │                │  (Unix socket)    │
                    ──────────                   │        │          │
                   Served from                   │  Django 5.2       │
                   global edge                   │  webProject/      │
                   cache ✅                      │        │          │
                                                 │  PostgreSQL 16    │
                                                 │  advaitam_db      │
                                                  ──────────────────
                                                 HTML response back
                                                 to user ✅

                                    ┌────────────────────────────────────┐
                                    │  When does Django send email?      │
                                    │                                    │
                                    │  /signupform/   → welcome email    │
                                    │  /forgotpassword/ → reset link     │
                                    │  /contact-submit/ → admin alert    │
                                    │                │                   │
                                    │                ▼                   │
                                    │       AWS SES  (us-east-1)         │
                                    │       SMTP port 587 / STARTTLS     │
                                    │       From: noreply@advaitam.info  │
                                    │                │                   │
                                    │                ▼                   │
                                    │       Recipient's inbox ✅         │
                                    └────────────────────────────────────┘
```

---

## ⚙️ YOUR APP AT A GLANCE — What Gets Deployed

```
URL                          → View Function / Class         → What It Does
─────────────────────────────────────────────────────────────────────────────
/                            → (no root view)                → 302 to /loginpage/
/loginpage/                  → loginForm_view                → Login with email+password
/signupform/                 → signupForm_view               → Create account + email sent ✉️
/forgotpassword/             → forgotpasswordForm_view       → Reset password + email sent ✉️
/home/            🔒         → homepage_view                 → Main home page
/about/           🔒         → aboutpage_view                → About section (4 phases)
/audio/           🔒         → audiopage_view                → Audio recitations
/books/           🔒         → books_view                    → PDF books
/gallery/         🔒         → gallery_view                  → Image gallery
/contact-submit/  🔒         → contact_view                  → Contact form (emails admin) ✉️
/claude/                     → claude_page / claude_api      → Claude AI chat (Anthropic)
/admin/                      → Django Admin                  → Superuser dashboard
/api/docs/                   → SpectacularSwaggerView        → Swagger API docs
/api/redoc/                  → SpectacularRedocView          → ReDoc API docs
/apimodelviewset/            → DRFModelViewSet               → REST API (session auth)

🔒 = requires login  (LOGIN_URL = /loginpage/)
✉️ = triggers AWS SES email  (noreply@advaitam.info → recipient)
```

---

## 📦 TECHNOLOGY STACK — What Runs in Production

```
Layer               Technology              Config File / Location
──────────────────────────────────────────────────────────────────────────
Web Server        │ Nginx 1.24             │ /etc/nginx/sites-available/advaitam
App Server        │ Gunicorn 23            │ /home/advaitam/app/gunicorn.conf.py
App Framework     │ Django 5.2.9           │ /home/advaitam/app/webProject/settings.py
Language          │ Python 3.12            │ /home/advaitam/venv/
Database          │ PostgreSQL 16          │ localhost:5432 / advaitam_db
Static/Media CDN  │ CloudFront + S3        │ .env → AWS_S3_CUSTOM_DOMAIN
SSL (EC2)         │ Let's Encrypt (certbot)│ /etc/letsencrypt/live/origin.advaitam.info/
SSL (CloudFront)  │ AWS ACM                │ *.advaitam.info (us-east-1 ONLY)
DNS               │ Route 53               │ advaitam.info hosted zone
Password Hash     │ Argon2                 │ settings.py → PASSWORD_HASHERS
AI Integration    │ Anthropic Claude       │ webapp/services/claude_service.py
Email             │ AWS SES (SMTP)         │ .env → AWS_SES_REGION_NAME / EMAIL_HOST_USER
Sessions          │ DB-backed (PostgreSQL) │ settings.py (no Redis needed)
Process Manager   │ systemd                │ /etc/systemd/system/advaitam.service
Secrets           │ .env (chmod 600)       │ /home/advaitam/app/.env
```

---

## ⚠️ PRE-FLIGHT: Changes Already Made to Your Code

Before you start, these fixes have already been applied to your codebase:

| File | What Was Fixed |
|---|---|
| `webapp/views.py` | Removed 6 dangerous `print()` statements leaking passwords + password hashes |
| `webapp/utils.py` | Removed debug `print(type(id))` / `print("inside id is not in")` |
| `webapp/custompermission.py` | Removed `print(request.method)` on every API request |
| `webapp/serializers.py` | Removed `print()` in validator (fired on every API call) |
| `webProject/settings.py` | WhiteNoise now conditional (off when `USE_S3=True`); added `CLOUDFRONT_SECRET` |
| `.env.production.bak` | Added `DJANGO_ENV=production` (was missing — production settings wouldn't activate!) |
| `deploy.sh` | Added `Environment=DJANGO_ENV=production` to systemd service unit |
| `webapp/services/__init__.py` | Created missing `__init__.py` for the services Python package |

---

## 🗺️ CORRECT EXECUTION ORDER (Follow This Exactly)

> ⚠️ **IMPORTANT — The phases in this document are NOT numbered in execution order.**
> Phase 7 (ACM Certificate) MUST be done BEFORE Phase 4 (CloudFront).
> Route 53 DNS (Phase 5) MUST be started early so DNS has time to propagate.
> Follow the steps below in ORDER — do not skip ahead.

```
STEP 1  → Phase 1  — AWS Account + IAM user + IAM Role + AWS CLI on Windows
            ✅ You get: AWS account ready, admin user, EC2 IAM role, CLI working

STEP 2  → Phase 2  — S3 bucket + OAC (Steps 2.1, 2.2, 2.3 ONLY — skip 2.4 for now)
            ✅ You get: S3 bucket created, OAC ready
            ⏸️  SKIP Step 2.4 (bucket policy) — needs CloudFront ID which you don't have yet

STEP 3  → Phase 3  — EC2 launch, server setup, PostgreSQL, code, venv, .env, migrate
            ✅ You get: Django app running on EC2 (not yet accessible on the internet)
            ⚠️  Do NOT run collectstatic yet — S3/CloudFront not set up yet

STEP 4  → Phase 5  — Route 53: create hosted zone + update nameservers at registrar
            ✅ You get: Route 53 managing your domain
            ⚠️  Do this NOW — DNS propagation takes up to 48 hours — start it early!
            ⏭️  You can continue to Step 5 while DNS propagates in the background

STEP 5  → Phase 7  — ACM Certificate (MUST be in us-east-1, MUST be done before CloudFront)
            ✅ You get: SSL certificate with status "Issued"
            ⚠️  Switch AWS Console region to us-east-1 before requesting
            ⚠️  Wait for status → "Issued" before moving on (5–30 minutes)

STEP 6  → Phase 4  — CloudFront distribution (cert is "Issued" + Route 53 is ready)
            ✅ You get: CloudFront URL (xxxxxxxxxxxx.cloudfront.net)
            → Then complete Phase 2 Step 2.4 (S3 bucket policy) using your CloudFront ID
            → Update .env on EC2: AWS_S3_CUSTOM_DOMAIN=xxxxxxxxxxxx.cloudfront.net
            → Run collectstatic (uploads CSS/JS/images/books to S3)
            → Upload audio files: aws s3 sync static/audio/ s3://advaitam-assets/static/audio/

STEP 7  → Phase 5 cont. — Create DNS A records in Route 53 (3 records for the 3 domains)
            ✅ You get: advaitam.info → CloudFront, origin.advaitam.info → EC2

STEP 8  → Phase 6  — Gunicorn + Nginx + certbot SSL for origin.advaitam.info
            ⚠️  Before certbot: nslookup origin.advaitam.info MUST return your EC2 Elastic IP
            ✅ You get: full production stack running over HTTPS

STEP 9  → Phase 8  — Final verification (test all URLs, emails, static files, audio)
            ✅ You get: confirmed working deployment

STEP 10 → Phase 9  — Security hardening (SSH, UFW firewall, security group)

STEP 11 → Phase 10 — Monitoring (CloudWatch alarms, budget alert, log rotation, Sentry)
```

---

## 📊 Architecture Overview
                        ┌─────────────────────────────────────────────┐
                        │              INTERNET USERS                  │
                        └──────────────────┬──────────────────────────┘
                                           │
                        ┌──────────────────▼──────────────────────────┐
                        │         Route 53 (advaitam.info)             │
                        │  advaitam.info  → CloudFront (Alias)         │
                        │  www.advaitam.info → CloudFront (Alias)      │
                        │  origin.advaitam.info → EC2 Elastic IP       │
                        └──────┬───────────────────────┬──────────────┘
                               │                       │
               ┌───────────────▼────────┐    ┌─────────▼──────────────┐
               │  CloudFront CDN         │    │   EC2 t4g.micro        │
               │  (Global Edge Cache)    │    │   Ubuntu 24.04 ARM64   │
               │  /static/* → S3         │    │                        │
               │  /media/*  → S3         │    │  ┌──────────────────┐  │
               │  /*  → EC2 origin       │───►│  │  Nginx (80/443)  │  │
               └────────────────────────┘    │  │  Let's Encrypt   │  │
                                             │  └────────┬─────────┘  │
               ┌────────────────────────┐    │           │             │
               │  S3: advaitam-assets   │    │  ┌────────▼─────────┐  │
               │  /static/              │    │  │  Gunicorn        │  │
               │    css/home.css        │◄───│  │  2 workers       │  │
               │    js/ (other JS)      │    │  │  2 threads each  │  │
               │    images/             │    │  │  Unix socket     │  │
               │    audio/ (.mp3 via    │    │  └────────┬─────────┘  │
               │      aws s3 sync)      │    │           │             │
               │    admin/              │    │  ┌────────▼─────────┐  │
               │  /media/ (future use)  │    │  │ Django 5.2       │  │
               └────────────────────────┘    │  │ Python 3.12      │  │
                                             │  └────────┬─────────┘  │
               ┌────────────────────────┐    │           │             │
               │  ACM Certificate       │    │  ┌────────▼─────────┐  │
               │  *.advaitam.info SSL   │    │  │ PostgreSQL 16    │  │
               └────────────────────────┘    │  │ localhost only   │  │
                                             │  │ advaitam_db      │  │
                                             │  └──────────────────┘  │
                                             └────────────────────────┘

               ┌────────────────────────┐
               │  AWS SES  (us-east-1)  │◄── Django SMTP outbound email:
               │  SMTP port 587 / TLS   │     /signupform/     → welcome email
               │  From:                 │     /forgotpassword/ → reset link
               │  noreply@advaitam.info │     /contact-submit/ → admin alert
               └────────────────────────┘
```

**Key facts about YOUR app:**
- Django 5.2.9 | Python 3.12 | Gunicorn 23 | PostgreSQL 16
- Static: CSS, JS, images, audio (5 folders: bhagavadgita, grantha, sutra, upanisad, vidyaranya), books (PDFs)
- No user file uploads currently (`MediaStorage` is ready but not yet used)
- Sessions: DB-backed (no Redis/ElastiCache needed → saves ~$12/mo)
- Claude AI integration via `webapp/services/claude_service.py` → needs `ANTHROPIC_API_KEY`
- Email: **AWS SES** (SMTP port 587, STARTTLS) — signup confirmation + password reset + contact form alert → `noreply@advaitam.info`

---

## 💰 Cost Breakdown (After Free Tier)

> 💡 **Teacher's note:** AWS charges you per hour for EC2, per GB for S3, and per GB transferred
> for CloudFront. The numbers below are real estimates for a low-traffic site like yours.
> In your first 12 months everything is basically free due to the AWS Free Tier.

| AWS Service | Config | Monthly Cost |
|---|---|---|
| EC2 t4g.micro | On-Demand | ~$6.05 |
| EBS gp3 20GB | EC2 root volume | ~$1.60 |
| S3 Standard | ~10GB static + audio | ~$0.50 |
| CloudFront | ~50GB/mo transfer out | ~$0.43 |
| Route 53 | 1 hosted zone | $0.50 |
| ACM Certificate | Free with CloudFront | $0.00 |
| AWS SES | First 62,000 emails/mo free (from EC2) | $0.00 |
| ElastiCache | ❌ SKIP — DB sessions | $0.00 |
| RDS | ❌ SKIP — PostgreSQL on EC2 | $0.00 |
| **TOTAL** | | **~$9.08/mo** |

> **💡 Free Tier (First 12 months):** EC2, EBS (30GB), S3 (5GB), CloudFront (1TB) are FREE.
> **💡 SES Free Tier:** 62,000 emails/month FREE when sent from an EC2 instance. More than enough for this app.

---

## 📋 PHASE 1 — AWS Account Setup

> 🎓 **What is this phase?**
> Before you can use any AWS service, you need an account. Think of it like creating a Google
> account before using Gmail — except AWS will charge your credit card for what you use.
> We will also create a safer "sub-user" (IAM user) so we never use the root account for daily work.

---

### Step 1.1 — Create Your AWS Account

**Why:** You need an AWS account to access EC2, S3, CloudFront, Route 53, SES, and ACM.

**What to do:**
1. Open your browser and go to → **https://aws.amazon.com**
2. Click the orange **"Create an AWS Account"** button in the top-right corner
3. Fill in:
   - **Email address** → use a real email you check (this is your root account email)
   - **Password** → use a strong password (16+ characters)
   - **Account name** → `advaitam` (just a label for yourself)
4. Choose **"Personal"** account type
5. Enter your credit/debit card details (you will NOT be charged unless you exceed free tier)
6. Complete phone verification
7. Choose **"Basic Support"** (free — you don't need paid support)

📸 **What you will see after signup:**
```
┌─────────────────────────────────────────────────┐
│  AWS Management Console                         │
│                                                 │
│  Hello, [your name]                             │
│                                                 │
│  Recently visited services:                     │
│  (empty for now)                                │
│                                                 │
│  Region selector (top right): US East (N.Virginia)│
└─────────────────────────────────────────────────┘
```

> ⚠️ **IMPORTANT — Set your region to us-east-1 right now:**
> Look at the top-right corner of the console. You will see a region name like "Ohio" or
> "Global". Click it and select **"US East (N. Virginia) us-east-1"**.
> Use this region for EVERYTHING in this guide. Never switch regions unless told to.

---

### Step 1.2 — Enable MFA on Root Account (Do This Immediately)

**Why:** If someone steals your root password, they can delete everything and run up a
$10,000 bill. MFA adds a second factor (your phone) so they can't get in even with the password.

**What to do:**
1. Click your account name (top-right) → **"Security credentials"**
2. Scroll down to **"Multi-factor authentication (MFA)"**
3. Click **"Assign MFA device"**
4. Choose **"Authenticator app"** → Next
5. Open Google Authenticator or Authy on your phone → scan the QR code
6. Enter two consecutive codes from your phone → Click **"Add MFA"**

📸 **What you will see:**
```
Multi-factor authentication (MFA)
  Status: ✅ MFA assigned
  Device: arn:aws:iam::123456789012:mfa/root-account-mfa
```

---

### Step 1.3 — Create an IAM Admin User (Never Work as Root)

**Why:** The root account is like the BIOS of your computer — you only use it for emergencies.
For day-to-day work, create a separate IAM user with admin rights. This limits the damage if
something goes wrong.

**What to do:**
1. In the AWS Console search bar (top), type **"IAM"** → click IAM
2. In the left sidebar → click **"Users"**
3. Click the orange **"Create user"** button

📸 **What you will see on the "Create user" page:**
```
Step 1: Specify user details
  User name: advaitam-admin          ← type this
  ☑ Provide user access to the AWS Management Console
    → I want to create an IAM user (select this)
    Console password: Custom password → type a strong password
    ☐ Users must create a new password at next sign-in (uncheck this)
```

4. Click **Next**
5. On "Set permissions" page:
   - Choose **"Attach policies directly"**
   - Search for `AdministratorAccess` → check the box next to it

📸 **What you will see:**
```
Permissions policies
  Filter: AdministratorAccess
  ☑ AdministratorAccess    AWS managed - job function
```

6. Click **Next** → **Create user**
7. On the confirmation page → click **"Download .csv file"** → save it safely

> ⚠️ The CSV file contains your login URL and password. Keep it safe. You will need it to log in
> as this IAM user instead of root.

**Log out of root, log in as IAM user from now on:**
```
Your IAM sign-in URL looks like:
https://123456789012.signin.aws.amazon.com/console
(Find this on the IAM → Dashboard page under "AWS Account" section)
```

---

### Step 1.4 — Create EC2 IAM Instance Role (So EC2 Can Access S3 Without Keys)

**Why:** Your Django app on EC2 needs to upload/read files from S3. Instead of putting AWS
access keys in your `.env` file (which is a security risk), we attach a "role" to the EC2
instance. The instance automatically gets temporary credentials — no keys needed.
Think of it like a staff badge that lets an employee enter the building without a key.

**What to do:**
1. Go to **IAM** → left sidebar → **"Roles"**
2. Click **"Create role"**

📸 **Step 1 — Select trusted entity:**
```
Trusted entity type: ● AWS service   ← select this
Use case: EC2                         ← select EC2 from the list
```

3. Click **Next**
4. Search for and check these two policies:
   - `AmazonS3FullAccess`
   - `AmazonSESFullAccess`

📸 **What you will see:**
```
Add permissions
  ☑ AmazonS3FullAccess       AWS managed
  ☑ AmazonSESFullAccess      AWS managed
```

5. Click **Next**
6. Role name: `advaitam-ec2-role`
7. Click **"Create role"**

📸 **Success message:**
```
✅ Role advaitam-ec2-role created successfully
```

> 💡 You will attach this role to your EC2 instance in Phase 3. That's all it takes —
> no AWS_ACCESS_KEY_ID needed in your .env file for S3 access.

---

### Step 1.5 — Install and Configure AWS CLI on Your Windows Machine

**Why:** The AWS CLI (Command Line Interface) lets you run AWS commands from PowerShell on
your Windows machine. You need it to:
- Upload your audio `.mp3` files directly to S3 (they are never in git)
- Verify files in S3 (`aws s3 ls`)
- Any future S3 management

**Install:**
```powershell
# Open PowerShell as Administrator and run:
winget install Amazon.AWSCLI
```

> If `winget` is not available, download the installer from:
> https://aws.amazon.com/cli/ → click "Download AWS CLI MSI installer for Windows"

Close PowerShell and reopen it, then verify:
```powershell
aws --version
# Should print: aws-cli/2.x.x Python/3.x.x Windows/...
```

**Configure with your IAM user credentials:**
```powershell
aws configure
```

📸 **You will be prompted — fill in each line:**
```
AWS Access Key ID [None]:     AKIAXXXXXXXXXXXXXXXX
                              ↑ from the CSV file you downloaded in Step 1.3
AWS Secret Access Key [None]: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                              ↑ also from the CSV
Default region name [None]:   us-east-1
Default output format [None]: json
```

**Verify it works:**
```powershell
aws sts get-caller-identity
```

📸 **Expected output:**
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/advaitam-admin"
}
```

> ✅ AWS CLI is now ready. On your **EC2 server** you do NOT need to configure the CLI —
> the EC2 IAM Role (Step 1.4) gives it automatic S3 and SES access with no keys required.

---

## 📋 PHASE 2 — S3 Bucket Setup

> 🎓 **What is this phase?**
> S3 (Simple Storage Service) is Amazon's file storage. Your CSS, JS, images, audio files,
> and PDF books will live here. CloudFront will then serve them globally from edge locations
> close to your users — much faster than serving from your EC2 server.
>
> Think of S3 as a hard drive in the cloud, and CloudFront as a delivery network that
> copies your files to servers worldwide so users get them quickly.

---

### Step 2.1 — Create the S3 Bucket

**Why:** You need one bucket to store all your static and media files.

**What to do:**
1. In the AWS Console search bar → type **"S3"** → click S3
2. Click the orange **"Create bucket"** button

📸 **Fill in the form:**
```
General configuration
  Bucket name: advaitam-assets        ← must be globally unique
  AWS Region: US East (N. Virginia) us-east-1   ← MUST be us-east-1

Object Ownership
  ● ACLs disabled (recommended)       ← select this

Block Public Access settings for this bucket
  ☑ Block all public access           ← KEEP THIS CHECKED
    (CloudFront will access it privately via OAC — users never hit S3 directly)

Bucket Versioning
  ● Disable                           ← saves cost, we don't need versions

Default encryption
  ● Server-side encryption with Amazon S3 managed keys (SSE-S3)   ← default is fine
```

3. Scroll down → Click **"Create bucket"**

📸 **What you will see:**
```
✅ Successfully created bucket "advaitam-assets"
```

> ⚠️ **Why block public access?** Because CloudFront (not the public) reads from S3.
> Users access files via `https://xxxx.cloudfront.net/static/...` not via S3 URLs directly.
> This is more secure and cheaper (CloudFront caches = fewer S3 reads).

---

### Step 2.2 — Create CloudFront Origin Access Control (OAC)

**Why:** OAC is like a VIP pass that only CloudFront has. When CloudFront requests a file
from S3, it signs the request with this OAC. S3 checks the signature and only serves the
file if it's from your CloudFront distribution — nobody else can read your S3 files.

**What to do:**
1. In the search bar → type **"CloudFront"** → click CloudFront
2. In the left sidebar → click **"Origin access"**
3. Click **"Create control setting"**

📸 **Fill in:**
```
Name: advaitam-oac
Description: OAC for advaitam-assets S3 bucket
Signing behavior: ● Sign requests (recommended)
Origin type: S3
```

4. Click **"Create"**

📸 **What you will see:**
```
✅ Origin access control advaitam-oac has been created
ID: E1XXXXXXXXXXXX   ← save this, you need it when creating the CloudFront distribution
```

---

### Step 2.3 — S3 Bucket Policy (Do This AFTER Phase 4 — CloudFront is ready)

> ⏸️ **PAUSE — Do not do this step yet.**
> You need your CloudFront Distribution ID first (created in Phase 4).
> Come back here after Phase 4 is complete.

**When you come back, here's what to do:**
1. Go to S3 → click **"advaitam-assets"** bucket
2. Click the **"Permissions"** tab
3. Scroll to **"Bucket policy"** → click **"Edit"**
4. Paste this JSON (replace the two placeholder values):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontOAC",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::advaitam-assets/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```

**How to find YOUR_ACCOUNT_ID:**
- Click your account name (top-right of console) → you will see a 12-digit number like `123456789012`

**How to find YOUR_DISTRIBUTION_ID:**
- CloudFront → Distributions → look at the "ID" column, e.g. `E1ABCD2EFGH3IJ`

5. Click **"Save changes"**

📸 **What you will see:**
```
✅ Successfully edited bucket policy
```

---

## 📋 PHASE 3 — EC2 Server Setup + App Deployment

> 🎓 **What is this phase?**
> EC2 (Elastic Compute Cloud) is your virtual server in the cloud. Think of it as renting
> a Linux computer in Amazon's data center. You will:
> - Launch the server (like turning on a new computer)
> - Install Python, PostgreSQL, Nginx
> - Copy your Django code onto it
> - Create the .env file with your production secrets
> - Run database migrations

---

### Step 3.1 — Launch Your EC2 Instance

**Why:** This is the actual server that will run your Django app 24/7.

**What to do:**
1. In the search bar → type **"EC2"** → click EC2
2. Click **"Launch instance"** (orange button)

📸 **Fill in each section carefully:**

**Name and tags:**
```
Name: advaitam-web
```

**Application and OS Images (AMI):**
```
→ Click "Browse more AMIs"
→ Search: "Ubuntu 24.04"
→ Filter Architecture: ARM64   ← CRITICAL — must be ARM64 for t4g instances
→ Select: Ubuntu Server 24.04 LTS (HVM), SSD Volume Type  (ARM64)
```
> ⚠️ If you pick the wrong architecture (x86 instead of ARM64), the t4g.micro instance
> type will not appear. ARM64 = cheaper and faster for this use case.

**Instance type:**
```
t4g.micro   ← search for this, it costs ~$6/month
             (t4g = ARM-based Graviton, micro = smallest size)
```

**Key pair (login):**
```
→ Click "Create new key pair"
  Key pair name: advaitam-key
  Key pair type: RSA
  Private key file format: .pem  (for SSH from Windows/Mac/Linux)
→ Click "Create key pair"
→ A file "advaitam-key.pem" will download automatically
```
> ⚠️ Save this .pem file somewhere safe (e.g. `C:\Users\YourName\.ssh\advaitam-key.pem`).
> If you lose it, you CANNOT SSH into your server. There is no recovery.

**Network settings:**
```
→ Click "Edit" (top right of Network settings section)
VPC: default VPC is fine
Subnet: No preference (any AZ)
Auto-assign public IP: Enable

Firewall (security groups):
→ Select "Create security group"
  Security group name: advaitam-sg

Add these rules:
  Type: SSH    Protocol: TCP  Port: 22   Source: My IP    ← only YOUR current IP
  Type: HTTP   Protocol: TCP  Port: 80   Source: 0.0.0.0/0 (Anywhere)
  Type: HTTPS  Protocol: TCP  Port: 443  Source: 0.0.0.0/0 (Anywhere)
```

**Configure storage:**
```
1 x  20 GiB   gp3   ← change from default 8GB to 20GB
                      (your audio files need space)
```

**Advanced details:**
```
IAM instance profile: advaitam-ec2-role   ← select the role from Phase 1
```

3. Click the orange **"Launch instance"** button

📸 **Success page:**
```
✅ Successfully initiated launch of instance
  Instance ID: i-0xxxxxxxxxxxxxxxxx
  
→ Click "View all instances"
→ Wait 1-2 minutes for "Instance state" to show: ● Running
→ Wait for "Status check" to show: ✅ 2/2 checks passed
```

---

### Step 3.2 — Allocate an Elastic IP Address

**Why:** By default, your EC2 server gets a new public IP every time it restarts. An Elastic IP
is a fixed IP that stays the same forever — even after reboots. Your DNS records will point to
this fixed IP.

**What to do:**
1. In the EC2 left sidebar → scroll down to **"Network & Security"** → click **"Elastic IPs"**
2. Click **"Allocate Elastic IP address"**

📸 **Settings:**
```
Network Border Group: us-east-1   ← default is fine
Public IPv4 address pool: Amazon's pool of IPv4 addresses  ← default
```

3. Click **"Allocate"**

📸 **Result:**
```
✅ New address request succeeded
  Allocated IPv4 address: 54.XXX.XXX.XXX   ← write this down!
```

4. Now associate it with your instance:
   - Check the checkbox next to your new Elastic IP
   - Click **"Actions"** → **"Associate Elastic IP address"**

📸 **Associate form:**
```
Resource type: ● Instance
Instance: i-0xxxxxxxxxxxxxxxxx   ← select your advaitam-web instance
Private IP address: (leave default)
☐ Allow this Elastic IP address to be reassociated
```

5. Click **"Associate"**

> 💡 Write down your Elastic IP: `54.XXX.XXX.XXX` — you will use it many times throughout
> this guide wherever you see `XX.XX.XX.XX`.

---

### Step 3.3 — SSH Into Your Server for the First Time

**Why:** SSH (Secure Shell) is how you type commands on your remote Linux server from your
Windows machine. Think of it as a remote terminal into the cloud.

**On Windows — fix the key file permissions first:**
```powershell
# Open PowerShell (not Command Prompt) and run:
icacls "C:\Users\YourName\.ssh\advaitam-key.pem" /inheritance:r
icacls "C:\Users\YourName\.ssh\advaitam-key.pem" /grant:r "%USERNAME%:R"
```
> If you skip this, SSH will complain "Permissions are too open" and refuse to connect.

**Now connect:**
```powershell
ssh -i "C:\Users\YourName\.ssh\advaitam-key.pem" ubuntu@54.XXX.XXX.XXX
```

📸 **First time connecting you will see:**
```
The authenticity of host '54.XXX.XXX.XXX' can't be established.
ED25519 key fingerprint is SHA256:xxxxxxxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no/[fingerprint])? 
```
Type `yes` and press Enter. This is normal — it's just confirming the server identity.

📸 **Successful connection looks like:**
```
Welcome to Ubuntu 24.04.1 LTS (GNU/Linux 6.8.0-1018-aws aarch64)

ubuntu@ip-172-31-XX-XX:~$
```
You are now inside your server. The `ubuntu@ip-172-31-XX-XX:~$` is the Linux prompt.

---

### Step 3.4 — Install Everything the Server Needs

**Why:** A fresh Ubuntu server has almost nothing installed. We need Python 3.12, PostgreSQL
(database), Nginx (web server), and Git (to pull your code).

**Run these commands one by one** (copy-paste each block):

```bash
# Update package lists and upgrade existing packages
sudo apt update && sudo apt upgrade -y
```
> This may take 2-3 minutes. You'll see a lot of output — that's normal.

```bash
# Install everything we need in one command
sudo apt install -y python3.12 python3.12-venv python3-pip \
                    postgresql postgresql-contrib libpq-dev \
                    nginx git curl build-essential
```
> This installs: Python 3.12, PostgreSQL, `libpq-dev` (**required** — without it `psycopg2` will
> fail to install), Nginx web server, Git, curl, and C build tools.

📸 **Verify installs worked:**
```bash
python3.12 --version    # should print: Python 3.12.x
psql --version          # should print: psql (PostgreSQL) 16.x
nginx -v                # should print: nginx version: nginx/1.24.x
git --version           # should print: git version 2.x.x
```

```bash
# Create a dedicated user for our app (don't run the app as root or ubuntu)
sudo useradd -m -s /bin/bash advaitam
sudo passwd advaitam
# You will be asked to set a password — choose something strong and remember it
```
> **Why a separate user?** Security. If someone exploits your Django app, they only get
> access to the `advaitam` user, not root or ubuntu.

---

### Step 3.5 — Set Up PostgreSQL Database

**Why:** Your Django app stores all data (users, books, sessions, etc.) in PostgreSQL.
We need to create the database and a user that Django will connect as.

```bash
# Switch to the postgres superuser
sudo -u postgres psql
```
You are now inside the PostgreSQL prompt. It looks like: `postgres=#`

```sql
-- Create the database
CREATE DATABASE advaitam_db;

-- Create the user with a strong password (change 'your_strong_password_here')
CREATE USER advaitam_user WITH PASSWORD 'your_strong_password_here';

-- Best practice settings for Django
ALTER ROLE advaitam_user SET client_encoding TO 'utf8';
ALTER ROLE advaitam_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE advaitam_user SET timezone TO 'UTC';

-- Give the user full access to the database
GRANT ALL PRIVILEGES ON DATABASE advaitam_db TO advaitam_user;
ALTER DATABASE advaitam_db OWNER TO advaitam_user;

-- Exit PostgreSQL
\q
```

📸 **Each command should respond with:**
```
CREATE DATABASE
CREATE ROLE
ALTER ROLE
ALTER ROLE
ALTER ROLE
GRANT
ALTER DATABASE
```

> ⚠️ Write down the password you chose for `advaitam_user` — you will put it in the .env file.

---

### Step 3.6 — Create Python Virtual Environment

**Why:** A virtual environment is an isolated Python installation just for your app.
It prevents your app's packages from conflicting with other Python programs on the server.

```bash
# Switch to the advaitam user
sudo -u advaitam bash

# Create the app directory
mkdir -p /home/advaitam/app
mkdir -p /home/advaitam/app/logs

# Create the virtual environment
cd /home/advaitam
python3.12 -m venv venv

# Activate it (you'll do this every time you work on the server)
source venv/bin/activate

# Your prompt now shows (venv) at the start:
# (venv) advaitam@ip-172-31-XX-XX:~$

# Upgrade pip
pip install --upgrade pip

# Exit back to ubuntu user
exit
```

---

### Step 3.7 — Push Your Code to GitHub (From Your Windows Machine)

> 💡 **Do this on your Windows machine in PowerShell, not on the EC2 server.**

```powershell
# Navigate to your project
cd D:\webProject

# Stage all files
git add .

# Commit with a message
git commit -m "production ready - February 2026"

# Push to GitHub
git push origin main
```

📸 **Expected output:**
```
[main abc1234] production ready - February 2026
 X files changed, Y insertions(+)

Enumerating objects: ...
Writing objects: 100% (X/X), done.
To https://github.com/KYALLAMRAJU/website.git
   abc1234..def5678  main -> main
```

---

### Step 3.8 — Clone Your Code onto EC2

> 💡 **Back on your EC2 server (SSH session):**

```bash
# Switch to advaitam user
sudo -u advaitam bash

# Activate the virtual environment
source /home/advaitam/venv/bin/activate

# Go to app directory and clone your code
cd /home/advaitam/app
git clone https://github.com/KYALLAMRAJU/website .
# Note the dot at the end — it clones INTO the current directory, not a subfolder
```

> ⚠️ **If your GitHub repo is private**, git will ask for credentials.
> You MUST use a **Personal Access Token** — GitHub no longer accepts passwords over HTTPS.
>
> **How to create a Personal Access Token (takes 2 minutes):**
> 1. On github.com — click your profile picture (top right) → **Settings**
> 2. Scroll all the way down in left sidebar → **Developer settings**
> 3. Click **Personal access tokens** → **Tokens (classic)** → **Generate new token (classic)**
> 4. Fill in:
>    ```
>    Note: advaitam-ec2-deploy
>    Expiration: 90 days
>    Scopes: ☑ repo   (full control of private repositories)
>    ```
> 5. Click **"Generate token"** → copy the token (it starts with `ghp_...`)
>    ⚠️ You will only see it ONCE — copy it now before closing the page
>
> **When git asks for credentials on EC2:**
> ```
> Username for 'https://github.com': KYALLAMRAJU
> Password for 'https://...':        ghp_xxxxxxxxxxxxxxxxxxxx   ← paste token here
> ```

📸 **Successful clone:**
```
Cloning into '.'...
remote: Enumerating objects: XXX, done.
remote: Counting objects: 100% (XXX/XXX), done.
Receiving objects: 100% (XXX/XXX), done.
```

```bash
# Install all Python packages
pip install -r requirements-prod.txt
```
> This installs Django, Gunicorn, psycopg2, boto3, etc. Takes 2-3 minutes.

📸 **End of output should look like:**
```
Successfully installed Django-5.2.9 gunicorn-23.x.x psycopg2-2.9.x boto3-1.x.x ...
```

---

### Step 3.9 — Create the Production .env File

**Why:** Your `.env` file is where all your secret configuration lives — database password,
Django secret key, AWS credentials, email settings. It is NEVER committed to git.
You create it manually on the server.

```bash
# Make sure you are still as advaitam user with venv activated
# Create and edit the .env file
nano /home/advaitam/app/.env
```

📸 **The nano editor opens — it looks like this:**
```
  GNU nano 7.2    /home/advaitam/app/.env

█  ← your cursor is here, start typing/pasting
```

**Paste the entire block below**, then fill in YOUR values:

```bash
# ========== DJANGO CORE ==========
DJANGO_ENV=production
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=advaitam.info,www.advaitam.info,origin.advaitam.info,54.XXX.XXX.XXX

# ========== DATABASE ==========
DB_ENGINE=django.db.backends.postgresql
DB_NAME=advaitam_db
DB_USER=advaitam_user
DB_PASSWORD=your_strong_password_here
DB_HOST=localhost
DB_PORT=5432

# ========== CSRF ==========
CSRF_TRUSTED_ORIGINS=https://advaitam.info,https://www.advaitam.info,https://origin.advaitam.info

# ========== S3 + CLOUDFRONT ==========
USE_S3=True
AWS_STORAGE_BUCKET_NAME=advaitam-assets
AWS_S3_REGION_NAME=us-east-1
# ⚠️ Fill this AFTER Phase 4 — leave xxxxxxxxxxxx for now:
AWS_S3_CUSTOM_DOMAIN=xxxxxxxxxxxx.cloudfront.net
# Leave blank — EC2 IAM Role handles this automatically:
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# ========== EMAIL (AWS SES) ==========
AWS_SES_REGION_NAME=us-east-1
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_HOST_USER=<SES-SMTP-USERNAME-from-IAM>
EMAIL_HOST_PASSWORD=<SES-SMTP-PASSWORD-from-IAM>
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@advaitam.info
ADMIN_EMAIL=kalyan.py28@gmail.com

# ========== SESSIONS ==========
SESSION_COOKIE_AGE=86400
SESSION_EXPIRE_AT_BROWSER_CLOSE=False

# ========== CLAUDE AI ==========
ANTHROPIC_API_KEY=sk-ant-your-key-here

# ========== SENTRY ERROR TRACKING ==========
SENTRY_DSN=https://your-key@sentry.io/project-id

# ========== CLOUDFRONT ORIGIN PROTECTION ==========
CLOUDFRONT_SECRET=your-random-secret-here
```

**How to generate SECRET_KEY:**
```bash
# Run this in a separate terminal window on Windows:
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Copy the output and paste it as SECRET_KEY value
```

**How to generate CLOUDFRONT_SECRET:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(40))"
# Copy the output and paste it as CLOUDFRONT_SECRET value
```

**Save and exit nano:**
```
Press Ctrl+X  → nano asks "Save modified buffer?"
Press Y       → confirms yes
Press Enter   → confirms the filename
```

📸 **You are back at the shell prompt — file is saved.**

**Lock down permissions — CRITICAL:**
```bash
chmod 600 /home/advaitam/app/.env
chown advaitam:advaitam /home/advaitam/app/.env
```
> `chmod 600` means only the owner can read/write it. Nobody else on the server can see it.

---

### Step 3.10 — Run Database Migrations

**Why:** Django migrations create all the database tables your app needs
(users, books, sessions, etc.).

```bash
# Make sure venv is active and you're in the app directory
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production

# Run migrations
python manage.py migrate
```

📸 **Expected output:**
```
Operations to perform:
  Apply all migrations: admin, auth, authtoken, contenttypes, sessions, taggit, webapp
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying webapp.0001_initial... OK
  ✅ All migrations applied
```

```bash
# Create your admin superuser account
python manage.py createsuperuser
```
📸 **You will be prompted:**
```
Username: admin
Email address: kalyan.py28@gmail.com
Password: (type a strong password)
Password (again): (type it again)
Superuser created successfully.
```

> ⚠️ **Do NOT run `collectstatic` yet!** S3 and CloudFront are not set up yet.
> You will run it in Phase 4 Step 4.4.

---

## 📋 PHASE 7 — ACM Certificate for CloudFront

> 🎓 **Why do this BEFORE Phase 4 (CloudFront)?**
> CloudFront needs an SSL certificate to serve your site over HTTPS. AWS Certificate Manager
> (ACM) provides free SSL certificates. But here's the catch: CloudFront ONLY accepts
> certificates from the **us-east-1** region — even if your EC2 is in another region.
> We do this phase before CloudFront so the cert is ready when we need it.

---

### Step 7.1 — Switch Your Console to us-east-1

**This is the most common mistake — do not skip this!**

📸 **What to look for:**
```
Top-right corner of AWS Console:
  [your-name ▼]  [us-east-1 ▼]  [Support ▼]
                  ↑
                  Click here and make sure it says "US East (N. Virginia)"
```

---

### Step 7.2 — Request a Certificate

1. In the search bar → type **"Certificate Manager"** → click ACM
2. Make sure you see **"US East (N. Virginia)"** in the region selector (top right)
3. Click **"Request a certificate"**

📸 **Certificate type:**
```
● Request a public certificate   ← select this (it's free)
○ Request a private certificate
```

4. Click **Next**

📸 **Domain names — add both:**
```
Fully qualified domain name:
  advaitam.info              ← type this, press "Add another name to this certificate"
  *.advaitam.info            ← type this (the * covers www, origin, and any subdomain)
```

**Validation method:**
```
● DNS validation - recommended   ← select this
  (We will add a CNAME record to Route 53 to prove we own the domain)
```

5. Click **"Request"**

📸 **What you see after requesting:**
```
Certificate status: ⏳ Pending validation
  
Domain             Validation status    CNAME name              CNAME value
advaitam.info      Pending              _abc123.advaitam.info   _xyz789.acm-validations.aws
*.advaitam.info    Pending              (same CNAME)            (same value)
```

---

### Step 7.3 — Validate Ownership via Route 53

**Why:** AWS needs to verify you actually own `advaitam.info`. DNS validation works by
asking you to add a specific CNAME record to your domain. AWS then checks that record exists.

1. Click **"Create records in Route 53"** button

📸 **You will see:**
```
Create DNS records in Amazon Route 53

The following records will be added to the hosted zone advaitam.info:

  _abc123.advaitam.info    CNAME    _xyz789.acm-validations.aws.

→ Click "Create records"
```

2. Click **"Create records"**

📸 **Success:**
```
✅ Successfully created records in Route 53
```

3. **Wait 5–10 minutes**, then refresh the page

📸 **When ready, the status changes to:**
```
Certificate status: ✅ Issued

Domain             Validation status
advaitam.info      ✅ Success
*.advaitam.info    ✅ Success
```

> ⚠️ **Do NOT move to Phase 4 (CloudFront) until you see "Issued".**
> If it stays "Pending" for more than 30 minutes, check that your Route 53 hosted zone
> is using the right nameservers (Phase 5 Step 5.3).

---

## 📋 PHASE 4 — CloudFront CDN Setup

> 🎓 **What is this phase?**
> CloudFront is Amazon's global Content Delivery Network (CDN). It does two things for you:
>
> 1. **Serves your static files (CSS, JS, images, audio) from servers near your users.**
>    Someone in Mumbai gets your files from a Mumbai server, not from Virginia.
>    This makes your site much faster.
>
> 2. **Acts as a reverse proxy for your Django app.**
>    All traffic goes through CloudFront → CloudFront talks to your EC2 on your behalf.
>    Your EC2's real IP (origin.advaitam.info) is hidden from the public.

---

### Step 4.1 — Create a CloudFront Distribution

1. In the search bar → type **"CloudFront"** → click CloudFront
2. Click **"Create distribution"**

**This is a long form — follow each section carefully:**

---

#### Section: Origin (you will add TWO origins)

**Origin 1 — S3 (for static/media files):**

📸
```
Origin domain: advaitam-assets.s3.us-east-1.amazonaws.com
               ↑ start typing "advaitam" and it will appear in the dropdown

Name: advaitam-assets-origin   (auto-filled, leave it)

Origin access:
  ● Origin access control settings (recommended)
    Origin access control: advaitam-oac   ← select from dropdown
    
    You may see a yellow banner: "Update the S3 bucket policy"
    → Click "Copy policy" (you will use this in Step 2.3 later)
    → Don't do the bucket policy yet — just copy it
```

**Origin 2 — EC2 (for Django pages):**

Click **"Add origin"**

📸
```
Origin domain: origin.advaitam.info   ← type your origin subdomain
Protocol: ● HTTPS only
HTTPS port: 443
Minimum origin SSL protocol: TLSv1.2

Add custom header:
  Header name: X-CloudFront-Secret
  Value: your-random-secret-here      ← same value as CLOUDFRONT_SECRET in your .env
  
  (This is the secret Nginx will check — if the header is missing or wrong,
   Nginx returns 403. This blocks anyone who tries to hit origin.advaitam.info directly.)
```

---

#### Section: Default cache behavior

📸
```
Origin and origin groups: advaitam-web-ec2   ← select your EC2 origin
Viewer protocol policy: ● Redirect HTTP to HTTPS
Allowed HTTP methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
                      ↑ select this (Django needs POST for forms/login)
Cache key and origin requests:
  ● Cache policy and origin request policy (recommended)
    Cache policy: CachingDisabled   ← for Django pages, we never cache
    Origin request policy: AllViewerExceptHostHeader
```

---

#### Section: Add additional behaviors (for static/media)

Click **"Add behavior"** (you need to add 2 more):

**Behavior 1 — Static files:**
📸
```
Path pattern: /static/*
Origin: advaitam-assets-origin   ← S3 origin
Viewer protocol policy: Redirect HTTP to HTTPS
Cache policy: CachingOptimized   ← cache for 1 year (static files never change)
```

**Behavior 2 — Media files:**
📸
```
Path pattern: /media/*
Origin: advaitam-assets-origin   ← S3 origin
Viewer protocol policy: Redirect HTTP to HTTPS
Cache policy: CachingOptimized
```

---

#### Section: Settings

📸
```
Alternate domain names (CNAMEs):
  → Click "Add item"
  advaitam.info
  → Click "Add item" again
  www.advaitam.info

Custom SSL certificate:
  → Click the field and start typing "advaitam"
  → Select your certificate: *.advaitam.info (the one we made in Phase 7)
  
  ⚠️ If the certificate does not appear in the dropdown:
     You probably requested it in the wrong region. It MUST be in us-east-1.

Default root object: (leave blank — Django handles routing)

Description: Advaitam production CDN
```

3. Click **"Create distribution"**

📸 **What you will see:**
```
✅ Distribution E1ABCD2EFGH3IJ has been created
Status: ⏳ Deploying...   (takes 5-15 minutes to deploy globally)

Distribution domain name: xxxxxxxxxxxx.cloudfront.net   ← WRITE THIS DOWN
```

> 💡 The Distribution domain name (`xxxxxxxxxxxx.cloudfront.net`) is what you put in your
> `.env` file as `AWS_S3_CUSTOM_DOMAIN`. Copy it now.

---

### Step 4.2 — Update Your .env File with the CloudFront Domain

**Back on your EC2 server:**
```bash
nano /home/advaitam/app/.env
# Find this line:
AWS_S3_CUSTOM_DOMAIN=xxxxxxxxxxxx.cloudfront.net
# Replace xxxxxxxxxxxx with your actual CloudFront domain prefix
# Save with Ctrl+X → Y → Enter
```

---

### Step 4.3 — Complete the S3 Bucket Policy (from Phase 2 Step 2.3)

Now go back to **Phase 2 Step 2.3** and complete the S3 bucket policy.
Use your actual values:
- **YOUR_ACCOUNT_ID** → your 12-digit AWS account number (top-right corner menu)
- **YOUR_DISTRIBUTION_ID** → `E1ABCD2EFGH3IJ` (from the CloudFront distribution you just created)

---

### Step 4.4 — Run collectstatic (Upload All Static Files to S3)

**Now it is safe to run collectstatic** because S3, CloudFront, and the bucket policy are all ready.

```bash
# On EC2, as advaitam user with venv active:
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production

python manage.py collectstatic --noinput
```

📸 **What you will see:**
```
Found another file with the destination path 'admin/...': ...
Post-processing 'admin/css/base.css'...
...
XXX static files copied to S3.
```

**Verify the files are in S3:**
```bash
aws s3 ls s3://advaitam-assets/static/ --recursive | head -20
```

📸 **Output shows your files:**
```
2026-02-27 10:30:00     12345 static/css/home.css
2026-02-27 10:30:00    234567 static/images/adishankaracharya.jpg
2026-02-27 10:30:00     98765 static/books/Django.pdf
...
```

> ⚠️ **Audio `.mp3` files NOT here yet** — upload them separately (Step 4.5 below).

---

### Step 4.5 — Upload Audio Files to S3 (Run From Your Windows Machine)

**Why:** Audio `.mp3` files are large binaries — they are **never committed to git** and are
**not processed by `collectstatic`**. You must upload them directly to S3 from your Windows
machine using the AWS CLI.

> 💡 Run this command once to do the initial upload. Whenever you add new `.mp3` files in
> future, just re-run it — `aws s3 sync` only uploads new/changed files, skipping existing ones.

**Run this from PowerShell on your Windows machine, inside `D:\webProject`:**

```powershell
cd D:\webProject

aws s3 sync static/audio/ s3://advaitam-assets/static/audio/ `
    --exclude "*.md" `
    --exclude ".gitkeep" `
    --content-type "audio/mpeg" `
    --cache-control "max-age=31536000" `
    --only-show-errors
```

📸 **Expected output while uploading:**
```
upload: static\audio\bhagavadgita\ch01.mp3 to s3://advaitam-assets/static/audio/bhagavadgita/ch01.mp3
upload: static\audio\bhagavadgita\ch02.mp3 to s3://advaitam-assets/static/audio/bhagavadgita/ch02.mp3
upload: static\audio\upanisad\day1.mp3 to s3://advaitam-assets/static/audio/upanisad/day1.mp3
...
```

**Verify upload worked:**
```powershell
aws s3 ls s3://advaitam-assets/static/audio/ --recursive
```

📸 **Expected output:**
```
2026-02-28 10:30:00   5242880 static/audio/bhagavadgita/ch01.mp3
2026-02-28 10:30:00   5345678 static/audio/bhagavadgita/ch02.mp3
2026-02-28 10:30:00   4891234 static/audio/upanisad/day1.mp3
2026-02-28 10:30:00   6123456 static/audio/grantha/viveka1.mp3
...
```

> ✅ Once uploaded, CloudFront serves them at:
> `https://xxxxxxxxxxxx.cloudfront.net/static/audio/bhagavadgita/ch01.mp3`
> This is exactly the path `audio.html` uses in its `AUDIO_DATA` object — the player works!

---

## 📋 PHASE 5 — Route 53 DNS Setup

> 🎓 **What is this phase?**
> DNS (Domain Name System) is the internet's phone book. When someone types `advaitam.info`,
> their computer asks DNS: "What IP address is advaitam.info?" DNS answers, and the browser
> connects to that IP.
>
> Route 53 is Amazon's DNS service. We will configure it so:
> - `advaitam.info` and `www.advaitam.info` → point to CloudFront (so users get the CDN)
> - `origin.advaitam.info` → points directly to EC2 (so Nginx/certbot can work)

---

### Step 5.1 — Create a Hosted Zone

1. In the search bar → type **"Route 53"** → click Route 53
2. In the left sidebar → click **"Hosted zones"**
3. Click **"Create hosted zone"**

📸
```
Domain name: advaitam.info
Description: (optional)
Type: ● Public hosted zone
```

4. Click **"Create hosted zone"**

📸 **What you will see after creation:**
```
Hosted zone: advaitam.info
Hosted zone ID: Z1234567890ABC

Records (2 already created automatically):
  advaitam.info    NS     ns-123.awsdns-45.com
                          ns-678.awsdns-90.net
                          ns-234.awsdns-56.org
                          ns-789.awsdns-12.co.uk
  advaitam.info    SOA    ns-123.awsdns-45.com. ...
```

**Write down your 4 NS (nameserver) values** — you will need them in the next step.

---

### Step 5.2 — Update Nameservers at Your Domain Registrar

**Why:** Right now your domain `advaitam.info` is managed by whoever sold it to you
(GoDaddy, Namecheap, Google Domains, etc.). You need to tell them: "From now on,
let Route 53 handle the DNS." You do this by updating the nameservers.

**What to do (example for Namecheap — yours may look slightly different):**
1. Log in to your domain registrar's website
2. Find your domain `advaitam.info` → click **"Manage"**
3. Find **"Nameservers"** section
4. Change from "Automatic DNS" to **"Custom DNS"**
5. Enter your 4 Route 53 nameservers:
   ```
   ns-123.awsdns-45.com
   ns-678.awsdns-90.net
   ns-234.awsdns-56.org
   ns-789.awsdns-12.co.uk
   ```
6. Save

📸 **After saving at registrar:**
```
Nameservers updated successfully.
Note: DNS changes can take 5 minutes to 48 hours to propagate worldwide.
```

> ⏰ **Wait at least 15 minutes before moving on.** You can check propagation at
> https://dnschecker.org — enter `advaitam.info` and look for NS records.

---

### Step 5.3 — Create DNS Records in Route 53

**Go back to Route 53 → Hosted zones → advaitam.info → click "Create record"**

**Record 1 — Root domain → CloudFront:**

📸
```
Record name: (leave blank — this is for advaitam.info itself)
Record type: A
Alias: ● On
Route traffic to: Alias to CloudFront distribution
                  → select your CloudFront distribution from the dropdown
                    (it will show as xxxxxxxxxxxx.cloudfront.net)
Routing policy: Simple routing
```
Click **"Add another record"**

**Record 2 — www → CloudFront:**
📸
```
Record name: www
Record type: A
Alias: ● On
Route traffic to: Alias to CloudFront distribution → same distribution
Routing policy: Simple routing
```
Click **"Add another record"**

**Record 3 — origin → EC2 (direct):**
📸
```
Record name: origin
Record type: A
Alias: ● Off
Value: 54.XXX.XXX.XXX    ← your EC2 Elastic IP
TTL: 300
Routing policy: Simple routing
```

Click **"Create records"**

📸 **Success:**
```
✅ 3 records were created successfully in advaitam.info
```

---

## 📋 PHASE 6 — Gunicorn + Nginx + SSL (The Web Server Layer)

> 🎓 **What is this phase?**
> This is the most technical phase. Here's what each piece does:
>
> - **Gunicorn** — runs your Django Python code. Like a waiter taking orders (HTTP requests)
>   and passing them to the kitchen (Django) to cook (process) and return food (HTML).
>
> - **Nginx** — sits in front of Gunicorn. It handles SSL (HTTPS), checks the CloudFront
>   secret header, and passes valid requests to Gunicorn via a Unix socket.
>
> - **SSL certificate (Let's Encrypt)** — makes `origin.advaitam.info` work over HTTPS.
>   Required because CloudFront connects to your origin using HTTPS.
>
> - **systemd** — makes Gunicorn start automatically when the server boots, and restart
>   if it crashes. Like a supervisor that keeps Gunicorn alive 24/7.

---

### Step 6.1 — Create Gunicorn systemd Socket File

**Why a socket file?** Nginx and Gunicorn communicate through a "Unix socket" — a special
file that acts as a pipe between them. It's faster than TCP/IP for local communication.

```bash
# SSH into EC2 if not already connected, then:
sudo nano /etc/systemd/system/advaitam.socket
```

**Type/paste this exactly:**
```ini
[Unit]
Description=Advaitam Gunicorn Socket

[Socket]
ListenStream=/run/advaitam/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Save: `Ctrl+X → Y → Enter`

---

### Step 6.2 — Create Gunicorn systemd Service File

```bash
sudo nano /etc/systemd/system/advaitam.service
```

**Type/paste this exactly:**
```ini
[Unit]
Description=Advaitam Gunicorn Daemon
Requires=advaitam.socket
After=network.target

[Service]
User=advaitam
Group=www-data
WorkingDirectory=/home/advaitam/app
Environment=DJANGO_ENV=production
ExecStart=/home/advaitam/venv/bin/gunicorn \
          --config /home/advaitam/app/gunicorn.conf.py \
          webProject.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X → Y → Enter`

> 💡 **What does each line mean?**
> - `User=advaitam` → runs as the advaitam user (not root)
> - `Environment=DJANGO_ENV=production` → tells Django to use production settings
> - `ExecStart=...gunicorn` → the actual command to start Gunicorn
> - `--config gunicorn.conf.py` → uses your config (2 workers, 2 threads, 120s timeout)

---

### Step 6.3 — Start and Enable Gunicorn

```bash
# Create the socket directory
sudo mkdir -p /run/advaitam
sudo chown advaitam:www-data /run/advaitam

# Reload systemd so it sees the new files
sudo systemctl daemon-reload

# Enable both (so they start on reboot)
sudo systemctl enable advaitam.socket
sudo systemctl enable advaitam.service

# Start them now
sudo systemctl start advaitam.socket
sudo systemctl start advaitam.service
```

**Check it worked:**
```bash
sudo systemctl status advaitam.service
```

📸 **Healthy output looks like:**
```
● advaitam.service - Advaitam Gunicorn Daemon
     Loaded: loaded (/etc/systemd/system/advaitam.service; enabled)
     Active: ● active (running) since Thu 2026-02-27 10:30:00 UTC; 5s ago
   Main PID: 12345 (gunicorn)
      Tasks: 5 (limit: 1141)

Feb 27 10:30:00 ip-172-31-XX-XX gunicorn[12345]: [2026-02-27 10:30:00 +0000] [12345] [INFO] Starting gunicorn 23.x.x
Feb 27 10:30:00 ip-172-31-XX-XX gunicorn[12346]: [2026-02-27 10:30:00 +0000] [12346] [INFO] Booting worker with pid: 12346
```

> ⚠️ If you see `Active: failed` → run `journalctl -u advaitam.service -n 30` to see the error.
> Most common cause: a typo in `.env` or a missing Python package.

---

### Step 6.4 — Get SSL Certificate with Certbot

**Why:** Nginx needs an SSL certificate for `origin.advaitam.info` so CloudFront can connect
to it over HTTPS. Let's Encrypt gives free certificates. Certbot automates getting and
renewing them.

> ⚠️ **Before running certbot:** `origin.advaitam.info` MUST resolve to your EC2 Elastic IP.
> Test this first:
> ```bash
> nslookup origin.advaitam.info
> # Should show: Address: 54.XXX.XXX.XXX (your Elastic IP)
> ```
> If it shows a different IP or "can't find", DNS hasn't propagated yet. Wait and try again.

```bash
# Install certbot with the Nginx plugin
sudo apt install -y certbot python3-certbot-nginx

# Get certificate — Nginx must already be running (it is, from Step 6.5)
# The --nginx plugin temporarily modifies Nginx config to complete domain validation
sudo certbot --nginx -d origin.advaitam.info
```

📸 **Certbot will ask:**
```
Enter email address (used for urgent renewal and security notices):
→ kalyan.py28@gmail.com

Please read the Terms of Service...
→ (A)gree

Would you be willing to share your email address...?
→ (N)o

Please choose whether or not to redirect HTTP traffic to HTTPS:
1: No redirect - Make no further changes to the webserver configuration.
2: Redirect   - Make all requests redirect to secure HTTPS access.
→ 2   ← always choose redirect
```

📸 **Success:**
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/origin.advaitam.info/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/origin.advaitam.info/privkey.pem
This certificate expires on 2026-05-28.
These files will be updated when the certificate renews.
```

**Set up auto-renewal:**
```bash
sudo certbot renew --dry-run
# Should say: "Congratulations, all simulated renewals succeeded"
```

---

### Step 6.5 — Configure Nginx

```bash
# Remove the default Nginx config
sudo rm /etc/nginx/sites-enabled/default

# Create your config
sudo nano /etc/nginx/sites-available/advaitam
```

**Paste this entire config:**
```nginx
# Redirect all plain HTTP to HTTPS
server {
    listen 80;
    server_name origin.advaitam.info;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name origin.advaitam.info;

    # SSL certificate from Let's Encrypt
    ssl_certificate     /etc/letsencrypt/live/origin.advaitam.info/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/origin.advaitam.info/privkey.pem;

    # CloudFront origin protection
    # CloudFront will send this secret header with every request
    # If the header is missing or wrong → 403 Forbidden
    # This means: ONLY CloudFront can reach your Django app, nobody else
    set $x_cloudfront_secret "your-random-secret-here";

    if ($http_x_cloudfront_secret != $x_cloudfront_secret) {
        return 403;
    }

    # Allow file uploads up to 20MB (for future media uploads)
    client_max_body_size 20M;

    # Pass all requests to Gunicorn via Unix socket
    location / {
        proxy_pass http://unix:/run/advaitam/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;   # 120s for audio streaming
    }

    access_log /home/advaitam/app/logs/nginx_access.log;
    error_log  /home/advaitam/app/logs/nginx_error.log;
}
```

> ⚠️ Replace `your-random-secret-here` with the same value as `CLOUDFRONT_SECRET` in `.env`
> AND the same value you entered as the CloudFront custom header in Phase 4.
> All three must be identical.

Save: `Ctrl+X → Y → Enter`

```bash
# Enable the config (create a symlink)
sudo ln -s /etc/nginx/sites-available/advaitam /etc/nginx/sites-enabled/

# Test for syntax errors
sudo nginx -t
```

📸 **Good output:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

> ⚠️ If you see an error, re-open the file and look for typos.

```bash
# Apply the new config
sudo systemctl restart nginx
sudo systemctl status nginx
```

📸 **Healthy Nginx:**
```
● nginx.service - A high performance web server and a reverse proxy server
     Active: ● active (running)
```

---

## 📋 PHASE 8 — Final Verification

> 🎓 **What is this phase?**
> You have set up everything. Now let's verify it all works end-to-end before calling it done.
> Think of this as a pre-flight checklist before takeoff.

---

### Step 8.1 — Django Production Health Check

```bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production
python manage.py check --deploy
```

📸 **What you want to see:**
```
System check identified no issues (0 silenced).
```

📸 **If you see warnings like this — they are OK:**
```
?: (security.W004) You have not set SECURE_HSTS_SECONDS...
```
> HSTS warnings are expected when behind CloudFront/Nginx because SSL terminates at CloudFront,
> not Django. Your settings.py already handles this correctly.

---

### Step 8.2 — Test Your Live Website

**From your Windows browser, visit these URLs and verify:**

| URL | Expected Result |
|-----|----------------|
| `https://advaitam.info/` | Redirects to `/loginpage/` → shows login form |
| `https://www.advaitam.info/` | Same as above |
| `https://advaitam.info/loginpage/` | Login page loads with CSS styling ✅ |
| `https://advaitam.info/static/css/home.css` | Shows CSS text (served from S3/CloudFront) |
| `https://origin.advaitam.info/loginpage/` | **403 Forbidden** ✅ (origin protection working) |

> 💡 If `advaitam.info` shows a browser error (not a Django page), DNS may not have propagated yet.
> Wait 30 minutes and try again. You can check at https://dnschecker.org

---

### Step 8.3 — Test Email (AWS SES)

```bash
sudo -u advaitam bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production

python manage.py shell
```

In the Django shell:
```python
>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail(
...     subject='Test from Advaitam',
...     message='If you see this, SES email is working!',
...     from_email=settings.DEFAULT_FROM_EMAIL,
...     recipient_list=[settings.ADMIN_EMAIL],
... )
```

📸 **Expected output:**
```
1
```
> A return value of `1` means 1 email was sent successfully. Check your inbox at `kalyan.py28@gmail.com`.

> ⚠️ If SES is still in sandbox mode, you will get `SMTPRecipientsRefused`.
> Solution: go to AWS SES Console → Account Dashboard → Request production access.

---

### Step 8.4 — Test Static Files Are Served from CloudFront

```bash
# From your Windows PowerShell:
curl -I "https://advaitam.info/static/css/home.css"
```

📸 **Look for these headers in the response:**
```
HTTP/2 200
x-cache: Hit from cloudfront          ← ✅ served from CloudFront edge cache
via: 1.1 xxxxxxxxxxxx.cloudfront.net (CloudFront)
server: AmazonS3                       ← ✅ actually came from S3
```

---

## 📋 PHASE 9 — Security Hardening

> 🎓 **What is this phase?**
> Your site works. Now let's lock it down. A server exposed to the internet will be
> probed by bots within minutes of going live. These steps make it much harder to attack.

---

### Step 9.1 — Harden SSH Access

**Why:** SSH on port 22 is constantly brute-forced by bots. We disable password login
so only someone with your `.pem` key file can SSH in.

```bash
sudo nano /etc/ssh/sshd_config
```

Find and change these lines (use `Ctrl+W` to search in nano):
```
PermitRootLogin no          ← change from yes to no
PasswordAuthentication no   ← change from yes to no
PubkeyAuthentication yes    ← make sure this is yes
```

Save and restart SSH:
```bash
sudo systemctl restart sshd
```

> ⚠️ **Before disconnecting**, open a NEW SSH session in a second terminal window to
> make sure you can still connect. If you can — great. If not, fix the config before closing
> your current session, or you will lock yourself out.

---

### Step 9.2 — Enable UFW Firewall

**Why:** UFW (Uncomplicated Firewall) controls which ports are open on the server.
We want: SSH (22), HTTP (80), HTTPS (443) — and nothing else.

```bash
sudo ufw default deny incoming    # block everything incoming by default
sudo ufw default allow outgoing   # allow all outgoing (app needs to call SES, etc.)
sudo ufw allow ssh                # allow SSH (port 22)
sudo ufw allow 'Nginx Full'       # allow HTTP (80) and HTTPS (443)
sudo ufw enable                   # turn it on (type 'y' to confirm)
sudo ufw status
```

📸 **Expected output:**
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
Nginx Full                 ALLOW       Anywhere
```

---

### Step 9.3 — Restrict EC2 Security Group (AWS Console)

**Why:** UFW is on the server. The EC2 Security Group is an additional firewall at the
AWS network level. We should restrict SSH to only your home IP.

1. Go to EC2 → **Security Groups** → click `advaitam-sg`
2. Click the **"Inbound rules"** tab → click **"Edit inbound rules"**
3. Find the SSH rule (port 22 from `0.0.0.0/0`)
4. Change the Source from `0.0.0.0/0` to **"My IP"**

📸
```
Type    Protocol  Port  Source
SSH     TCP       22    My IP  ← 203.0.113.X/32 (your current public IP)
HTTP    TCP       80    0.0.0.0/0
HTTPS   TCP       443   0.0.0.0/0
```

5. Click **"Save rules"**

> 💡 If you change location (e.g. go to a café), update this rule with your new IP.
> Or use a VPN with a fixed IP.

---

### Step 9.4 — Verify Django Security Settings

```bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production
python manage.py check --deploy
```

These should all be active in production mode (your settings.py already sets them):
```
✅ SECURE_SSL_REDIRECT = True
✅ SESSION_COOKIE_SECURE = True
✅ CSRF_COOKIE_SECURE = True
✅ SECURE_HSTS_SECONDS = 31536000
✅ X_FRAME_OPTIONS = DENY
✅ SECURE_BROWSER_XSS_FILTER = True
```

---

## 📋 PHASE 10 — Monitoring

> 🎓 **What is this phase?**
> Your site is live and secure. Now set up alerts so you know if something goes wrong —
> before your users report it to you.

---

### Step 10.1 — Set Up CloudWatch Alarms

**Why:** CloudWatch monitors your EC2. We will create two alerts:
- If CPU is too high for too long → your app is struggling
- If the instance fails health checks → it may be down

**What to do:**
1. In the search bar → type **"CloudWatch"** → click CloudWatch
2. Left sidebar → **"Alarms"** → **"All alarms"** → click **"Create alarm"**

**Alarm 1 — High CPU:**

📸
```
Step 1 — Specify metric and conditions:
  → Click "Select metric"
  → EC2 → Per-Instance Metrics
  → Find your instance (i-0xxxxxxxxxxxxxxxxx) → CPUUtilization → Select metric

  Statistic: Average
  Period: 5 minutes
  Threshold type: Static
  Whenever CPUUtilization is: Greater than 80
```

📸
```
Step 2 — Configure actions:
  Alarm state trigger: In alarm
  → Create new SNS topic
    Topic name: advaitam-alerts
    Email: kalyan.py28@gmail.com
  → Click "Create topic"
```
> You will get a confirmation email from AWS SNS — click "Confirm subscription" in it.

Click through to **Create alarm**.

**Alarm 2 — Instance health check failed:**
Repeat the process but choose:
- Metric: `StatusCheckFailed`
- Threshold: `>= 1` (any failure)

---

### Step 10.2 — Set Up AWS Budget Alert

**Why:** Prevents surprise bills. You get an email if you're about to exceed $10/month.

1. Click your account name (top-right) → **"Billing and Cost Management"**
2. Left sidebar → **"Budgets"** → **"Create budget"**

📸
```
Budget setup:
  ● Use a template (simplified)
  Template: Monthly cost budget

Budget name: advaitam-monthly-budget
Budgeted amount ($): 10

Alert threshold: 80%   → Email: kalyan.py28@gmail.com
Alert threshold: 100%  → Email: kalyan.py28@gmail.com
```

3. Click **"Create budget"**

---

### Step 10.3 — Set Up Log Rotation

**Why:** Your Django and Nginx logs grow forever if not rotated. After a month of traffic,
they can fill up your 20GB disk. Log rotation automatically compresses and deletes old logs.

```bash
sudo nano /etc/logrotate.d/advaitam
```

**Paste this:**
```
/home/advaitam/app/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 advaitam www-data
    sharedscripts
    postrotate
        systemctl reload advaitam.service > /dev/null 2>&1 || true
    endscript
}
```

Save: `Ctrl+X → Y → Enter`

**Test it works:**
```bash
sudo logrotate --debug /etc/logrotate.d/advaitam
# Should print what it WOULD do (no actual rotation in debug mode)
```

> 💡 This keeps 14 days of compressed logs (about 14 files). Older ones are deleted automatically.

---

### Step 10.3 — Set Up AWS SES for Production Access

> ⚠️ By default, SES is in **sandbox mode** — you can only send emails TO verified addresses.
> To send to real users (signup emails, password resets), you must request production access.

**What to do:**
1. Go to **SES** → left sidebar → **"Account dashboard"**

📸 **You will see:**
```
Sending quota
  Sandbox: Yes   ← we need to change this to No

→ Click "Request production access"
```

2. Fill in the form:

📸
```
Website URL: https://advaitam.info
Use case description: 
  "Transactional emails for a spiritual content website:
   1. Account registration confirmation
   2. Password reset links  
   3. Contact form notifications to admin
   Expected volume: fewer than 100 emails/day"

Mail type: Transactional
```

3. Submit. AWS reviews within 24 hours and usually approves.

---

### Step 10.4 — Set Up SES SMTP Credentials

**Why:** Django connects to SES via SMTP. You need SMTP-specific credentials — these are
different from your regular AWS access keys.

**What to do:**
1. Go to **SES** → left sidebar → **"SMTP settings"**

📸 **You will see:**
```
SMTP endpoint: email-smtp.us-east-1.amazonaws.com
Port: 587 (STARTTLS)   or   465 (SSL)

→ Click "Create SMTP credentials"
```

2. IAM user name: `advaitam-ses-smtp` (leave default or type this)
3. Click **"Create"**

📸 **IMPORTANT — Download credentials immediately:**
```
✅ SMTP credentials created

SMTP username: AKIAXXXXXXXXXXXXXXXX
SMTP password: BMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

⚠️ This is the ONLY time you will see the password. Download it now.
→ Click "Download credentials"
```

4. Update your `.env` file on EC2:
```bash
nano /home/advaitam/app/.env
# Update these two lines:
EMAIL_HOST_USER=AKIAXXXXXXXXXXXXXXXX
EMAIL_HOST_PASSWORD=BMxxxxxxxxxxxxxxxxxxxxxxxx
```

5. Restart Gunicorn so the new values take effect:
```bash
sudo systemctl restart advaitam.service
```

---

### Step 10.5 — Verify Your Domain in SES

**Why:** SES requires you to prove you own the domain you're sending from (`advaitam.info`).

1. Go to **SES** → **"Verified identities"** → **"Create identity"**

📸
```
Identity type: ● Domain
Domain: advaitam.info
☑ Use a custom MAIL FROM domain (optional — skip for now)
☑ Easy DKIM — RSA 2048-bit   ← provides email authentication
```

2. Click **"Create identity"**

📸 **SES gives you CNAME records to add to Route 53:**
```
DKIM records to publish:
  Name: xxxxxxxx._domainkey.advaitam.info    Value: xxxxxxxx.dkim.amazonses.com
  Name: yyyyyyyy._domainkey.advaitam.info    Value: yyyyyyyy.dkim.amazonses.com
  Name: zzzzzzzz._domainkey.advaitam.info    Value: zzzzzzzz.dkim.amazonses.com
  
→ Click "Publish DNS records" (if Route 53 is linked, it adds them automatically)
```

3. Wait 5–10 minutes → status changes to **Verified ✅**

---

### Step 10.6 — Enable Sentry Error Tracking (Optional but Recommended)

**Why:** When your app crashes in production, you want to know immediately — with the full
stack trace, the URL that caused it, and the user who was affected.

```bash
# On EC2, with venv active:
pip install sentry-sdk
```

Add to `requirements-prod.txt`:
```
sentry-sdk==2.x.x
```

In `.env`:
```
SENTRY_DSN=https://your-key@sentry.io/project-id
```

> Get your DSN by creating a free account at https://sentry.io → New Project → Django.

Then uncomment in `settings.py`:
```python
# _SENTRY_DSN = env('SENTRY_DSN', default=None)
# if _SENTRY_DSN:
#     import sentry_sdk
#     sentry_sdk.init(dsn=_SENTRY_DSN, traces_sample_rate=0.2, environment='production')
```

---

## 🔄 Deployment Workflow — How to Update Your Site After Going Live

> 🎓 **Every time you make code changes**, follow this exact sequence:

```bash
# ── STEP 1: On your Windows machine ──────────────────────────────────────
cd D:\webProject
git add .
git commit -m "describe what you changed"
git push origin main

# ── STEP 2: SSH into EC2 ─────────────────────────────────────────────────
ssh -i "C:\Users\YourName\.ssh\advaitam-key.pem" ubuntu@54.XXX.XXX.XXX

# ── STEP 3: Pull the new code ────────────────────────────────────────────
sudo -u advaitam bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
git pull origin main

# ── STEP 4: Only run these if needed ─────────────────────────────────────
pip install -r requirements-prod.txt     # ← only if you added new packages
export DJANGO_ENV=production
python manage.py migrate                 # ← only if you changed models
python manage.py collectstatic --noinput # ← only if you changed CSS/JS/images

# ── STEP 5: Restart Gunicorn ─────────────────────────────────────────────
exit   # back to ubuntu user
sudo systemctl restart advaitam.service
sudo systemctl status advaitam.service   # verify it's running
```

---

## 🐛 Troubleshooting

> 🎓 **How to diagnose problems:** Always check logs first. They tell you exactly what went wrong.

---

### Problem: Site shows "502 Bad Gateway"

**What it means:** Nginx is running but can't reach Gunicorn.

```bash
# Check if Gunicorn is actually running:
sudo systemctl status advaitam.service

# Read the last 50 lines of Gunicorn logs:
journalctl -u advaitam.service -n 50 --no-pager

# Check if the socket file exists:
ls -la /run/advaitam/gunicorn.sock
# Should show: srwxrwxrwx 1 advaitam www-data ...

# Check Nginx error log:
tail -30 /home/advaitam/app/logs/nginx_error.log
```

**Common fixes:**
```bash
# Socket directory missing → recreate it:
sudo mkdir -p /run/advaitam
sudo chown advaitam:www-data /run/advaitam
sudo systemctl restart advaitam.service

# Import error in Django → check:
sudo -u advaitam bash -c "source /home/advaitam/venv/bin/activate && cd /home/advaitam/app && DJANGO_ENV=production python manage.py check"
```

---

### Problem: Site shows "500 Internal Server Error"

**What it means:** Django is running but something crashed inside your app.

```bash
# Check Django's error log:
tail -50 /home/advaitam/app/logs/django.log

# Or check Gunicorn logs for the traceback:
journalctl -u advaitam.service -n 100 --no-pager | grep -A 20 "Exception"
```

---

### Problem: Static files show 404 (CSS/JS not loading, site looks broken)

```bash
# 1. Check USE_S3=True in .env:
grep USE_S3 /home/advaitam/app/.env

# 2. Check the CloudFront domain is correct (no typo):
grep AWS_S3_CUSTOM_DOMAIN /home/advaitam/app/.env

# 3. Verify files are actually in S3:
aws s3 ls s3://advaitam-assets/static/css/

# 4. Re-run collectstatic:
sudo -u advaitam bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production
python manage.py collectstatic --noinput
```

---

### Problem: Database connection error

```bash
# Check PostgreSQL is running:
sudo systemctl status postgresql

# Try connecting manually (if this works, Django settings are the problem):
sudo -u advaitam psql -U advaitam_user -d advaitam_db -h localhost

# Check .env has correct DB settings:
grep "^DB_" /home/advaitam/app/.env
```

---

### Problem: Emails not being sent

```bash
# Test from Django shell:
sudo -u advaitam bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production
python manage.py shell

>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail('Test', 'Test body', settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
```

| Error | Cause | Fix |
|-------|-------|-----|
| `SMTPAuthenticationError` | Wrong SES SMTP credentials | Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `.env` — these are SES SMTP credentials, NOT your AWS access keys |
| `SMTPRecipientsRefused` | SES sandbox mode | Request SES production access (Phase 10 Step 10.3) OR verify the recipient email in SES |
| `ConnectionRefusedError` | Wrong SES endpoint | Check `EMAIL_HOST` matches your SES region: `email-smtp.us-east-1.amazonaws.com` |
| `SMTPSenderRefused` | Sender not verified | Verify `advaitam.info` domain in SES (Phase 10 Step 10.5) |

---

### Problem: 403 Forbidden on every page

**What it means:** The CloudFront secret doesn't match. Someone is hitting your EC2 directly,
or CloudFront isn't sending the right secret header.

```bash
# Check what value is in .env:
grep CLOUDFRONT_SECRET /home/advaitam/app/.env

# Check what value is in Nginx config:
grep x_cloudfront_secret /etc/nginx/sites-available/advaitam

# Check what value is in CloudFront:
# AWS Console → CloudFront → your distribution → Origins tab
# → click your EC2 origin → scroll to "Add custom headers"
# The value must be IDENTICAL in all three places (no spaces, no quotes)
```

---

### Problem: Gunicorn starts but then crashes

```bash
# See the full error:
journalctl -u advaitam.service -n 100 --no-pager

# Most common causes:
# 1. Missing package → pip install -r requirements-prod.txt
# 2. .env file missing or unreadable → ls -la /home/advaitam/app/.env
# 3. Database not running → sudo systemctl start postgresql
# 4. Wrong DJANGO_ENV → make sure Environment=DJANGO_ENV=production in .service file
```

---

## 📞 Quick Reference Card

> 🎓 **Print this out or save it — you will use these constantly.**

### Your Server Details
| What | Value |
|------|-------|
| EC2 Elastic IP | `54.XXX.XXX.XXX` (your actual IP) |
| SSH command | `ssh -i advaitam-key.pem ubuntu@54.XXX.XXX.XXX` |
| App directory | `/home/advaitam/app/` |
| Python venv | `/home/advaitam/venv/` |
| .env file | `/home/advaitam/app/.env` |
| Log files | `/home/advaitam/app/logs/` |
| Gunicorn socket | `/run/advaitam/gunicorn.sock` |
| Nginx config | `/etc/nginx/sites-available/advaitam` |
| systemd service | `/etc/systemd/system/advaitam.service` |
| SSL certificate | `/etc/letsencrypt/live/origin.advaitam.info/` |

### Most Used Commands on EC2
```bash
# Restart Django app:
sudo systemctl restart advaitam.service

# Check if app is running:
sudo systemctl status advaitam.service

# Watch live logs (Ctrl+C to stop):
journalctl -u advaitam.service -f

# Check Nginx:
sudo systemctl status nginx
sudo nginx -t                    # test config for syntax errors
sudo systemctl restart nginx

# Check disk space:
df -h

# Check memory usage:
free -h

# Check what processes are running:
ps aux | grep gunicorn

# Check what ports are listening:
ss -tlnp

# Run Django management commands:
sudo -u advaitam bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production
python manage.py [command]       # e.g. migrate, collectstatic, shell, check
```

### AWS Services Quick Links
| Service | URL | What for |
|---------|-----|----------|
| EC2 | console.aws.amazon.com/ec2 | Server, security groups, elastic IPs |
| S3 | console.aws.amazon.com/s3 | File storage, bucket policy |
| CloudFront | console.aws.amazon.com/cloudfront | CDN distribution, cache invalidation |
| Route 53 | console.aws.amazon.com/route53 | DNS records |
| ACM | console.aws.amazon.com/acm | SSL certificates |
| SES | console.aws.amazon.com/ses | Email sending, verified identities |
| CloudWatch | console.aws.amazon.com/cloudwatch | Alarms, logs, metrics |
| IAM | console.aws.amazon.com/iam | Users, roles, policies |
| Billing | console.aws.amazon.com/billing | Costs, budgets |
```
https://aws.amazon.com → Create account
Use a real email + strong password + MFA on root account
Region: us-east-1 (N. Virginia) — use this for EVERYTHING
```

### Step 1.2 — Create IAM Admin User (don't use root)
```
IAM → Users → Create user
Username: advaitam-admin
Attach policy: AdministratorAccess
Create access key → Download CSV (you need this for AWS CLI)
```

### Step 1.3 — Install & Configure AWS CLI
```bash
# On your Windows machine:
winget install Amazon.AWSCLI
aws configure
  AWS Access Key ID:     [from CSV]
  AWS Secret Access Key: [from CSV]
  Default region:        us-east-1
  Default output format: json

# Verify:
aws sts get-caller-identity
```

### Step 1.4 — Create EC2 IAM Instance Role (for S3 access — no keys needed on server)
```
IAM → Roles → Create role
Trusted entity: AWS Service → EC2
Attach policies:
  - AmazonS3FullAccess
  - AmazonSESFullAccess      ← needed if you want Django to send email via boto3 later
Role name: advaitam-ec2-role
```

> ⚠️ This role is what lets EC2 access S3 without putting AWS keys in .env

---

## 📋 PHASE 2 — S3 Bucket Setup

### Step 2.1 — Create S3 Bucket
```
S3 → Create bucket
Bucket name: advaitam-assets
Region: us-east-1
Block ALL public access: ✅ ON (CloudFront uses OAC — public access not needed)
Versioning: OFF (saves cost)
Encryption: SSE-S3 (default)
```

### Step 2.2 — Create Bucket Folders (optional — collectstatic does this)
```
static/
media/
```

### Step 2.3 — Create CloudFront Origin Access Control (OAC)
```
CloudFront → Origin access → Create control setting
Name: advaitam-oac
Signing behavior: Sign requests (recommended)
Origin type: S3
```
> Save the OAC ID — you need it in Phase 4

### Step 2.4 — Add S3 Bucket Policy (do this AFTER CloudFront is created in Phase 4)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontOAC",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::advaitam-assets/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```
> Replace YOUR_ACCOUNT_ID and YOUR_DISTRIBUTION_ID after Phase 4

---

## 📋 PHASE 3 — EC2 Setup + App Deployment

### Step 3.1 — Launch EC2 Instance
```
EC2 → Launch instance
Name: advaitam-web
AMI: Ubuntu Server 24.04 LTS (ARM64)  ← must be ARM64 for t4g
Instance type: t4g.micro
Key pair: Create new → advaitam-key.pem → Download and save safely
Network: default VPC, default subnet
Security group: Create new → advaitam-sg
  Inbound rules:
    SSH    port 22   → My IP (your current IP only)
    HTTP   port 80   → 0.0.0.0/0
    HTTPS  port 443  → 0.0.0.0/0
Storage: 20GB gp3
IAM instance profile: advaitam-ec2-role  ← attach the role from Phase 1
```

### Step 3.2 — Allocate Elastic IP
```
EC2 → Elastic IPs → Allocate → Associate with your instance
Note the IP: XX.XX.XX.XX  (this never changes, even after reboot)
```

### Step 3.3 — SSH Into Server
```bash
# From Windows (PowerShell or Windows Terminal):
ssh -i "C:\path\to\advaitam-key.pem" ubuntu@XX.XX.XX.XX

# Fix key permissions if needed:
icacls advaitam-key.pem /inheritance:r /grant:r "%USERNAME%:R"
```

### Step 3.4 — Server Initial Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx git

# Create app user (don't run app as root or ubuntu)
sudo useradd -m -s /bin/bash advaitam
sudo passwd advaitam   # set a password
```

### Step 3.5 — PostgreSQL Setup
```bash
sudo -u postgres psql

CREATE DATABASE advaitam_db;
CREATE USER advaitam_user WITH PASSWORD 'your_strong_password_here';
ALTER ROLE advaitam_user SET client_encoding TO 'utf8';
ALTER ROLE advaitam_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE advaitam_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE advaitam_db TO advaitam_user;
ALTER DATABASE advaitam_db OWNER TO advaitam_user;
\q
```

### Step 3.6 — Create Virtual Environment
```bash
sudo -u advaitam bash
mkdir -p /home/advaitam/app
cd /home/advaitam
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### Step 3.7 — Push Code from Windows (run on your Windows machine)
```bash
# In D:\webProject on your Windows machine:
git add .
git commit -m "production ready"
git push origin main
```

### Step 3.8 — Clone Code on EC2
```bash
# On EC2, as advaitam user:
cd /home/advaitam/app
git clone https://github.com/KYALLAMRAJU/website .
# (the dot clones into current directory)

# Install dependencies:
source /home/advaitam/venv/bin/activate
pip install -r requirements-prod.txt
```

### Step 3.9 — Create Production .env File
```bash
nano /home/advaitam/app/.env
```

Paste this (fill in your values):
```bash
# ========== DJANGO CORE ==========
DJANGO_ENV=production
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=advaitam.info,www.advaitam.info,origin.advaitam.info,XX.XX.XX.XX

# ========== DATABASE ==========
DB_ENGINE=django.db.backends.postgresql
DB_NAME=advaitam_db
DB_USER=advaitam_user
DB_PASSWORD=your_strong_password_here
DB_HOST=localhost
DB_PORT=5432

# ========== CSRF ==========
CSRF_TRUSTED_ORIGINS=https://advaitam.info,https://www.advaitam.info,https://origin.advaitam.info

# ========== S3 + CLOUDFRONT ==========
USE_S3=True
AWS_STORAGE_BUCKET_NAME=advaitam-assets
AWS_S3_REGION_NAME=us-east-1
# ⚠️ Fill this in AFTER Phase 4 (you get this from CloudFront distribution):
AWS_S3_CUSTOM_DOMAIN=xxxxxxxxxxxx.cloudfront.net
# Leave blank — EC2 IAM Instance Role handles S3 access (no keys needed):
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# ========== EMAIL (AWS SES) ==========
# How to get these credentials:
#   1. AWS Console → SES → SMTP Settings → "Create SMTP Credentials"
#   2. This generates an IAM user with SMTP-specific username & password
#      (these are NOT your normal AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)
#   3. Verify your sender domain (advaitam.info) under SES → Verified Identities
#   4. Request production access to send to any address (default is sandbox only)
#
# SES SMTP endpoints by region:
#   us-east-1  → email-smtp.us-east-1.amazonaws.com
#   us-west-2  → email-smtp.us-west-2.amazonaws.com
#   eu-west-1  → email-smtp.eu-west-1.amazonaws.com
#   ap-south-1 → email-smtp.ap-south-1.amazonaws.com
AWS_SES_REGION_NAME=us-east-1
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_HOST_USER=<SES-SMTP-USERNAME-from-IAM>
EMAIL_HOST_PASSWORD=<SES-SMTP-PASSWORD-from-IAM>
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@advaitam.info
ADMIN_EMAIL=kalyan.py28@gmail.com

# ========== SESSIONS ==========
SESSION_COOKIE_AGE=86400
SESSION_EXPIRE_AT_BROWSER_CLOSE=False

# ========== CLAUDE AI ==========
ANTHROPIC_API_KEY=sk-ant-your-key-here

# ========== SENTRY ERROR TRACKING ==========
SENTRY_DSN=https://your-key@sentry.io/project-id

# ========== CLOUDFRONT ORIGIN PROTECTION ==========
# Use the same value generated above with secrets.token_urlsafe(40):
CLOUDFRONT_SECRET=your-random-secret-here
```

```bash
# Lock down permissions — CRITICAL:
chmod 600 /home/advaitam/app/.env
chown advaitam:advaitam /home/advaitam/app/.env
```

### Step 3.10 — Run Migrations
```bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production
python manage.py migrate
python manage.py createsuperuser
```

> ⚠️ Do NOT run `collectstatic` yet — S3 and CloudFront are not set up yet

---

## 📋 PHASE 4 — CloudFront CDN Setup

### Step 4.1 — Create CloudFront Distribution
```
CloudFront → Create distribution

Origin 1: S3 (for static/media files)
  Origin domain: advaitam-assets.s3.us-east-1.amazonaws.com
  Origin access: Origin access control settings (OAC)
  OAC: advaitam-oac (created in Phase 2)
  Origin path: (leave blank)

Origin 2: EC2 (for Django pages)
  Origin domain: origin.advaitam.info
  Protocol: HTTPS only
  Port: 443
  Add custom header: X-CloudFront-Secret: your-random-secret-here
    (same value as CLOUDFRONT_SECRET in .env)

Behaviors:
  /static/*  → Origin 1 (S3)   Cache policy: CachingOptimized (1 year)
  /media/*   → Origin 1 (S3)   Cache policy: CachingOptimized (7 days)
  /*         → Origin 2 (EC2)  Cache policy: CachingDisabled

Alternate domain names (CNAMEs):
  advaitam.info
  www.advaitam.info

SSL certificate: Custom SSL → select your ACM cert (from Phase 7)
  ⚠️ If cert not showing: make sure you requested it in us-east-1

Default root object: (leave blank — Django handles routing)
```

### Step 4.2 — Note Your CloudFront Domain
```
After creation, note: xxxxxxxxxxxx.cloudfront.net
Update .env: AWS_S3_CUSTOM_DOMAIN=xxxxxxxxxxxx.cloudfront.net
```

### Step 4.3 — Update S3 Bucket Policy
```
Now go back to Phase 2, Step 2.4 and add the bucket policy
Replace:
  YOUR_ACCOUNT_ID → your 12-digit AWS account ID
  YOUR_DISTRIBUTION_ID → your CloudFront distribution ID (e.g. E1ABCD2EFGH3IJ)
```

### Step 4.4 — Run collectstatic (NOW it's safe)
```bash
# On EC2:
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production
python manage.py collectstatic --noinput

# Verify files appeared in S3:
aws s3 ls s3://advaitam-assets/static/ --recursive | head -20
```

---

## 📋 PHASE 5 — Route 53 DNS Setup

### Step 5.1 — Create Hosted Zone
```
Route 53 → Hosted zones → Create hosted zone
Domain name: advaitam.info
Type: Public hosted zone
```

### Step 5.2 — Note the Name Servers
```
After creation, Route 53 gives you 4 nameservers, e.g.:
  ns-123.awsdns-45.com
  ns-678.awsdns-90.net
  ns-234.awsdns-56.org
  ns-789.awsdns-12.co.uk
```

### Step 5.3 — Update Nameservers at Your Domain Registrar
```
Go to wherever you bought advaitam.info (GoDaddy, Namecheap, etc.)
Replace their nameservers with the 4 Route 53 nameservers above
⚠️ DNS propagation takes 5 minutes to 48 hours
```

### Step 5.4 — Create DNS Records
```
In Route 53 hosted zone:

Record 1: advaitam.info
  Type: A
  Alias: Yes
  Route traffic to: CloudFront distribution → select your distribution

Record 2: www.advaitam.info
  Type: A
  Alias: Yes
  Route traffic to: CloudFront distribution → same distribution

Record 3: origin.advaitam.info
  Type: A
  Alias: No
  Value: XX.XX.XX.XX  (your EC2 Elastic IP)
  TTL: 300
```

---

## 📋 PHASE 6 — Gunicorn + Nginx + SSL

### Step 6.1 — Create Gunicorn Socket + Service (systemd)
```bash
# Create socket file:
sudo nano /etc/systemd/system/advaitam.socket
```
```ini
[Unit]
Description=Advaitam Gunicorn Socket

[Socket]
ListenStream=/run/advaitam/gunicorn.sock

[Install]
WantedBy=sockets.target
```

```bash
# Create service file:
sudo nano /etc/systemd/system/advaitam.service
```
```ini
[Unit]
Description=Advaitam Gunicorn Daemon
Requires=advaitam.socket
After=network.target

[Service]
User=advaitam
Group=www-data
WorkingDirectory=/home/advaitam/app
Environment=DJANGO_ENV=production
ExecStart=/home/advaitam/venv/bin/gunicorn \
          --config /home/advaitam/app/gunicorn.conf.py \
          webProject.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start:
sudo mkdir -p /run/advaitam
sudo chown advaitam:www-data /run/advaitam
sudo systemctl daemon-reload
sudo systemctl enable advaitam.socket advaitam.service
sudo systemctl start advaitam.socket
sudo systemctl start advaitam.service
sudo systemctl status advaitam.service
```

### Step 6.2 — SSL Certificate via Certbot (Let's Encrypt for origin.advaitam.info)
```bash
# ⚠️ DNS must be propagated first — test with: nslookup origin.advaitam.info
# origin.advaitam.info must resolve to your EC2 Elastic IP before running this

sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d origin.advaitam.info
# Follow prompts: enter email, agree to TOS, choose redirect (option 2)

# Verify auto-renewal:
sudo certbot renew --dry-run
```

### Step 6.3 — Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/advaitam
```
```nginx
# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name origin.advaitam.info;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name origin.advaitam.info;

    ssl_certificate     /etc/letsencrypt/live/origin.advaitam.info/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/origin.advaitam.info/privkey.pem;

    # Only allow requests from CloudFront (origin protection)
    # This secret must match X-CloudFront-Secret header CloudFront sends
    set $x_cloudfront_secret "your-random-secret-here";  # same as CLOUDFRONT_SECRET in .env

    if ($http_x_cloudfront_secret != $x_cloudfront_secret) {
        return 403;
    }

    client_max_body_size 20M;

    location / {
        proxy_pass http://unix:/run/advaitam/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    access_log /home/advaitam/app/logs/nginx_access.log;
    error_log  /home/advaitam/app/logs/nginx_error.log;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/advaitam /etc/nginx/sites-enabled/
sudo nginx -t   # must say: syntax is ok
sudo systemctl restart nginx
```

---

## 📋 PHASE 7 — ACM Certificate for CloudFront

> ⚠️ **ACM certificates for CloudFront MUST be requested in `us-east-1`** regardless of where your EC2 is!

### Step 7.1 — Request Certificate
```
AWS Console → Switch region to us-east-1
ACM → Request certificate → Request a public certificate
Domain names:
  advaitam.info
  *.advaitam.info        ← covers www, origin, and any future subdomain
Validation method: DNS validation (recommended)
```

### Step 7.2 — Validate via DNS
```
ACM shows you CNAME records to add to Route 53
Click "Create records in Route 53" (automatic)
Wait 5–10 minutes for status to change to "Issued"
```

> ⚠️ Do NOT proceed to CloudFront setup (Phase 4) until cert status = **Issued**

---

## 📋 PHASE 8 — Final Verification

### Step 8.1 — Django Production Check
```bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production
python manage.py check --deploy
# Should show 0 errors (some warnings about HSTS are OK if behind CloudFront)
```

### Step 8.2 — Test All URLs
```bash
# From your Windows machine:
curl -I https://advaitam.info/loginpage/          # should return 200
curl -I https://advaitam.info/static/css/home.css # should return 200 (from S3/CloudFront)
curl -I https://origin.advaitam.info/loginpage/   # should return 403 (origin protection working)
```

### Step 8.3 — Test Email via Django Shell
```bash
sudo -u advaitam bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production

python manage.py shell
>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail('Test', 'Test body', settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
# Should return: 1 (success)
```

### Step 8.4 — Test Static Files
```bash
# Check files are in S3:
aws s3 ls s3://advaitam-assets/static/css/
aws s3 ls s3://advaitam-assets/static/audio/ --recursive | wc -l

# Check CloudFront serves them:
curl -I https://xxxxxxxxxxxx.cloudfront.net/static/css/home.css
```

---

## 📋 PHASE 9 — Security Hardening

### Step 9.1 — Harden SSH
```bash
sudo nano /etc/ssh/sshd_config
# Set:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

sudo systemctl restart sshd
```

### Step 9.2 — Configure UFW Firewall
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### Step 9.3 — Restrict EC2 Security Group
```
EC2 → Security Groups → advaitam-sg
Remove: SSH from 0.0.0.0/0
Add:    SSH from YOUR_HOME_IP/32 only
HTTP/HTTPS remain open (CloudFront needs them)
```

### Step 9.4 — Generate Strong CLOUDFRONT_SECRET
```bash
# On Windows (PowerShell):
python -c "import secrets; print(secrets.token_urlsafe(40))"

# Put this value in BOTH:
# 1. /home/advaitam/app/.env  →  CLOUDFRONT_SECRET=xxxxx
# 2. Nginx config             →  set $x_cloudfront_secret "xxxxx";
# 3. CloudFront custom header →  X-CloudFront-Secret: xxxxx
# All three must be identical
```

### Step 9.5 — Verify Django Security Settings
```bash
python manage.py check --deploy
# These should all be present when DEBUG=False:
# ✅ SECURE_SSL_REDIRECT
# ✅ SESSION_COOKIE_SECURE
# ✅ CSRF_COOKIE_SECURE
# ✅ SECURE_HSTS_SECONDS
# ✅ X_FRAME_OPTIONS
```

---

## 📋 PHASE 10 — Monitoring

### Step 10.1 — CloudWatch Alarms
```
CloudWatch → Alarms → Create alarm

Alarm 1: EC2 CPUUtilization > 80% for 5 minutes → SNS → Email
Alarm 2: EC2 StatusCheckFailed → SNS → Email
```

### Step 10.2 — AWS Budget Alert
```
AWS Billing → Budgets → Create budget
Type: Cost budget
Amount: $10/month
Alert at 80% ($8) → Email: kalyan.py28@gmail.com
Alert at 100% ($10) → Email alert
```

### Step 10.3 — Django Log Rotation
```bash
sudo nano /etc/logrotate.d/advaitam
```
```
/home/advaitam/app/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 advaitam www-data
    sharedscripts
    postrotate
        systemctl reload advaitam.service > /dev/null 2>&1 || true
    endscript
}
```

### Step 10.4 — Enable Sentry (Optional but Recommended)
```bash
# Install:
pip install sentry-sdk

# Add to requirements-prod.txt:
sentry-sdk==2.x.x

# In .env:
SENTRY_DSN=https://your-key@sentry.io/project-id

# Uncomment in settings.py:
# _SENTRY_DSN = env('SENTRY_DSN', default=None)
# if _SENTRY_DSN:
#     import sentry_sdk
#     sentry_sdk.init(dsn=_SENTRY_DSN, traces_sample_rate=0.2, environment='production')
```

---

## 🔄 Deployment Workflow (After Initial Setup)

Every time you make code changes:

```bash
# On your Windows machine:
git add .
git commit -m "describe your change"
git push origin main

# On EC2:
sudo -u advaitam bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
git pull origin main
pip install -r requirements-prod.txt   # only if requirements changed
python manage.py migrate               # only if models changed
python manage.py collectstatic --noinput  # only if static files changed
sudo systemctl restart advaitam.service
sudo systemctl status advaitam.service
```

---

## 🐛 Troubleshooting

### Gunicorn not starting
```bash
sudo systemctl status advaitam.service
journalctl -u advaitam.service -n 50 --no-pager

# Common causes:
# 1. .env not found → check /home/advaitam/app/.env exists and chmod 600
# 2. Import error → activate venv and run: python manage.py check
# 3. Socket dir missing → sudo mkdir -p /run/advaitam && sudo chown advaitam:www-data /run/advaitam
```

### 502 Bad Gateway from Nginx
```bash
# Check gunicorn socket exists:
ls -la /run/advaitam/gunicorn.sock

# Check Nginx can reach it:
sudo -u www-data ls /run/advaitam/

# Check Nginx error log:
tail -50 /home/advaitam/app/logs/nginx_error.log
```

### Static files not loading (404)
```bash
# Check USE_S3=True in .env
# Check AWS_S3_CUSTOM_DOMAIN is set to your CloudFront domain (not S3 URL)
# Check S3 bucket policy allows CloudFront OAC
# Run collectstatic again and verify files appear in S3 console
```

### Database connection errors
```bash
# Check PostgreSQL is running:
sudo systemctl status postgresql

# Test connection manually:
sudo -u advaitam psql -U advaitam_user -d advaitam_db -h localhost
# If this works, the Django DB settings are correct

# Check .env has correct DB_PASSWORD
```

### Email not sending
```bash
# Test email from Django shell:
sudo -u advaitam bash
source /home/advaitam/venv/bin/activate
cd /home/advaitam/app
export DJANGO_ENV=production

python manage.py shell
>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail('Test', 'Test body', settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
# Should return: 1 (success)
# If it raises SMTPAuthenticationError  → check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env
#   (these are SES SMTP credentials, NOT your AWS access keys)
# If it raises SMTPRecipientsRefused    → your SES account is still in sandbox mode;
#   either verify the recipient address in SES, or request SES production access
# If it raises ConnectionRefusedError   → check EMAIL_HOST matches your SES region endpoint
```

### 403 on every request from CloudFront
```bash
# The X-CloudFront-Secret header value doesn't match
# Step 1: Check .env value:
grep CLOUDFRONT_SECRET /home/advaitam/app/.env

# Step 2: Check Nginx config value:
grep x_cloudfront_secret /etc/nginx/sites-available/advaitam

# Both values must be IDENTICAL (no quotes, no spaces)
# After fixing: sudo systemctl restart nginx
```

### Gunicorn logs show "django.db.utils.OperationalError"
```bash
# PostgreSQL isn't running or .env DB settings are wrong
sudo systemctl start postgresql
grep "^DB_" /home/advaitam/app/.env   # verify DB_HOST=localhost, DB_NAME=advaitam_db
```

---

## 📞 Quick Reference

| What | Value |
|---|---|
| EC2 IP | XX.XX.XX.XX (Elastic IP) |
| SSH | `ssh -i advaitam-key.pem ubuntu@XX.XX.XX.XX` |
| App directory | `/home/advaitam/app/` |
| Venv | `/home/advaitam/venv/` |
| .env file | `/home/advaitam/app/.env` |
| Logs | `/home/advaitam/app/logs/` |
| Gunicorn socket | `/run/advaitam/gunicorn.sock` |
| Nginx config | `/etc/nginx/sites-available/advaitam` |
| systemd service | `/etc/systemd/system/advaitam.service` |
| S3 bucket | `advaitam-assets` |
| Database | `advaitam_db` on `localhost:5432` |
| Email | AWS SES — `email-smtp.us-east-1.amazonaws.com:587` |

### Useful Commands (on EC2)
```bash
# Restart app:
sudo systemctl restart advaitam.service

# View live logs:
journalctl -u advaitam.service -f

# Check Django:
sudo -u advaitam bash -c "source /home/advaitam/venv/bin/activate && cd /home/advaitam/app && DJANGO_ENV=production python manage.py check"

# Check disk space:
df -h

# Check memory:
free -h

# Check what's listening on ports:
ss -tlnp
```
````
