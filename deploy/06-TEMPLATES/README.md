# ?? 06-TEMPLATES
**Configuration templates & examples**
This folder contains configuration file templates that you copy and customize for your deployment.
## ?? Files in This Folder
### **README.md** (This file)
Navigation and overview of templates
### **.env.prod.template** ? MAIN FILE
Production environment variables template
**Contains sections for:**
- Core Django settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- Database configuration (PostgreSQL on EC2)
- AWS S3 & CloudFront configuration
- Email settings (Amazon SES or Gmail)
- Session and cache settings
- Anthropic Claude API key
- Sentry error tracking (optional)
- CloudFront origin protection
**How to use:**
1. Copy: cp .env.prod.template .env.production.bak
2. Edit: nano .env.production.bak (fill in YOUR values)
3. Deploy: Upload to EC2
4. Security: chmod 600 .env.production.bak (read-only for root)
## ?? Template Variables
### Required Variables
`
SECRET_KEY=<generate-random-key>
DEBUG=False
ALLOWED_HOSTS=advaitam.info,www.advaitam.info,origin.advaitam.info
DB_NAME=advaitam_db
DB_USER=advaitam_user
DB_PASSWORD=<strong-password>
DB_HOST=localhost
AWS_STORAGE_BUCKET_NAME=advaitam-assets
AWS_S3_CUSTOM_DOMAIN=d123456.cloudfront.net
`
### Optional Variables
`
ANTHROPIC_API_KEY=sk-ant-...
SENTRY_DSN=https://...@sentry.io/...
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
`
## ?? Files Included
| File | Purpose | How to Use |
|------|---------|-----------|
| .env.prod.template | Environment variables | Copy ? Edit ? Deploy |
## ?? Setup Workflow
**1. Prepare Local Environment**
`ash
cp 06-TEMPLATES/.env.prod.template .env.production.bak
nano .env.production.bak  # Fill in YOUR values
`
**2. Verify Locally**
`ash
# Test with local settings
python manage.py check
`
**3. Deploy to Production**
`ash
# Upload to EC2
scp -i key.pem .env.production.bak ubuntu@<EC2-IP>:/home/advaitam/app/
ssh -i key.pem ubuntu@<EC2-IP>
chmod 600 /home/advaitam/app/.env.production.bak
`
**4. Verify on EC2**
`ash
python manage.py check
python manage.py collectstatic --noinput
`
## ?? Security Best Practices
**For .env files:**
- [ ] Never commit to Git (included in .gitignore)
- [ ] Set file permissions: chmod 600 .env.production.bak
- [ ] Never share with team (keep locally secure)
- [ ] Rotate secrets every 90 days
- [ ] Backup encrypted copies
**For SECRET_KEY:**
- Generate random: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
- Unique for each environment
- Never reuse between projects
**For Passwords:**
- Use strong passwords (16+ chars)
- Mix: uppercase, lowercase, numbers, symbols
- Generate: openssl rand -base64 16
**For API Keys:**
- Limit permissions to only needed resources
- Rotate quarterly
- Monitor usage
- Revoke if compromised
## ? Status
- ? Template complete and documented
- ? All variables explained
- ? Security best practices included
- ? Ready to customize
## ??? Next Steps
1. Copy .env.prod.template ? .env.production.bak
2. Edit and fill in YOUR values
3. Use in deployment (copy to EC2)
4. Secure with chmod 600
?? Next: Follow deployment steps in 02-DEPLOYMENT-CONCEPTS/ and 04-CHECKLISTS/
