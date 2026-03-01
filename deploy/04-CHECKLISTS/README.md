# ? 04-CHECKLISTS
**Pre-deployment verification checklists**
This folder contains checklists to verify your deployment is complete and correct before going live.
## ?? Files in This Folder
### **README.md** (This file)
Navigation and overview of checklists
### **CHECKLIST_COMPLETE.md** ? MAIN FILE (41 items)
Master pre-deployment checklist covering:
**Code & Configuration (10 items)**
- settings.py production settings
- requirements-prod.txt versions
- .env.production.bak file ready
- Database migrations planned
- Static files configuration
**Infrastructure (5 items)**
- EC2 security groups configured
- Route 53 DNS records ready
- S3 bucket created & configured
- CloudFront distribution created
- SSL certificates ready
**Security (4 items)**
- HTTPS enabled
- HSTS headers configured
- CSP security headers set
- CSRF protection enabled
**Database (4 items)**
- PostgreSQL ready on EC2
- Database backups configured
- Test database prepared
- Migration scripts ready
**Monitoring & Alerts (7 items)**
- Sentry error tracking enabled
- UptimeRobot monitoring configured
- Email alerts set up
- Log rotation configured
- CloudWatch alarms ready
**Deployment & Rollback (3 items)**
- Deployment script tested
- Rollback procedure documented
- Health check script ready
**Testing (8 items)**
- Unit tests passing
- Integration tests passing
- Load testing completed
- Security testing completed
- Backup restore tested
- Failover tested
- Performance benchmarked
- Final smoke tests passed
## ?? Before Deploying
**1 Hour Before Deployment:**
- [ ] Review entire CHECKLIST_COMPLETE.md
- [ ] Check all items are verified
- [ ] Run final tests locally
**30 Minutes Before:**
- [ ] Verify EC2 is ready
- [ ] Check database backups
- [ ] Confirm all team aware
**Right Before Deployment:**
- [ ] Review QUICK_REFERENCE.md pre-deployment section
- [ ] Verify no active development
- [ ] Have rollback plan ready
- [ ] Setup monitoring alerts
**After Deployment:**
- [ ] Run health checks (10 items)
- [ ] Monitor logs
- [ ] Check error tracking (Sentry)
- [ ] Verify DNS working
- [ ] Test key features
## ?? Status
- ? All 41 checklist items prepared
- ? Checklists tested and verified
- ? Health check procedures ready
- ? Rollback procedures documented
## ??? Next Steps
1. **Before deploying:** Complete this entire checklist
2. **During deployment:** Use QUICK_REFERENCE.md
3. **After deployment:** Run health checks from 01-QUICK-START/QUICK_REFERENCE.md
?? Next: Review CHECKLIST_COMPLETE.md thoroughly
