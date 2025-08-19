# Next Actions & Implementation Guide

## Immediate Priority (Critical Path)

### 🔥 Fix WF-A Workflow Error
**Problem:** `Cannot read properties of undefined (reading 'status')` in "Get Menu Prices" node
**Action Required:**
1. Open n8n workflow editor
2. Check HTTP Request node configuration:
   - URL: Should be `https://qlhpmrehrmprptldtchb.supabase.co/rest/v1/menus`
   - Headers: `apikey: [ANON_KEY]`, `Content-Type: application/json`
   - Method: GET
3. Test response structure and fix JavaScript code expecting `.status` property

### 🔧 Import & Configure Workflows  
**Current Status:** JSON files exist but may not be imported to n8n
**Action Required:**
1. Access n8n interface (likely at `localhost:5678`)
2. Import workflow files from `/workflows/` directory:
   - `WF-A-inbound-chat-v2.json` → Rename to "Tenzai Chat (WF-A)"
   - `WF-B-order-processing-FINAL-FIXED.json` → Rename to "Tenzai Orders (WF-B)"  
   - `WF-C-utils.json` → Rename to "Tenzai Utils (WF-C)"
3. Configure environment variables/credentials in each workflow

### 🧪 End-to-End Testing
**Test Scenarios:**
1. **Basic Chat:** Send test message → Verify FAQ response
2. **Order Flow:** Submit web order → Verify DB record + staff notification
3. **Error Handling:** Submit invalid data → Verify proper error responses
4. **Security:** Test webhook without signature → Verify 401 rejection

## Week 1 Implementation Plan

### Day 1-2: Fix & Import Workflows
- [x] ~~Clean up project files~~
- [x] ~~Create project documentation~~  
- [ ] Fix WF-A HTTP request configuration
- [ ] Import all workflow JSON files to n8n
- [ ] Verify database connections and credentials

### Day 3-4: Security & Validation  
- [ ] Implement webhook signature validation (LINE, FB, IG)
- [ ] Test rate limiting and error handling
- [ ] Verify RLS policies working correctly
- [ ] Configure proper CORS headers for web app

### Day 5-7: Integration Testing
- [ ] Test complete chat flow: message → FAQ response  
- [ ] Test complete order flow: web → n8n → DB → notification
- [ ] Test error scenarios and recovery
- [ ] Load testing with multiple concurrent requests

## Technical Debt to Address

### Security Hardening
- [ ] Rotate API keys if they've been exposed
- [ ] Implement request logging for audit trail
- [ ] Set up monitoring/alerting for failed requests
- [ ] Review and tighten Supabase RLS policies

### Performance Optimization  
- [ ] Optimize database queries (add indexes)
- [ ] Implement response caching where appropriate
- [ ] Monitor Supabase usage vs Free tier limits
- [ ] Set up automated database cleanup for old data

### Monitoring & Maintenance
- [ ] Health check endpoints for all services
- [ ] Log aggregation and analysis setup
- [ ] Backup strategy for n8n workflows and database
- [ ] Documentation for common troubleshooting scenarios

## Success Criteria
**MVP Ready When:**
✅ Customer can ask FAQ questions and get instant responses
✅ Customer can click "สั่งอาหาร" and access web ordering interface  
✅ Web orders successfully create database records
✅ Staff receives LINE notifications for new orders
✅ All webhook signatures are properly validated
✅ System handles basic error scenarios gracefully

## Risk Mitigation
**High Risk Items:**
- Supabase Free tier limits → Monitor usage daily  
- n8n workflow stability → Implement health checks + restart logic
- Webhook spam/abuse → Rate limiting + signature validation
- Database connection failures → Retry logic + fallback responses

**Rollback Plan:**
- Keep current manual order-taking process as backup
- Document manual override procedures for staff
- Maintain contact information for critical vendor support