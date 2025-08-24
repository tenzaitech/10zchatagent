// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Complete Order Flow - Find & Fix Issues', () => {
  
  test('investigate order creation step by step', async ({ page }) => {
    console.log('🔍 Starting complete order flow investigation...');
    
    // Enable comprehensive logging
    page.on('console', msg => console.log(`🖥️ Console: ${msg.text()}`));
    page.on('request', req => console.log(`📤 ${req.method()} ${req.url()}`));
    page.on('response', res => console.log(`📥 ${res.status()} ${res.url()}`));
    page.on('requestfailed', req => console.log(`❌ Failed: ${req.url()}`));
    
    await page.goto('/customer_webapp.html');
    await page.waitForTimeout(2000);
    
    // Take initial screenshot
    await page.screenshot({ path: 'tests/screenshots/01-initial-load.png', fullPage: true });
    console.log('📸 Screenshot: 01-initial-load.png');
    
    // Check if we need to connect to database first
    const configPanel = page.locator('#configPanel');
    const mainContent = page.locator('#mainContent');
    
    const isConfigVisible = await configPanel.isVisible();
    const isMainVisible = await mainContent.isVisible();
    
    console.log(`📊 Config panel visible: ${isConfigVisible}`);
    console.log(`📊 Main content visible: ${isMainVisible}`);
    
    if (isConfigVisible || !isMainVisible) {
      console.log('🔧 Need to configure database connection...');
      
      // Click config toggle if needed
      if (!isConfigVisible) {
        await page.locator('.config-toggle').click();
        await page.waitForTimeout(500);
      }
      
      // Fill database config from privatekey.md
      await page.fill('#supabaseUrl', 'https://qlhpmrehrmprptldtchb.supabase.co');
      await page.fill('#serviceKey', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMzNzA0MiwiZXhwIjoyMDY5OTEzMDQyfQ.foCnBLUA6SOXHPBKuBJaKu2A1CPUeetMTjXWSbBkObU');
      
      // Connect to database
      await page.locator('button:has-text("เชื่อมต่อ")').click();
      await page.waitForTimeout(3000);
      
      await page.screenshot({ path: 'tests/screenshots/02-after-db-connect.png', fullPage: true });
      console.log('📸 Screenshot: 02-after-db-connect.png');
    }
    
    // Wait for menu to load
    await page.waitForSelector('.menu-card', { timeout: 10000 });
    console.log('✅ Menu loaded successfully');
    
    // Select first menu item
    const firstMenuItem = page.locator('.menu-card').first();
    const menuName = await firstMenuItem.locator('.menu-name').textContent();
    console.log(`🍣 Selected menu: ${menuName}`);
    
    // Add quantity
    await firstMenuItem.locator('.qty-btn:has-text("+")').click();
    await page.waitForTimeout(500);
    
    // Add to cart
    await firstMenuItem.locator('.add-to-cart').click();
    await page.waitForTimeout(1000);
    
    await page.screenshot({ path: 'tests/screenshots/03-item-added-to-cart.png', fullPage: true });
    console.log('📸 Screenshot: 03-item-added-to-cart.png');
    
    // Open cart
    await page.locator('.cart-toggle').click();
    await page.waitForTimeout(1000);
    
    await page.screenshot({ path: 'tests/screenshots/04-cart-opened.png', fullPage: true });
    console.log('📸 Screenshot: 04-cart-opened.png');
    
    // Click checkout button
    await page.locator('.checkout-btn').click();
    await page.waitForTimeout(2000);
    
    await page.screenshot({ path: 'tests/screenshots/05-checkout-form.png', fullPage: true });
    console.log('📸 Screenshot: 05-checkout-form.png');
    
    // Fill customer information
    const customerName = 'Playwright Test User';
    const customerPhone = '0812345678';
    
    await page.fill('#customerName', customerName);
    await page.fill('#customerPhone', customerPhone);
    await page.selectOption('#orderType', 'pickup');
    
    await page.screenshot({ path: 'tests/screenshots/06-form-filled.png', fullPage: true });
    console.log('📸 Screenshot: 06-form-filled.png');
    
    // Submit order and capture all network activity
    console.log('🚀 Submitting order...');
    
    // Listen for the order creation request specifically
    const orderRequestPromise = page.waitForRequest(request => 
      request.url().includes('/api/orders/create') && request.method() === 'POST'
    );
    
    const orderResponsePromise = page.waitForResponse(response => 
      response.url().includes('/api/orders/create')
    );
    
    await page.locator('#submitOrder').click();
    
    try {
      // Wait for request/response
      const orderRequest = await orderRequestPromise;
      const orderResponse = await orderResponsePromise;
      
      console.log(`📤 Order request body: ${await orderRequest.postData()}`);
      console.log(`📥 Order response status: ${orderResponse.status()}`);
      console.log(`📥 Order response body: ${await orderResponse.text()}`);
      
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'tests/screenshots/07-after-order-submit.png', fullPage: true });
      console.log('📸 Screenshot: 07-after-order-submit.png');
      
    } catch (error) {
      console.log(`❌ Error during order submission: ${error.message}`);
      await page.screenshot({ path: 'tests/screenshots/07-order-error.png', fullPage: true });
    }
    
    console.log('🔍 Order flow investigation completed');
  });
  
  test('test order API directly to identify issues', async ({ page }) => {
    console.log('🔧 Testing order API directly...');
    
    const orderData = {
      customer_name: "API Test User",
      customer_phone: "0812345678", 
      order_type: "pickup",
      total_amount: 119,
      items: [
        {
          id: "test-id",
          name: "Test Sushi",
          price: 119,
          quantity: 1
        }
      ]
    };
    
    console.log(`📤 Sending order data: ${JSON.stringify(orderData, null, 2)}`);
    
    try {
      const response = await page.request.post('/api/orders/create', {
        data: orderData,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const responseText = await response.text();
      console.log(`📥 API Response Status: ${response.status()}`);
      console.log(`📥 API Response Body: ${responseText}`);
      
      if (!response.ok()) {
        console.log('❌ API Error detected - this is the issue to fix!');
      }
      
    } catch (error) {
      console.log(`❌ API Request Error: ${error.message}`);
    }
  });
});