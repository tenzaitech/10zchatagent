// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Admin Dashboard Debug Test', () => {
  
  test('debug admin dashboard port and API issues', async ({ page }) => {
    console.log('🔍 Debugging Admin Dashboard...');
    
    // Monitor network requests
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        console.log(`📤 API Request: ${request.method()} ${request.url()}`);
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        console.log(`📥 API Response: ${response.status()} ${response.url()}`);
      }
    });
    
    page.on('console', msg => {
      console.log(`🖥️ [Browser Console]: ${msg.text()}`);
    });
    
    // Test different port configurations
    const testUrls = [
      'http://localhost:8000/admin/staff-orders.html',  // Expected port
      'http://localhost:8002/admin/staff-orders.html',  // Actual service port
      'http://localhost:8080/admin/staff-orders.html'   // Alternative port
    ];
    
    for (const testUrl of testUrls) {
      console.log(`\n🔗 Testing URL: ${testUrl}`);
      
      try {
        await page.goto(testUrl, { waitUntil: 'networkidle', timeout: 10000 });
        
        // Take screenshot for visual debugging
        const urlSlug = testUrl.replace(/[^a-z0-9]/gi, '_');
        await page.screenshot({ 
          path: `tests/screenshots/admin-${urlSlug}.png`, 
          fullPage: true 
        });
        
        console.log(`✅ Successfully loaded: ${testUrl}`);
        console.log(`📸 Screenshot saved: admin-${urlSlug}.png`);
        
        // Check page title
        const title = await page.title();
        console.log(`📋 Page title: "${title}"`);
        
        // Check for error messages
        const errorElements = page.locator('.error');
        const errorCount = await errorElements.count();
        if (errorCount > 0) {
          const errorText = await errorElements.first().textContent();
          console.log(`❌ Error found: "${errorText}"`);
        } else {
          console.log(`✅ No error messages found`);
        }
        
        // Wait a bit for API calls
        await page.waitForTimeout(5000);
        
        // Check stats display
        const totalOrders = await page.locator('#total-orders').textContent();
        const pendingOrders = await page.locator('#pending-orders').textContent();
        
        console.log(`📊 Stats - Total: ${totalOrders}, Pending: ${pendingOrders}`);
        
        // Check orders container
        const ordersContainer = page.locator('#orders-container');
        const containerText = await ordersContainer.textContent();
        
        if (containerText.includes('กำลังโหลด')) {
          console.log(`⏳ Still loading orders...`);
        } else if (containerText.includes('ยังไม่มีออเดอร์')) {
          console.log(`📝 No orders found (empty state)`);
        } else if (containerText.includes('ข้อผิดพลาด') || containerText.includes('Error')) {
          console.log(`❌ Error loading orders`);
        } else {
          console.log(`✅ Orders appear to be loaded`);
        }
        
        return; // Exit the loop on successful load
        
      } catch (error) {
        console.log(`❌ Failed to load ${testUrl}: ${error.message}`);
        continue; // Try next URL
      }
    }
    
    throw new Error('❌ All admin dashboard URLs failed to load');
  });
  
  test('test admin API endpoints directly', async ({ page, request }) => {
    console.log('🔍 Testing Admin API endpoints directly...');
    
    // Test different API ports
    const apiPorts = [8000, 8002, 8080];
    
    for (const port of apiPorts) {
      const apiUrl = `http://localhost:${port}/api/orders/status/today`;
      console.log(`\n📡 Testing API: ${apiUrl}`);
      
      try {
        const response = await request.get(apiUrl, {
          timeout: 5000
        });
        
        console.log(`📥 Response Status: ${response.status()}`);
        console.log(`📥 Response Headers:`, response.headers());
        
        if (response.ok()) {
          const data = await response.json();
          console.log(`✅ API Success on port ${port}`);
          console.log(`📊 Orders returned: ${data.orders ? data.orders.length : 'undefined'}`);
          
          if (data.debug_info) {
            console.log(`🔍 Debug info:`, data.debug_info);
          }
          
          // Test status update endpoint
          if (data.orders && data.orders.length > 0) {
            const testOrder = data.orders[0];
            const updateUrl = `http://localhost:${port}/api/orders/${testOrder.order_number}/status`;
            
            console.log(`🔄 Testing status update: ${updateUrl}`);
            
            try {
              const updateResponse = await request.patch(updateUrl, {
                data: { status: 'confirmed' },
                timeout: 5000
              });
              
              console.log(`📝 Status update response: ${updateResponse.status()}`);
              
              if (updateResponse.ok()) {
                console.log(`✅ Status update works on port ${port}`);
              }
            } catch (updateError) {
              console.log(`❌ Status update failed: ${updateError.message}`);
            }
          }
          
          return; // Exit on successful API test
          
        } else {
          console.log(`❌ API Error ${response.status()}: ${await response.text()}`);
        }
        
      } catch (error) {
        console.log(`❌ API request failed on port ${port}: ${error.message}`);
      }
    }
    
    throw new Error('❌ All API endpoints failed');
  });
  
  test('create test order and verify admin can see it', async ({ page, request }) => {
    console.log('🧪 Creating test order and verifying admin dashboard...');
    
    // First, determine which port has working API
    let workingPort = null;
    const ports = [8002, 8000, 8080];
    
    for (const port of ports) {
      try {
        const response = await request.get(`http://localhost:${port}/health`);
        if (response.ok()) {
          workingPort = port;
          console.log(`✅ Found working API on port ${port}`);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!workingPort) {
      throw new Error('❌ No working API server found');
    }
    
    // Create a test order
    const orderData = {
      customer_name: "Admin Test Order",
      customer_phone: "0899999999",
      total_amount: 159,
      order_type: "pickup",
      payment_method: "cash",
      notes: "Test order for admin dashboard",
      items: [
        {
          id: "e9874f12-cfef-4895-a2f7-529887fd62e1",
          name: "EBI TENPURA",
          quantity: 1,
          price: 159,
          total: 159
        }
      ],
      platform: "WEB",
      platform_user_id: "admin_test_user"
    };
    
    console.log('📤 Creating test order...');
    const createResponse = await request.post(`http://localhost:${workingPort}/api/orders/create`, {
      data: orderData
    });
    
    if (!createResponse.ok()) {
      throw new Error(`❌ Failed to create test order: ${createResponse.status()}`);
    }
    
    const orderResult = await createResponse.json();
    console.log(`✅ Test order created: ${orderResult.order_number}`);
    
    // Now test admin dashboard
    await page.goto(`http://localhost:${workingPort}/admin/staff-orders.html`);
    await page.waitForTimeout(3000);
    
    // Take screenshot
    await page.screenshot({ 
      path: 'tests/screenshots/admin-with-test-order.png', 
      fullPage: true 
    });
    
    // Check if order appears
    const orderNumber = orderResult.order_number;
    const orderElement = page.locator(`text="${orderNumber}"`);
    
    if (await orderElement.isVisible()) {
      console.log(`✅ Test order ${orderNumber} is visible in admin dashboard`);
    } else {
      console.log(`❌ Test order ${orderNumber} is NOT visible in admin dashboard`);
      
      // Debug: check what's in the orders container
      const containerText = await page.locator('#orders-container').textContent();
      console.log(`🔍 Orders container content:`, containerText.slice(0, 200));
    }
    
    // Test refresh button
    console.log('🔄 Testing refresh functionality...');
    await page.click('.refresh-btn');
    await page.waitForTimeout(2000);
    
    // Take another screenshot after refresh
    await page.screenshot({ 
      path: 'tests/screenshots/admin-after-refresh.png', 
      fullPage: true 
    });
    
    console.log('🎉 Admin dashboard test completed');
  });
});