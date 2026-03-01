# ?? 05-AWS
**AWS infrastructure setup guide**
This folder contains AWS-specific deployment and infrastructure setup instructions.
## ?? Files in This Folder
### **README.md** (This file)
Navigation and overview of AWS setup
### **AWS_PRODUCTION_DEPLOYMENT_GUIDE.md** ? MAIN FILE
Complete AWS setup guide covering:
**EC2 Instance Setup**
- Launch EC2 t4g.micro instance
- Configure security groups
- SSH key pair setup
- Elastic IP configuration
- VPC and subnet configuration
**RDS Database (Optional)**
- Alternative: Local PostgreSQL on EC2
- RDS for managed database
- Multi-AZ setup
- Automated backups
**S3 Bucket Setup**
- Create S3 bucket for static files
- Configure bucket permissions
- Enable versioning
- Setup bucket policies
**CloudFront CDN**
- Create CloudFront distribution
- Configure origin (S3 or EC2)
- SSL/TLS certificate
- Cache behavior settings
- Distribution domain
**Route 53 DNS**
- Domain registration
- DNS record creation
- CNAME for CloudFront
- Health checks
**IAM Roles & Permissions**
- EC2 instance role
- S3 access permissions
- CloudFront access
- Least privilege setup
**SSL/TLS Certificates**
- ACM certificate request
- Certificate validation
- CloudFront certificate
- Nginx certificate (Let's Encrypt)
**Monitoring & Logging**
- CloudWatch monitoring
- S3 access logs
- CloudFront logs
- VPC Flow Logs
## ?? AWS Deployment Steps
**Phase 1: Compute (EC2)**
1. Launch EC2 instance
2. Configure security groups
3. Setup SSH access
4. Configure Elastic IP
**Phase 2: Storage (S3)**
1. Create S3 bucket
2. Configure permissions
3. Enable versioning
4. Setup bucket policies
**Phase 3: CDN (CloudFront)**
1. Create distribution
2. Configure origin
3. Setup SSL certificate
4. Configure caching
**Phase 4: DNS (Route 53)**
1. Register domain
2. Create DNS records
3. Configure CNAME to CloudFront
4. Setup health checks
**Phase 5: IAM**
1. Create IAM role for EC2
2. Attach S3 permissions
3. Attach CloudFront permissions
**Phase 6: Monitoring**
1. Enable CloudWatch
2. Setup log groups
3. Configure alarms
4. Setup SNS notifications
## ?? AWS Services Used
| Service | Purpose | Cost |
|---------|---------|------|
| EC2 t4g.micro | Application server | ~-5/month |
| S3 | Static file storage | ~/month |
| CloudFront | CDN | ~-5/month |
| Route 53 | DNS | ~.50/month |
| RDS (optional) | Database | ~-30/month |
| **Total** | **All services** | **~-50/month** |
## ? Status
- ? AWS guide complete (detailed)
- ? All services documented
- ? Cost estimates provided
- ? Security best practices included
## ??? Next Steps
1. Read this README first
2. Review AWS_PRODUCTION_DEPLOYMENT_GUIDE.md
3. Follow AWS setup steps
4. Then go to 03-SECURITY/ for security configuration
?? Next: Read AWS_PRODUCTION_DEPLOYMENT_GUIDE.md for step-by-step AWS setup
