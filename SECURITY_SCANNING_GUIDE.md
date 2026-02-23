# 🔒 Security Scanning Guide — Local vs Production

**Date:** February 22, 2026  
**Project:** Advaitam Django Website

---

## 📋 Overview

Security scanning checks your Python packages for **known CVEs (Common Vulnerabilities and Exposures)** that could put your app at risk.

You should scan in **3 places:**
1. ✅ **Local (your machine)** — Before committing code
2. ✅ **GitHub** — Automatically via Dependabot
3. ✅ **Production (EC2)** — Monthly maintenance

---

## 🏠 LOCAL SECURITY SCANNING (Development)

### When to Run
- Before committing code to GitHub
- After installing new packages
- During development setup

### How to Run

```bash
cd D:\webProject
.\.venv\Scripts\safety check --file requirements-prod.txt
```

### What It Does
- Scans all packages in `requirements-prod.txt`
- Checks against safety.io vulnerability database
- Reports CVEs with severity levels
- Shows remediation steps

### Example Output
```
Found and scanned 23 packages
0 vulnerabilities reported  ✅ ALL GOOD!
```

### If Vulnerabilities Found
1. Read the CVE details (what's vulnerable)
2. Update package versions in `requirements-prod.txt`
3. Run `pip install -r requirements-prod.txt` to update locally
4. Re-run safety check to verify fix
5. Test your app still works
6. Commit the updated `requirements-prod.txt`

---

## 🤖 AUTOMATED SCANNING (GitHub Dependabot)

### What It Does
- Automatically scans your repo **daily**
- Creates **Pull Requests** when vulnerabilities found
- Suggests fixes
- Works **24/7** without you doing anything

### Setup
GitHub Dependabot is now enabled via `.github/dependabot.yml`

### How to Use
1. Go to your GitHub repo
2. Click **"Pull Requests"** tab
3. Look for PRs labeled `security`
4. Review the changes
5. Merge the PR (GitHub will run tests first)

### Example
```
Dependabot: Bump django from 5.2.8 to 5.2.9
  - Fixes CVE-2025-64460 (DOS in XML Deserializer)
  - Fixes CVE-2025-13372 (SQL injection)
```

---

## 🚀 PRODUCTION SCANNING (EC2 Server)

### When to Run
- Monthly maintenance (1st of month)
- Before major deploys
- If you suspect a vulnerability

### How to Run

```bash
# 1. SSH into your EC2 server
ssh -i your-key.pem ubuntu@<EC2-IP>

# 2. Navigate to app directory
cd /home/advaitam/app

# 3. Activate virtual environment
source /home/advaitam/venv/bin/activate

# 4. Install safety (one-time)
pip install safety

# 5. Run security scan
safety check --file requirements-prod.txt
```

### What It Checks
- Exactly what's running on your live server
- Not what's in your local environment
- Verifies production dependencies are safe

### Expected Output (If All Safe)
```
Found and scanned 23 packages
0 vulnerabilities reported ✅ ALL GOOD!
```

### If Vulnerabilities Found in Production
1. **Do NOT panic** — Vulnerabilities don't mean active attacks
2. Create an update plan (don't update immediately)
3. Test updates in local environment first
4. Deploy updated code to EC2 using `deploy.sh`
5. Re-run safety check to verify

---

## 📊 Comparison: Local vs Production

| Aspect | Local | Production |
|--------|-------|-----------|
| **Frequency** | Before each commit | Monthly |
| **Environment** | Your development machine | Live EC2 server |
| **Automation** | Manual (you run it) | Manual (you SSH in) |
| **What It Checks** | requirements-prod.txt | What's actually running |
| **Action on CVE** | Update locally & test | Plan careful update |

---

## ✅ STEP-BY-STEP: Setting Up Security Scanning

### Step 1: Local Security Scanning (Right Now)

```bash
cd D:\webProject
.\.venv\Scripts\safety check --file requirements-prod.txt
```

✅ **You already did this!** No vulnerabilities found.

---

### Step 2: Commit Dependabot Config to GitHub

```bash
cd D:\webProject
git add .github/dependabot.yml
git commit -m "security: add dependabot configuration for automatic vulnerability scanning"
git push origin main
```

✅ **Dependabot now monitors your repo 24/7**

---

### Step 3: Monthly Production Scan (Later)

Create a calendar reminder for the 1st of each month:
```bash
ssh -i your-key.pem ubuntu@<EC2-IP>
cd /home/advaitam/app
source /home/advaitam/venv/bin/activate
safety check --file requirements-prod.txt
```

---

## 🛡️ Security Scanning Workflow

### Your Development Cycle

```
1. Write Code Locally
   ↓
2. Run Local Safety Check ← YOU
   .\.venv\Scripts\safety check --file requirements-prod.txt
   ↓
3. Commit & Push to GitHub
   ↓
4. GitHub Dependabot Runs ← AUTOMATED (24/7)
   - Scans for CVEs daily
   - Creates PRs if vulnerabilities found
   ↓
5. Review & Merge Dependabot PR
   ↓
6. Deploy to Production
   ↓
7. Run Production Safety Check ← YOU (Monthly)
   safety check --file requirements-prod.txt (on EC2)
```

---

## 📋 Maintenance Schedule

### Daily
- Nothing (Dependabot watches automatically)

### Weekly
- Check GitHub for security PRs from Dependabot
- Merge if tests pass

### Monthly (1st of month)
- SSH into EC2
- Run: `safety check --file requirements-prod.txt`
- Document results

### Quarterly (Every 90 days)
- Review all merged security updates
- Check if any CVEs were missed
- Update scanning procedures if needed

---

## 🚨 What to Do If CVE Found

### Priority Levels

**CRITICAL (fix immediately):**
- Active exploits known
- Security bypass vulnerabilities
- Authentication/encryption breaks

**HIGH (fix within 1 week):**
- Remote code execution possible
- Data exposure risk
- Privilege escalation

**MEDIUM (fix within 1 month):**
- Denial of service
- Information disclosure
- Limited impact

**LOW (fix at next release):**
- Minor issues
- Difficult to exploit
- Low impact

### Steps to Fix

```
1. Identify CVE severity
2. Find fixed version in PyPI
3. Update requirements-prod.txt
4. Test locally:
   pip install -r requirements-prod.txt
   python manage.py test
5. Run safety check again
6. If fixed: commit & push
7. If not fixed: investigate further
```

---

## 💡 Pro Tips

### Tip 1: Automate Daily Local Checks
Add to your task scheduler (Windows):
```batch
cd D:\webProject
.\.venv\Scripts\safety check --file requirements-prod.txt
```

### Tip 2: Export Safety Reports
```bash
.\.venv\Scripts\safety check --file requirements-prod.txt --json > safety-report.json
```

### Tip 3: Ignore False Positives
If a CVE doesn't apply to your setup:
```bash
safety check --file requirements-prod.txt --ignore 12345
```

### Tip 4: GitHub Notifications
Go to GitHub repo → Settings → Notifications
- Enable security alerts
- You'll be notified instantly of new CVEs

---

## 📚 Additional Resources

- **Safety.io:** https://safety.io/
- **CVE Database:** https://cve.mitre.org/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **GitHub Security:** https://github.com/features/security

---

## ✅ Your Current Status

| Check | Status |
|-------|--------|
| Local scanning setup | ✅ Done |
| Safety check run | ✅ Done - 0 CVEs |
| Dependabot configured | ✅ Done |
| Production scanning procedure | ✅ Documented |

**You're all set!** Your security scanning is now configured for local, automated, and production environments.

---

**Last Updated:** February 22, 2026  
**Next Action:** Commit `.github/dependabot.yml` to GitHub

