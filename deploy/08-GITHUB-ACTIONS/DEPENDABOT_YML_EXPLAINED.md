# 📘 dependabot.yml — Plain English Explanation

## What Is This File?

Think of Dependabot as a **security guard** that watches your Python packages 24/7.

Every day it checks:
- Are any of your packages outdated?
- Do any packages have **known security vulnerabilities (CVEs)**?

If it finds something, it automatically opens a **Pull Request** on GitHub with the fix — like a colleague saying *"Hey, Django has a security patch, want me to update it?"*

You just review and click **Merge**. No manual work.

---

## Where Does It Live?

```
.github/
  dependabot.yml    ← this file
```

GitHub reads this automatically — no setup needed beyond this file.

---

## Why Does This Matter?

Real example: In 2024, Django released a security patch for a SQL injection vulnerability.

**Without Dependabot:**
- You might not notice for weeks or months
- Your live site stays vulnerable
- Hackers could exploit it

**With Dependabot:**
- Next morning at 3:00 AM it detects the vulnerability
- Opens a Pull Request: *"Update Django from 5.2.8 to 5.2.9 (security fix)"*
- You review and merge — done in 2 minutes

---

## Line-by-Line Explanation

### Section 1: Version

```yaml
version: 2
```

Just tells GitHub which version of the Dependabot config format to use. Always `2` for modern setups.

---

### Section 2: What to Watch

```yaml
updates:
  - package-ecosystem: "pip"
    directory: "/"
```

**Plain English:**
- `package-ecosystem: "pip"` → Watch Python packages (pip is Python's package manager)
- `directory: "/"` → Look in the root folder of the project for the requirements files

---

### Section 3: Which File to Watch

```yaml
files:
  include:
    - "requirements-prod.txt"
```

**Plain English:**
- Only watch `requirements-prod.txt` — your production dependencies
- Ignores `requirements.txt` (dev file) — you don't want to clutter PRs with dev tool updates
- This keeps focus on packages that actually run on your live server

---

### Section 4: Schedule

```yaml
schedule:
  interval: "daily"
  time: "03:00"
```

**Plain English:**
- Check for updates **every day at 3:00 AM**
- Why 3 AM? Low traffic time — even if something goes wrong, minimal users are affected
- Other options you could use: `"weekly"` or `"monthly"`

---

### Section 5: Limit PRs

```yaml
open-pull-requests-limit: 5
```

**Plain English:**
- Maximum 5 open Dependabot PRs at a time
- Prevents your GitHub from being flooded with 20 update PRs at once
- Once you merge or close some, it can open new ones

---

### Section 6: Who Gets Notified

```yaml
reviewers:
  - "KYALLAMRAJU"
assignees:
  - "KYALLAMRAJU"
```

**Plain English:**
- When Dependabot opens a PR, it tags **you** as the reviewer and assignee
- You get an email notification
- Replace `KYALLAMRAJU` with your actual GitHub username if it ever changes

---

### Section 7: Labels

```yaml
labels:
  - "security"
  - "dependencies"
```

**Plain English:**
- Dependabot PRs get tagged with these labels automatically
- Makes it easy to filter: *"Show me all security PRs"*
- You need to create these labels in your GitHub repo once:
  **GitHub → Repo → Issues → Labels → New label**

---

### Section 8: Commit Message Format

```yaml
commit-message:
  prefix: "security:"
  include: "scope"
```

**Plain English:**
- All Dependabot commits will start with `security:` in the message
- Example: `security: bump Django from 5.2.8 to 5.2.9`
- This keeps your git history clean and easy to search
- `include: "scope"` adds the package name to the message

---

### Section 9: What Type of Updates

```yaml
allow:
  - dependency-type: "production"
```

**Plain English:**
- Only update **production dependencies** (packages in `requirements-prod.txt`)
- Does NOT update dev/test tools
- Keeps it focused on what affects your live server

---

### Section 10: PR Branch Naming

```yaml
pull-request-branch-name:
  separator: "/"
```

**Plain English:**
- Dependabot PRs will use `/` as separator in branch names
- Example branch name: `dependabot/pip/Django-5.2.9`
- Just a cosmetic preference for how branches are named

---

## What a Dependabot PR Looks Like

When Dependabot finds an update, you'll see this on GitHub:

```
🔒 security: bump Django from 5.2.8 to 5.2.9

Bumps Django from 5.2.8 to 5.2.9

Security advisory:
  CVE-2025-XXXX — SQL injection vulnerability in QuerySet.filter()
  Severity: HIGH

Changelog:
  https://docs.djangoproject.com/en/5.2/releases/5.2.9/

Commits:
  abc1234 Fixed SQL injection in filter()
  def5678 Security patch for...

[Review changes] [Merge pull request]
```

---

## Your Workflow When Dependabot Opens a PR

```
Dependabot opens PR at 3 AM
        │
        ▼
You get email notification
        │
        ▼
Go to GitHub → Pull Requests
        │
        ▼
Read the PR — is it just a patch version? (e.g. 5.2.8 → 5.2.9)
        │
        ├── Patch version (5.2.x) → Usually safe → Merge ✅
        │
        ├── Minor version (5.x.0) → Read changelog first → Merge if safe ✅
        │
        └── Major version (x.0.0) → Test locally first → Careful ⚠️
```

---

## What Is a CVE?

**CVE = Common Vulnerabilities and Exposures**

It's a public database of known security holes in software.
Each one gets an ID like `CVE-2025-12345`.

Example:
- `CVE-2024-38875` — Django had a denial-of-service vulnerability in `urlpatterns`
- Dependabot would have caught this and told you to upgrade

---

## Summary

| Feature | What It Does |
|---------|-------------|
| Watches `requirements-prod.txt` | Monitors your production packages |
| Runs daily at 3 AM | Checks for new vulnerabilities every day |
| Opens Pull Requests | Proposes the fix automatically |
| Tags you as reviewer | Notifies you via email |
| Max 5 PRs at once | Keeps things manageable |
| Labels PRs as "security" | Easy to find and filter |
| Only production deps | Stays focused on what matters |

**Bottom line:** Dependabot means you'll never accidentally run a vulnerable version of Django, psycopg2, boto3, or any other package on your live server — because it tells you about it before it becomes a problem.

