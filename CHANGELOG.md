# Changelog

All notable changes to the Tenzai Sushi Chatbot project will be documented in this file.

## [1.2.0] - 2025-08-20

### 🎉 Major Features Added
- **Multi-Platform Customer Management**: Unified customer profiles across LINE/FB/IG/Web
- **Order Confirmation System**: Automatic LINE push notifications with Flex Message UI
- **Real-Time Order Tracking**: Live status page with auto-refresh every 30 seconds
- **Deep Linking Integration**: Seamless flow from chatbot to web app with pre-filled data
- **Platform ID System**: Smart customer identification (`LINE_{user_id}`, `FB_{user_id}`, `WEB_{phone}`)

### ✨ Enhancements
- Enhanced UX flow with 3-step ordering process
- Smart intent classification for FAQ vs AI responses
- Phone-based customer merging across platforms
- Order status timeline with visual progress indicators
- Automatic redirect to order tracking after successful order

### 🔧 Technical Improvements
- Migration from n8n to Python FastAPI (500MB → 30MB memory usage)
- Comprehensive error handling and retry logic
- Webhook signature validation for all platforms
- Database query optimization
- CORS configuration for ngrok domains

### 📱 API Changes
- `POST /api/orders/create` - Enhanced with platform detection
- `GET /api/orders/{order_number}` - New order status endpoint
- Improved customer creation logic with platform awareness
- Added schema inspection endpoints for debugging

### 🐛 Bug Fixes
- Fixed customer ID null errors in order creation
- Resolved platform ID conflicts between web and chat orders
- Fixed menu ID validation for UUID format
- Corrected CORS issues with ngrok tunneling

### 📚 Documentation
- Complete README.md overhaul
- Updated CLAUDE.md architecture documentation
- New .env.example template
- Enhanced setup instructions

## [1.1.0] - 2025-08-19

### 🚀 Initial Working System
- Basic Python FastAPI chatbot API
- LINE webhook integration
- Web ordering interface
- Supabase database integration
- ngrok tunnel setup
- Basic order creation functionality

### Features
- LINE message handling with signature verification
- Simple FAQ responses
- Web-based food ordering
- Database order storage
- Customer management basics

## [1.0.0] - 2025-08-18

### 🏗️ Project Foundation
- Initial project setup
- Database schema design
- Basic infrastructure configuration
- Development environment setup

---

## Version History Summary

- **v1.2.0**: Full-featured multi-platform chatbot with order tracking
- **v1.1.0**: Basic working chatbot and ordering system  
- **v1.0.0**: Project foundation and setup

## Planned Features

### Next Release (v1.3.0)
- Staff notification system
- Facebook/Instagram webhook support
- Admin dashboard for order management
- Basic analytics and reporting

### Future Releases
- Payment integration (QR Code/PromptPay)
- Advanced analytics
- Load testing and optimization
- Multi-restaurant support

---

*Generated with [Claude Code](https://claude.ai/code) - AI-powered development assistant*