# 08 — GitHub Actions (CI/CD)

## What's in This Folder

| File | What It Explains |
|------|-----------------|
| `DEPLOY_YML_EXPLAINED.md` | Full plain-English walkthrough of `.github/workflows/deploy.yml` — your automated test + deploy robot |
| `DEPENDABOT_YML_EXPLAINED.md` | Full plain-English walkthrough of `.github/dependabot.yml` — your automated security guard |

---

## One-Line Summary

- **deploy.yml** → *"Every time I push code, automatically test it and deploy it to EC2"*
- **dependabot.yml** → *"Every day, check if any of my packages have security vulnerabilities and tell me"*

---

## The Actual Files These Explain

```
.github/
  workflows/
    deploy.yml        ← CI/CD pipeline (test + deploy)
  dependabot.yml      ← Automated dependency security scanning
```

---

## Before You Deploy — GitHub Secrets Required

The `deploy.yml` needs two secrets set in GitHub before it can SSH into your EC2:

**GitHub → Your Repo → Settings → Secrets and variables → Actions**

| Secret Name | What to Put There |
|-------------|------------------|
| `AWS_EC2_PRIVATE_KEY` | The full contents of your `.pem` key file |
| `AWS_EC2_HOST` | Your EC2 public IP address (e.g. `54.123.45.67`) |

Without these, the deploy step will fail.

