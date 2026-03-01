# 🔒 Security Scanning - Both Development & Production

**Date:** February 23, 2026  
**Updated:** Covers both requirements.txt and requirements-prod.txt

---

## 📋 Quick Answer

**YES, you should scan BOTH files:**

✅ **requirements-prod.txt** (Production)
- Scanned ✅ Already done - 0 CVEs found
- Use for: Production EC2 deployment
- When: Before deploying, monthly checks

✅ **requirements.txt** (Local Development)
- Should scan regularly
- Use for: Local development environment
- When: Before committing code

---

## 📊 Why Both Files?

### Local Development (requirements.txt)
**Why it matters:**
- Your local machine runs these packages
- Could have vulnerabilities you develop against
- Testing dependencies might have issues
- Development tools can have security problems

**Vulnerabilities risk:**
- You might commit code that uses vulnerable dev packages
- Colleagues using your repo would inherit vulnerabilities
- Could introduce bad practices into codebase

### Production (requirements-prod.txt)
**Why it matters:**
- Live users depend on these packages
- Direct internet exposure
- Data security concerns
- Performance & stability critical

**Vulnerabilities risk:**
- Direct attacks on production
- Data breaches
- Service outages
- Security incidents

---

## 🎯 Security Scanning Strategy

### LAYER 1: Local Development - SCAN BOTH FILES

```bash
# Scan development requirements (before committing)
.\.venv\Scripts\safety check --file requirements.txt

# Scan production requirements (before deploying)
.\.venv\Scripts\safety check --file requirements-prod.txt
```

**When:** Before each commit & push to GitHub

### LAYER 2: GitHub - Dependabot Watches BOTH

Your `.github/dependabot.yml` is configured to watch:
- ✅ requirements.txt
- ✅ requirements-prod.txt

**Frequency:** Daily automatic scanning

### LAYER 3: Production - SCAN Production File

```bash
ssh -i key.pem ubuntu@<EC2-IP>
cd /home/advaitam/app
source venv/bin/activate
safety check --file requirements-prod.txt
```

**When:** Monthly (1st of month)

---

## 📁 File Comparison

| Aspect | requirements.txt | requirements-prod.txt |
|--------|-----------------|----------------------|
| **Purpose** | Local development | Production server |
| **Packages** | All (dev + prod) | Production only |
| **Size** | Larger (150 lines) | Smaller (46 lines) |
| **Should scan** | YES ✅ | YES ✅ |
| **Frequency** | Before each commit | Before deploy + monthly |
| **Dependencies** | Testing, debugging tools | Only what's needed |

---

## 📦 Package Breakdown

### requirements.txt (Local - 150 packages)
Contains:
- ✅ All production packages
- ✅ Testing packages (pytest, coverage, etc.)
- ✅ Development tools (black, flake8, etc.)
- ✅ Debugging tools (debugpy, ipython, etc.)
- ✅ Code quality tools (mypy, pylint, etc.)

**Example extra packages:**
```
pytest
black
flake8
mypy
ipython
jupyter
factory-boy
faker  (you have fakerdata.py!)
```

### requirements-prod.txt (Production - 46 packages)
Contains:
- ✅ Core Django
- ✅ Database (PostgreSQL)
- ✅ REST API framework
- ✅ Authentication
- ✅ Storage (S3)
- ✅ Caching (Redis)
- ✅ Monitoring
- ✅ Error tracking

**No extra packages** for testing/debugging

---

## 🔒 Current CVE Status

### requirements-prod.txt
- ✅ **0 CVEs** (all 4 fixed)
- ✅ All scanned and verified
- ✅ Production-ready

### requirements.txt
- **NOT YET SCANNED** (should be!)
- Check for development-specific vulnerabilities
- May have different CVEs than prod

---

## 🚀 Recommended Scanning Workflow

### Daily (Before Committing Code)

```bash
# Step 1: Scan development requirements
.\.venv\Scripts\safety check --file requirements.txt

# Step 2: Scan production requirements
.\.venv\Scripts\safety check --file requirements-prod.txt

# Step 3: If all clear, commit
git commit -m "your changes"
git push origin main
```

### Weekly (GitHub Check)

Go to GitHub and check for Dependabot PRs
- Look for: Pull Requests with "security" label
- Review: Both requirements files scanned by Dependabot
- Merge: If tests pass

### Monthly (Production Verification)

```bash
# Run on EC2 server on 1st of month
safety check --file requirements-prod.txt
```

---

## ❓ Common Questions

### Q: Do I need different versions in requirements.txt vs requirements-prod.txt?

**A: Generally YES, here's why:**

