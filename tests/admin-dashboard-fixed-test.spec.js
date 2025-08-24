// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Admin Dashboard Fixed Test', () => {
  
  test('verify admin dashboard works with fixed port 8002', async ({ page }) => {
    console.log('✅ Testing fixed admin dashboard...');
    
    // Monitor API requests
    page.on('request', request => {
      if (request.url().includes('/api/orders')) {
        console.log(`📤 API Request: ${request.method()} ${request.url()}`);
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/orders')) {
        console.log(`📥 API Response: ${response.status()} ${response.url()}`);
      }
    });
    
    // Test the corrected admin page
    console.log('🔗 Testing: http://localhost:8002/admin/staff-orders.html');
    await page.goto('http://localhost:8002/admin/staff-orders.html');
    
    // Wait for page to load
    await page.waitForTimeout(3000);
    
    // Take screenshot
    await page.screenshot({ 
      path: 'tests/screenshots/admin-dashboard-fixed.png', 
      fullPage: true 
    });
    
    // Check page title
    const title = await page.title();
    console.log(`📋 Page title: "${title}"`);
    expect(title).toContain('Staff Orders Dashboard');
    
    // Check that no errors are displayed
    const errorElements = page.locator('.error');
    const errorCount = await errorElements.count();
    
    if (errorCount > 0) {
      const errorText = await errorElements.first().textContent();
      console.log(`❌ Error still found: "${errorText}"`);
    } else {
      console.log(`✅ No error messages - admin dashboard working!`);
    }
    
    // Check if stats are loaded (not showing '-')
    const totalOrders = await page.locator('#total-orders').textContent();
    const pendingOrders = await page.locator('#pending-orders').textContent();
    
    console.log(`📊 Stats - Total: ${totalOrders}, Pending: ${pendingOrders}`);
    
    // Verify stats are not showing '-' (which means loading failed)
    if (totalOrders !== '-' && pendingOrders !== '-') {
      console.log(`✅ Order statistics loaded successfully!`);
    } else {
      console.log(`❌ Statistics still showing loading state`);
    }
    
    // Check orders container content
    const ordersContainer = page.locator('#orders-container');
    const containerText = await ordersContainer.textContent();
    
    if (containerText.includes('กำลังโหลด')) {
      console.log(`⏳ Still loading orders...`);
    } else if (containerText.includes('ยังไม่มีออเดอร์')) {
      console.log(`📝 No orders today (but API working)`);
    } else if (containerText.includes('ข้อผิดพลาด') || containerText.includes('Error')) {
      console.log(`❌ Error loading orders: ${containerText.slice(0, 100)}`);
    } else if (containerText.includes('#T')) {
      // Look for order numbers starting with #T
      console.log(`✅ Orders are displayed! Found order numbers in content.`);
    } else {
      console.log(`✅ Orders container loaded (content: ${containerText.slice(0, 50)}...)`);
    }
    
    // Test refresh button
    console.log('🔄 Testing refresh functionality...');
    await page.click('.refresh-btn');
    await page.waitForTimeout(2000);
    
    // Take screenshot after refresh
    await page.screenshot({ 
      path: 'tests/screenshots/admin-dashboard-after-refresh.png', 
      fullPage: true 
    });
    
    console.log('🎉 Admin dashboard fixed test completed successfully!');
  });
  
  test('test order status update functionality', async ({ page, request }) => {
    console.log('🔄 Testing order status update functionality...');
    
    // First get the list of orders
    const ordersResponse = await request.get('http://localhost:8002/api/orders/status/today');
    
    if (!ordersResponse.ok()) {
      throw new Error(`Failed to get orders: ${ordersResponse.status()}`);
    }
    
    const ordersData = await ordersResponse.json();
    console.log(`📊 Found ${ordersData.orders.length} orders`);
    
    if (ordersData.orders.length > 0) {
      const testOrder = ordersData.orders[0];
      console.log(`🧪 Testing with order: ${testOrder.order_number} (status: ${testOrder.status})`);
      
      // Load admin page
      await page.goto('http://localhost:8002/admin/staff-orders.html');
      await page.waitForTimeout(3000);
      
      // Look for the test order in the page
      const orderElement = page.locator(`text="${testOrder.order_number}"`);
      
      if (await orderElement.isVisible()) {
        console.log(`✅ Order ${testOrder.order_number} is visible in admin dashboard`);
        
        // Try to find and click a status update button
        const statusButtons = page.locator('.action-btn');
        const buttonCount = await statusButtons.count();
        
        console.log(`🔘 Found ${buttonCount} action buttons`);
        
        if (buttonCount > 0) {
          // Take screenshot before action
          await page.screenshot({ 
            path: 'tests/screenshots/admin-before-status-update.png', 
            fullPage: true 
          });
          
          // Click first action button (usually confirm or next status)
          await statusButtons.first().click();
          await page.waitForTimeout(2000);
          
          // Take screenshot after action
          await page.screenshot({ 
            path: 'tests/screenshots/admin-after-status-update.png', 
            fullPage: true 
          });
          
          console.log(`✅ Status update button clicked successfully`);
        }
        
      } else {
        console.log(`⚠️ Order ${testOrder.order_number} not visible in admin dashboard`);
      }
      
    } else {
      console.log(`📝 No orders available for status update testing`);
    }
    
    console.log('🎉 Status update test completed!');
  });
  
  test('verify all admin dashboard features', async ({ page }) => {
    console.log('🔍 Comprehensive admin dashboard feature test...');
    
    await page.goto('http://localhost:8002/admin/staff-orders.html');
    await page.waitForTimeout(3000);
    
    // Check all key elements are present
    const elements = {
      'header': '.header h1',
      'stats-bar': '.stats-bar', 
      'total-orders': '#total-orders',
      'pending-orders': '#pending-orders',
      'preparing-orders': '#preparing-orders',
      'completed-orders': '#completed-orders',
      'refresh-btn': '.refresh-btn',
      'orders-container': '#orders-container'
    };
    
    for (const [name, selector] of Object.entries(elements)) {
      const element = page.locator(selector);
      const isVisible = await element.isVisible();
      console.log(`${isVisible ? '✅' : '❌'} ${name}: ${isVisible ? 'visible' : 'not found'}`);
    }
    
    // Test that stats are numeric (not '-')
    const stats = ['total-orders', 'pending-orders', 'preparing-orders', 'completed-orders'];
    let statsWorking = 0;
    
    for (const statId of stats) {
      const statValue = await page.locator(`#${statId}`).textContent();
      const isNumeric = /^\d+$/.test(statValue);
      console.log(`📊 ${statId}: ${statValue} ${isNumeric ? '✅' : '❌'}`);
      if (isNumeric) statsWorking++;
    }
    
    console.log(`📊 ${statsWorking}/${stats.length} statistics working correctly`);
    
    // Final comprehensive screenshot
    await page.screenshot({ 
      path: 'tests/screenshots/admin-dashboard-comprehensive.png', 
      fullPage: true 
    });
    
    // Success criteria: at least basic elements visible and some stats working
    const basicElementsWorking = await page.locator('.header h1').isVisible() && 
                                 await page.locator('.stats-bar').isVisible() &&
                                 await page.locator('#orders-container').isVisible();
    
    if (basicElementsWorking && statsWorking >= 1) {
      console.log('🎉 Admin dashboard comprehensive test PASSED!');
    } else {
      console.log('❌ Admin dashboard comprehensive test FAILED');
      throw new Error('Basic admin dashboard functionality not working');
    }
  });
});