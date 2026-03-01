# 📘 deploy.yml — Plain English Explanation

## What Is This File?

Think of `deploy.yml` as a **robot assistant** that lives on GitHub.

Every time you push code to GitHub, this robot automatically:
1. **Tests** your code to make sure nothing is broken
2. **Deploys** (copies) your code to your AWS EC2 server

You never have to manually SSH into the server and run commands — the robot does it for you.

---

## Where Does It Live?

```
.github/
  workflows/
    deploy.yml    ← this file
```

GitHub looks specifically in `.github/workflows/` for automation files.

---

## The Big Picture

```
YOU push code to GitHub
        │
        ▼
GitHub sees the push
        │
        ▼
GitHub starts the robot (GitHub Actions)
        │
        ├─── Job 1: TEST ──────────────────────────────────
        │      Start a temporary Ubuntu computer
        │      Install Python 3.12
        │      Install all requirements
        │      Run database migrations
        │      Run your tests
        │      Run Django checks
        │      If ANY step fails → STOP, don't deploy
        │
        └─── Job 2: DEPLOY (only runs if Job 1 passed) ────
               SSH into your EC2 server
               git pull (download latest code)
               pip install (update packages)
               migrate (update database)
               collectstatic (upload files to S3)
               restart Gunicorn (apply code changes)
               reload Nginx (apply config changes)
```

---

## Line-by-Line Explanation

### Section 1: When Does This Run?

```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
```

**Plain English:**
- Run this robot when someone **pushes code** to the `main` branch
- Also run tests (but NOT deploy) when someone opens a **Pull Request** to main

**Why?**
- You never want untested code to reach your live server
- Pull Requests let you test code BEFORE merging it into main

---

### Section 2: The TEST Job

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
```

**Plain English:**
- GitHub spins up a **fresh Ubuntu computer** in the cloud (free!)
- This computer exists only for the duration of this test
- It gets deleted afterwards — clean slate every time

---

### Section 3: Setting Up a Test Database

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_DB: advaitam_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
```

**Plain English:**
- Spins up a **temporary PostgreSQL database** just for testing
- This is NOT your real database — it's a throwaway test database
- Gets deleted when the test finishes
- Uses simple credentials (`postgres`/`postgres`) because it's not real data

```yaml
options: >-
  --health-cmd pg_isready
  --health-interval 10s
  --health-timeout 5s
  --health-retries 5
```

**Plain English:**
- Wait for the database to actually be ready before running tests
- Check every 10 seconds, give up after 5 failed attempts
- Prevents tests from failing just because the DB wasn't ready yet

```yaml
ports:
  - 5432:5432
```

**Plain English:**
- Make the database accessible on port 5432 (standard PostgreSQL port)
- Django in the test needs to connect to it

---

### Section 4: Step-by-Step Test Actions

#### Step 1: Download Your Code
```yaml
- uses: actions/checkout@v4
```
Downloads your code from GitHub onto the temporary Ubuntu computer.

---

#### Step 2: Install Python
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
```
Installs Python 3.12 — same version as your EC2 server.

**Why match versions?** If tests pass on Python 3.12 and your server runs 3.12, you know the code will work.

---

#### Step 3: Install Dependencies
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements-prod.txt
```
Installs all the Python packages your project needs (Django, psycopg2, boto3, etc.)

Uses `requirements-prod.txt` (not `requirements.txt`) because you want to test with the same packages that run in production.

---

#### Step 4: Run Database Migrations
```yaml
- name: Run migrations
  env:
    DEBUG: False
    SECRET_KEY: test-secret-key-not-used-in-production
    DB_NAME: advaitam_test
    ...
    USE_S3: False
  run: python manage.py migrate
```

**Plain English:**
- Creates all the database tables in the temporary test database
- Uses fake/test values for SECRET_KEY and DB credentials
- `USE_S3: False` — don't try to connect to AWS S3 during tests (it would fail without real AWS keys)

---

#### Step 5: Run Tests
```yaml
- name: Run tests
  run: python manage.py test
```
Runs all the test files in your `webapp/tests/` folder.

