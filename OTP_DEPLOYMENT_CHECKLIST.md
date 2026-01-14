# OTP System Deployment Checklist

## Pre-Deployment

### 1. SMSCountry Account Setup
- [ ] Sign up at https://www.smscountry.com
- [ ] Complete account verification
- [ ] Get AuthKey from dashboard
- [ ] Get AuthToken from dashboard
- [ ] Note down credentials securely

### 2. DLT Registration (India)
- [ ] Register on DLT portal: https://www.dltconnect.com
- [ ] Register sender ID: `SCNTLK`
- [ ] Submit template for approval:
  ```
  Your OTP for Scan2Talk website registration is {OTP}. 
  Do not share it with anyone. - Scan2Talk
  ```
- [ ] Get DLT Template ID: `1707176830112398745`
- [ ] Wait for approval (usually 24-48 hours)
- [ ] Verify template is active

### 3. Local Testing
- [ ] Run test suite: `python test_otp_system.py`
- [ ] Verify 8/9 tests pass
- [ ] Test activation flow locally
- [ ] Check console OTP display
- [ ] Verify all 3 steps work
- [ ] Test resend functionality
- [ ] Test error scenarios

## Configuration

### 4. Environment Variables
- [ ] Open `.env` file
- [ ] Add SMSCountry credentials:
  ```bash
  SMSCOUNTRY_AUTH_KEY=your_real_auth_key_here
  SMSCOUNTRY_AUTH_TOKEN=your_real_auth_token_here
  ```
- [ ] Verify credentials are correct
- [ ] Do NOT commit `.env` to git
- [ ] Update `.env.example` with placeholder values

### 5. Production Settings
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure Redis for cache (recommended):
  ```python
  CACHES = {
      'default': {
          'BACKEND': 'django.core.cache.backends.redis.RedisCache',
          'LOCATION': 'redis://127.0.0.1:6379/1',
      }
  }
  ```
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Configure logging:
  ```python
  LOGGING = {
      'version': 1,
      'handlers': {
          'file': {
              'class': 'logging.FileHandler',
              'filename': 'logs/otp.log',
          },
      },
      'loggers': {
          'apps.communications.otp_service': {
              'handlers': ['file'],
              'level': 'INFO',
          },
      },
  }
  ```

## Testing with Real SMS

### 6. Test SMS Sending
- [ ] Use test phone number (your own)
- [ ] Start server: `python manage.py runserver`
- [ ] Navigate to activation page
- [ ] Enter test phone number
- [ ] Verify SMS received
- [ ] Check SMS content matches template
- [ ] Verify sender ID is `SCNTLK`
- [ ] Test OTP verification
- [ ] Complete full activation flow

### 7. Test Error Scenarios
- [ ] Test with invalid phone number
- [ ] Test with wrong OTP (3 times)
- [ ] Test OTP expiry (wait 5+ minutes)
- [ ] Test resend functionality
- [ ] Test session expiry
- [ ] Verify error messages are clear

## Security Verification

### 8. Security Checks
- [ ] Verify OTP is hashed before storage
- [ ] Check no plain-text OTP in logs
- [ ] Verify 5-minute expiry works
- [ ] Confirm 3-attempt limit enforced
- [ ] Test OTP invalidation after success
- [ ] Verify session-based verification
- [ ] Check no SMS API calls from frontend
- [ ] Review DLT compliance

### 9. Code Review
- [ ] Review `apps/communications/otp_service.py`
- [ ] Check error handling is comprehensive
- [ ] Verify logging is appropriate
- [ ] Ensure no sensitive data in logs
- [ ] Check rate limiting (if implemented)
- [ ] Review security best practices

## Deployment

### 10. Server Setup
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Configure web server (nginx/apache)
- [ ] Set up SSL certificate
- [ ] Configure firewall rules

### 11. Redis Setup (Recommended)
- [ ] Install Redis: `sudo apt-get install redis-server`
- [ ] Start Redis: `sudo systemctl start redis`
- [ ] Enable on boot: `sudo systemctl enable redis`
- [ ] Test connection: `redis-cli ping`
- [ ] Configure Redis password (production)
- [ ] Update Django cache settings

### 12. Deploy Application
- [ ] Push code to production server
- [ ] Update `.env` with production values
- [ ] Restart application server
- [ ] Check logs for errors
- [ ] Verify application starts successfully

## Post-Deployment

### 13. Smoke Testing
- [ ] Test activation flow end-to-end
- [ ] Verify SMS received on real phone
- [ ] Check OTP verification works
- [ ] Test resend functionality
- [ ] Verify error handling
- [ ] Check all 3 steps complete successfully

### 14. Monitoring Setup
- [ ] Set up log monitoring
- [ ] Configure alerts for:
  - [ ] Failed OTP sends
  - [ ] High verification failure rate
  - [ ] API errors
  - [ ] Timeout errors