**Development (requirements.txt):**
```
Django==5.2.9
pytest==8.0.0          ← Only in dev
black==24.1.1          ← Only in dev
django-stubs==5.0.0    ← Only in dev
```

**Production (requirements-prod.txt):**
```
Django==5.2.9
# No testing/formatting tools
```

**Same packages CAN be pinned to same version**, but you don't need testing tools in production.

### Q: If requirements.txt has a CVE, must I update it?

**A: YES! Here's why:**

1. **You develop with it** - The CVE affects your local machine
2. **Team members use it** - Others inherit the vulnerability
3. **Tests run against it** - CI/CD pipeline affected
4. **Code quality** - Shows bad security practices

### Q: Can Dependabot watch both files?

**A: YES! ✅**

Your `.github/dependabot.yml` is already configured to watch pip:
```yaml
package-ecosystem: "pip"
directory: "/"  # Watches all .txt files in root
```

This means Dependabot scans:
- ✅ requirements.txt
- ✅ requirements-prod.txt
- ✅ Any other .txt files

### Q: What if they have different CVEs?

**A: Good catch!**

They could have different vulnerabilities:

```
requirements.txt might have:
  ❌ pytest==7.0.0 (old, has CVE)
  ✅ Django==5.2.9 (safe)

requirements-prod.txt might have:
  ✅ Django==5.2.9 (safe)
  (doesn't have pytest)
```

**Action:** Fix the CVE in whichever file has it.

---

## 📋 Security Scanning Checklist

### Local Development (Before Committing)

- [ ] Run: `safety check --file requirements.txt`
- [ ] Run: `safety check --file requirements-prod.txt`
- [ ] If CVEs found:
  - [ ] Note the CVE ID
  - [ ] Find patched version
  - [ ] Update requirements file
  - [ ] Re-run safety check
  - [ ] Test locally
  - [ ] Then commit

### Before Production Deployment

- [ ] Run: `safety check --file requirements-prod.txt`
- [ ] Verify: 0 CVEs
- [ ] Review: All versions current
- [ ] Deploy: Using deploy.sh
- [ ] Verify: Application working

### Monthly Production Check (1st of month)

- [ ] SSH into EC2
- [ ] Run: `safety check --file requirements-prod.txt`
- [ ] Document: Any findings
- [ ] If CVEs: Create ticket to fix

---

## 🔄 Update Strategy

### When to Update Which File?

| Scenario | Update | Why |
|----------|--------|-----|
| Testing tool CVE | requirements.txt | Affects your development |
| Production package CVE | Both files | Need it everywhere |
| New dev tool needed | requirements.txt only | Not used in production |
| Django security patch | Both files | Critical for safety |

### Example Workflow

```
Scenario: Django security patch released (5.2.9 → 5.2.10)

Step 1: Update requirements-prod.txt
  Django==5.2.9 → Django==5.2.10

Step 2: Update requirements.txt
  Django==5.2.9 → Django==5.2.10

Step 3: Test locally
  pip install -r requirements.txt
  python manage.py test

Step 4: Scan both files
  safety check --file requirements.txt
  safety check --file requirements-prod.txt

Step 5: Commit & push
  git commit -m "security: bump Django to 5.2.10"

Step 6: Deploy to production
  bash deploy.sh
```

---

## 📖 Summary

### Do We Need to Scan Both?

✅ **YES! Absolutely!**

- **requirements.txt** → Scan before committing (protects development)
- **requirements-prod.txt** → Scan before deploying (protects production)

### Scanning Schedule

```
Daily:    Scan both before committing (you)
Daily:    Dependabot scans both automatically (GitHub)
Weekly:   Check GitHub for security PRs (you)
Monthly:  Scan production file on EC2 (you)
```

### Commands to Use

```bash
# Development scan
.\.venv\Scripts\safety check --file requirements.txt

# Production scan (local)
.\.venv\Scripts\safety check --file requirements-prod.txt

# Production scan (EC2 monthly)
ssh... && safety check --file requirements-prod.txt
```

### Bottom Line

**Scan BOTH files:**
- Protects your development environment
- Protects production deployment
- Catches all vulnerabilities
- Industry best practice
- Takes only 20 seconds total

---

## ✅ Next Steps

1. **Scan requirements.txt now:**
   ```bash
   .\.venv\Scripts\safety check --file requirements.txt
   ```

2. **Document any CVEs found**

3. **Add to your workflow:**
   - Before every commit: scan both
   - Before every deploy: scan prod file
   - Monthly: check EC2

4. **Dependabot will help:**
   - Creates PRs for security updates
   - Watches both files automatically
   - You just review & merge

---

**Status: Covered! Both files should be scanned regularly.** ✅