If any test fails → the whole workflow stops → code does NOT get deployed. 🛡️

---

#### Step 6: Django Check
```yaml
- name: Check Django
  run: python manage.py check --deploy
```

**Plain English:**
- Runs Django's built-in security checklist
- Checks for common misconfigurations before going live
- `--deploy` flag enables extra production-only checks
- Examples: Is DEBUG=False? Are cookies secure? Is HSTS enabled?

---

### Section 5: The DEPLOY Job

```yaml
deploy:
  needs: test
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

**Plain English:**
- `needs: test` → Only runs AFTER the test job passes successfully
- `github.ref == 'refs/heads/main'` → Only deploys from the `main` branch (not from other branches)
- `github.event_name == 'push'` → Only deploys on real pushes, NOT on pull requests

**Combined meaning:** Only deploy to the live server when:
✅ All tests passed AND
✅ We're on the main branch AND
✅ It was an actual push (not just a PR preview)

---

### Section 6: The SSH Deploy Steps

```yaml
- name: Deploy to EC2
  env:
    PRIVATE_KEY: ${{ secrets.AWS_EC2_PRIVATE_KEY }}
    HOST: ${{ secrets.AWS_EC2_HOST }}
    USER: ubuntu
```

**Plain English:**
- `secrets.AWS_EC2_PRIVATE_KEY` — Your EC2 SSH private key, stored securely in GitHub Secrets (never visible in the code)
- `secrets.AWS_EC2_HOST` — Your EC2 server's IP address or domain, also in GitHub Secrets
- `USER: ubuntu` — The SSH username (ubuntu is default for AWS EC2 Ubuntu servers)

---

```yaml
run: |
  mkdir -p ~/.ssh
  echo "$PRIVATE_KEY" > ~/.ssh/deploy_key.pem
  chmod 600 ~/.ssh/deploy_key.pem
  ssh-keyscan -H $HOST >> ~/.ssh/known_hosts
```

**Plain English:**
1. Create the `.ssh` folder
2. Write the private key to a file
3. `chmod 600` — restrict permissions so only the owner can read it (SSH requires this)
4. `ssh-keyscan` — pre-approve the server's fingerprint so SSH doesn't ask "are you sure you want to connect?"

---

```yaml
ssh -i ~/.ssh/deploy_key.pem $USER@$HOST << 'EOF'
  cd /home/advaitam/app
  git pull origin main
  source /home/advaitam/venv/bin/activate
  pip install -r requirements-prod.txt
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  sudo systemctl restart advaitam.service
  sudo systemctl reload nginx
EOF
```

**Plain English — what runs ON YOUR EC2 SERVER:**

| Command | What it does |
|---------|-------------|
| `cd /home/advaitam/app` | Go to your project folder |
| `git pull origin main` | Download the latest code from GitHub |
| `source .../activate` | Switch to your Python virtual environment |
| `pip install -r requirements-prod.txt` | Install any new/updated packages |
| `python manage.py migrate --noinput` | Apply any new database changes |
| `python manage.py collectstatic --noinput` | Upload static files to S3 |
| `systemctl restart advaitam.service` | Restart Gunicorn with the new code |
| `systemctl reload nginx` | Reload Nginx config (no downtime) |

---

## GitHub Secrets You Must Set

Before this workflow can deploy, go to:
**GitHub → Your Repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Value |
|-------------|-------|
| `AWS_EC2_PRIVATE_KEY` | Contents of your `.pem` key file (the whole text) |
| `AWS_EC2_HOST` | Your EC2 public IP or domain (e.g. `54.123.45.67`) |

---

## Summary Flow

```
git push origin main
      │
      ▼
GitHub Actions starts
      │
      ▼
[TEST JOB] ─── fails? ──→ STOP. Email you. Don't deploy.
      │
   passes
      │
      ▼
[DEPLOY JOB]
      │
      ▼
SSH into EC2
      │
      ▼
Pull code + install + migrate + collectstatic + restart
      │
      ▼
✅ Your live site is updated!
```

**Total time:** Usually 3–5 minutes from `git push` to live.