- [ ] Set up metrics dashboard:
  - [ ] OTP send success rate
  - [ ] OTP verification success rate
  - [ ] Average verification time
  - [ ] Failed attempt rate

### 15. Documentation
- [ ] Document production credentials location
- [ ] Create runbook for common issues
- [ ] Document support procedures
- [ ] Update team wiki/docs
- [ ] Share SMSCountry support contacts

## Monitoring & Maintenance

### 16. Daily Checks
- [ ] Check OTP send success rate
- [ ] Review error logs
- [ ] Monitor API response times
- [ ] Check for unusual patterns
- [ ] Verify SMS delivery rate

### 17. Weekly Reviews
- [ ] Analyze OTP verification metrics
- [ ] Review failed attempts
- [ ] Check for abuse patterns
- [ ] Update documentation if needed
- [ ] Review and optimize if needed

### 18. Monthly Tasks
- [ ] Review SMSCountry usage/costs
- [ ] Check DLT compliance status
- [ ] Update dependencies if needed
- [ ] Review security measures
- [ ] Optimize based on metrics

## Rollback Plan

### 19. Rollback Preparation
- [ ] Document current version
- [ ] Keep backup of previous code
- [ ] Document rollback steps:
  1. Stop application server
  2. Restore previous code version
  3. Restore previous `.env` settings
  4. Restart application server
  4. Verify functionality
- [ ] Test rollback procedure

## Support

### 20. Support Contacts
- [ ] SMSCountry Support: support@smscountry.com
- [ ] SMSCountry Phone: [Add phone number]
- [ ] DLT Support: [Add contact]
- [ ] Internal team contacts documented
- [ ] Escalation procedures defined

## Common Issues & Solutions

### Issue: "SMS service not configured"
**Solution:**
1. Check `.env` file has credentials
2. Verify credentials are correct
3. Restart application server
4. Check logs for details

### Issue: "Failed to send OTP"
**Solution:**
1. Check SMSCountry account balance
2. Verify DLT template is approved
3. Check API endpoint accessibility
4. Review SMSCountry dashboard for errors
5. Contact SMSCountry support

### Issue: "OTP not received"
**Solution:**
1. Check phone number format (10 digits)
2. Verify SMS was sent (check logs)
3. Check SMSCountry delivery status
4. Try resend functionality
5. Check phone network connectivity

### Issue: "Maximum attempts exceeded"
**Solution:**
1. User should request new OTP
2. Check if rate limiting needed
3. Monitor for abuse patterns

### Issue: "OTP expired"
**Solution:**
1. User should request new OTP
2. Consider increasing expiry time if needed
3. Check if users need more time

## Performance Optimization

### 21. Optimization Checklist
- [ ] Enable Redis caching
- [ ] Configure connection pooling
- [ ] Set up CDN for static files
- [ ] Enable gzip compression
- [ ] Optimize database queries
- [ ] Set up caching headers
- [ ] Monitor response times

### 22. Scaling Considerations
- [ ] Monitor concurrent OTP requests
- [ ] Plan for traffic spikes
- [ ] Consider rate limiting per IP
- [ ] Set up load balancing if needed
- [ ] Plan for horizontal scaling

## Compliance

### 23. Legal & Compliance
- [ ] Verify DLT compliance maintained
- [ ] Check TRAI regulations compliance
- [ ] Review data protection policies
- [ ] Ensure user consent obtained
- [ ] Document compliance measures
- [ ] Regular compliance audits

### 24. Privacy
- [ ] No phone numbers stored in logs
- [ ] OTP hashed before storage
- [ ] Session data cleared after use
- [ ] Comply with data retention policies
- [ ] User data encrypted at rest

## Final Verification

### 25. Go-Live Checklist
- [ ] All tests passing
- [ ] Real SMS sending works
- [ ] Error handling verified
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Team trained
- [ ] Support procedures ready
- [ ] Rollback plan tested
- [ ] Stakeholders informed

### 26. Post-Launch
- [ ] Monitor for first 24 hours
- [ ] Collect user feedback
- [ ] Address any issues immediately
- [ ] Document lessons learned
- [ ] Plan improvements

---

## Sign-Off

**Deployed By:** ___________________  
**Date:** ___________________  
**Version:** 1.0.0  
**Status:** ☐ Ready for Production  

**Reviewed By:** ___________________  
**Date:** ___________________  

**Approved By:** ___________________  
**Date:** ___________________  

---

## Quick Reference

### Test Command
```bash
python test_otp_system.py
```

### Start Server
```bash
python manage.py runserver
```

### Check Logs
```bash
tail -f logs/otp.log
```

### Redis Status
```bash
redis-cli ping
```

### SMSCountry Dashboard
https://www.smscountry.com/dashboard

### DLT Portal
https://www.dltconnect.com

---

**Deployment Checklist Complete** ✅

Print this checklist and check off items as you complete them during deployment.
