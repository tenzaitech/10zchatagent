# Function Dependencies Analysis

> Generated before file separation for safe refactoring

## 📊 Current Functions (17 total)

### LINE Services (4 functions)
- `send_line_message(reply_token, messages)` - ✅ Independent
- `send_line_push_message(user_id, messages)` - ✅ Independent  
- `send_order_confirmation(...)` - 🔗 Calls: `send_line_push_message`
- `verify_line_signature(body, signature)` - ✅ Independent

### Database Services (3 functions)
- `supabase_request(method, endpoint, data, use_service_key)` - ✅ Independent
- `find_or_create_customer(name, phone, platform, platform_user_id)` - 🔗 Calls: `supabase_request`, `generate_platform_id`
- `generate_platform_id(platform, identifier)` - ✅ Independent

### AI Services (2 functions)  
- `get_ai_response(message, user_id)` - ✅ Independent
- `classify_intent(message_text)` - ✅ Independent

### API Endpoints (8 functions)
- `health_check()` - ✅ Independent
- `inspect_database_schema()` - 🔗 Calls: `supabase_request`
- `get_sample_data()` - 🔗 Calls: `supabase_request`
- `line_webhook(request)` - 🔗 Calls: `verify_line_signature`, `classify_intent`, `get_ai_response`, `send_line_message`
- `create_order(request)` - 🔗 Calls: `supabase_request`, `find_or_create_customer`, `send_order_confirmation`
- `get_order_status(order_number)` - 🔗 Calls: `supabase_request`
- `facebook_webhook(request)` - ✅ Independent (placeholder)
- `instagram_webhook(request)` - ✅ Independent (placeholder)

## 🎯 Dependency Graph

```
API Endpoints:
├── line_webhook → verify_line_signature, classify_intent, get_ai_response, send_line_message
├── create_order → supabase_request, find_or_create_customer, send_order_confirmation
├── get_order_status → supabase_request
├── inspect_database_schema → supabase_request  
└── get_sample_data → supabase_request

Service Functions:
├── find_or_create_customer → supabase_request, generate_platform_id
└── send_order_confirmation → send_line_push_message

Independent Functions:
├── LINE: send_line_message, send_line_push_message, verify_line_signature
├── Database: supabase_request, generate_platform_id
├── AI: get_ai_response, classify_intent
└── Health: health_check, facebook_webhook, instagram_webhook
```

## 📁 Safe Grouping Strategy

### Group 1: Core Services (No Dependencies)
```python
# config.py
- Environment variables
- Constants (FAQ_RESPONSES, FALLBACK_MESSAGE)

# services/database_service.py
- supabase_request()
- generate_platform_id()

# services/line_service.py  
- send_line_message()
- send_line_push_message()
- verify_line_signature()

# services/ai_service.py
- get_ai_response()
- classify_intent()
```

### Group 2: Business Logic (Uses Core Services)
```python
# services/customer_service.py
- find_or_create_customer() → uses database_service

# services/notification_service.py  
- send_order_confirmation() → uses line_service
```

### Group 3: API Routes (Uses All Services)
```python
# routers/admin.py
- health_check()
- inspect_database_schema() → uses database_service
- get_sample_data() → uses database_service

# routers/webhooks.py
- line_webhook() → uses line_service, ai_service
- facebook_webhook()  
- instagram_webhook()

# routers/orders.py
- create_order() → uses database_service, customer_service, notification_service
- get_order_status() → uses database_service
```

## ✅ Safe Migration Order

1. **Phase 1**: Create independent services (config, database_service, line_service, ai_service)
2. **Phase 2**: Create business logic (customer_service, notification_service)  
3. **Phase 3**: Create routers (admin, webhooks, orders)
4. **Phase 4**: Update main.py to use new structure

## 🔒 Critical Dependencies to Watch

- `find_or_create_customer` depends on `supabase_request` and `generate_platform_id`
- `send_order_confirmation` depends on `send_line_push_message`  
- `create_order` depends on multiple services - must import correctly
- All routers depend on services - must handle imports carefully

## 🚨 Import Risk Areas

1. **Circular imports**: Services should not import from routers
2. **Missing dependencies**: Each service must import what it needs
3. **Environment variables**: Must be available to all services via config
4. **FastAPI dependencies**: App instance must be accessible to routers

---

*This analysis ensures safe file separation with minimal risk of breaking dependencies*