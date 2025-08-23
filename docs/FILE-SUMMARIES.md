# File Summaries - Large Files Context Optimization

> **Purpose:** เก็บ summary ของไฟล์ขนาดใหญ่เพื่อป้องกัน Error 413 Context Window

## 📄 webappadmin/customer_webapp.html (1,235 lines)
**Function:** Customer ordering interface  
**Size:** 1,235 lines (ใหญ่เกิน context limit)

### Key Components:
1. **HTML Structure (1-579):**
   - Order form with customer details
   - Menu display with categories  
   - Shopping cart interface
   - Payment options (PromptPay QR)
   - Order status tracking

2. **JavaScript Section (580-1234):**
   - Supabase database connection
   - Menu/category loading
   - Cart management functions
   - Order creation and checkout
   - Real-time order status updates
   - Platform integration (LINE/FB/IG)

### Core Functions:
- `getPlatformInfo()` - Extract URL parameters
- `connectDatabase()` - Supabase connection
- `loadCategories()` - Load menu categories  
- `loadMenus()` - Load menu items
- `addToCart()` - Add items to cart
- `updateCart()` - Update cart display
- `submitOrder()` - Create order via API
- `generateQR()` - PromptPay QR generation
- `trackOrder()` - Real-time order tracking

### When to read:
- Use Grep to find specific functions
- Read sections 1-579 for HTML structure
- For JS functions, search by function name instead of reading all

## 📄 webappadmin/admin/staff-orders.html (558 lines)
**Function:** Staff order management dashboard  
**Size:** 558 lines (manageable but can be optimized)

### Key Components:
- Order list display
- Status management
- Real-time updates
- Customer details
- Order actions (accept/complete)

### Recently Fixed:
- CORS error when opened via file:// protocol
- API endpoint detection logic
- Error messaging improvements

## 🚀 Context Optimization Rules:

### ✅ DO:
- Use Grep to search for specific functions
- Read small sections with offset/limit
- Use FILE-SUMMARIES.md for overview
- Split large files into modules

### 🚫 DON'T:
- Read entire customer_webapp.html (1,235 lines)
- Load multiple screenshots at once
- Include unnecessary git history
- Read archived files

### 📏 Size Guidelines:
- HTML files: Max read 300 lines at once
- JS extraction: Files > 800 lines
- Images: Use .gitignore to block
- Archives: Keep separate from context

---
*Updated: 23 Aug 2025 - Context optimization for Claude Code*