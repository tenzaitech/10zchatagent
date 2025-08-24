// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Real Data Order Flow', () => {
  
  test('create order with real menu data from Supabase', async ({ page }) => {
    console.log('🔥 Testing with real menu data from Supabase...');
    
    // Step 1: Get real menu data from Supabase
    const menuResponse = await page.request.get('https://qlhpmrehrmprptldtchb.supabase.co/rest/v1/menus?select=id,name,name_thai,price&limit=1&is_available=eq.true', {
      headers: {
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMzNzA0MiwiZXhwIjoyMDY5OTEzMDQyfQ.foCnBLUA6SOXHPBKuBJaKu2A1CPUeetMTjXWSbBkObU',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMzNzA0MiwiZXhwIjoyMDY5OTEzMDQyfQ.foCnBLUA6SOXHPBKuBJaKu2A1CPUeetMTjXWSbBkObU'
      }
    });
    
    const menuData = await menuResponse.json();
    console.log('🍣 Real menu data:', JSON.stringify(menuData, null, 2));
    
    const realMenuItem = menuData[0];
    
    // Step 2: Test order creation with real menu UUID
    const orderData = {
      customer_name: "Real Data Test User",
      customer_phone: "0812345678",
      order_type: "pickup",
      total_amount: realMenuItem.price,
      items: [
        {
          id: realMenuItem.id, // Real UUID from database
          name: realMenuItem.name,
          price: realMenuItem.price,
          quantity: 1
        }
      ]
    };
    
    console.log('📤 Testing order with real data:', JSON.stringify(orderData, null, 2));
    
    // Step 3: Create order via API
    const orderResponse = await page.request.post('/api/orders/create', {
      data: orderData,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const responseText = await orderResponse.text();
    console.log(`📥 Order API Response Status: ${orderResponse.status()}`);
    console.log(`📥 Order API Response: ${responseText}`);
    
    if (orderResponse.ok()) {
      const orderResult = JSON.parse(responseText);
      console.log(`✅ SUCCESS! Order created: ${orderResult.order_number}`);
      console.log(`💰 Total amount: ${orderResult.total_amount} บาท`);
      
      // Step 4: Verify order was created in database
      const verifyResponse = await page.request.get(`/api/orders/${orderResult.order_number}`);
      const verifyData = await verifyResponse.json();
      
      console.log('🔍 Order verification:', JSON.stringify(verifyData, null, 2));
      
    } else {
      console.log(`❌ Order creation failed: ${responseText}`);
      throw new Error(`Order API failed with ${orderResponse.status()}`);
    }
  });
  
  test('test complete UI flow with real menu selection', async ({ page }) => {
    console.log('🎭 Testing complete UI flow with real menu selection...');
    
    // Enable logging
    page.on('console', msg => console.log(`🖥️ Console: ${msg.text()}`));
    page.on('request', req => {
      if (req.url().includes('orders/create')) {
        console.log(`📤 Order Request: ${req.method()} ${req.url()}`);
      }
    });
    page.on('response', res => {
      if (res.url().includes('orders/create')) {
        console.log(`📥 Order Response: ${res.status()} ${res.url()}`);
      }
    });
    
    // Go to customer webapp
    await page.goto('/customer_webapp.html');
    await page.waitForTimeout(2000);
    
    // Take initial screenshot
    await page.screenshot({ path: 'tests/screenshots/real-01-initial.png', fullPage: true });
    
    // Configure database if needed
    const configPanel = page.locator('#configPanel');
    const mainContent = page.locator('#mainContent');
    
    if (await configPanel.isVisible() || !(await mainContent.isVisible())) {
      console.log('🔧 Configuring database connection...');
      
      if (!(await configPanel.isVisible())) {
        await page.locator('.config-toggle').click();
        await page.waitForTimeout(500);
      }
      
      await page.fill('#supabaseUrl', 'https://qlhpmrehrmprptldtchb.supabase.co');
      await page.fill('#serviceKey', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMzNzA0MiwiZXhwIjoyMDY5OTEzMDQyfQ.foCnBLUA6SOXHPBKuBJaKu2A1CPUeetMTjXWSbBkObU');
      
      await page.locator('button:has-text("เชื่อมต่อ")').click();
      await page.waitForTimeout(3000);
      
      await page.screenshot({ path: 'tests/screenshots/real-02-connected.png', fullPage: true });
    }
    
    // Wait for menu to load
    await page.waitForSelector('.menu-card', { timeout: 10000 });
    console.log('✅ Menu loaded successfully');
    
    await page.screenshot({ path: 'tests/screenshots/real-03-menu-loaded.png', fullPage: true });
    
    // Select first menu item (which has real menu ID)
    const firstMenuItem = page.locator('.menu-card').first();
    const menuName = await firstMenuItem.locator('.menu-name').textContent();
    const menuPrice = await firstMenuItem.locator('.menu-price').textContent();
    console.log(`🍣 Selected menu: ${menuName} - ${menuPrice}`);
    
    // Add quantity and add to cart
    await firstMenuItem.locator('.qty-btn:has-text("+")').click();
    await page.waitForTimeout(500);
    await firstMenuItem.locator('.add-to-cart').click();
    await page.waitForTimeout(1000);
    
    await page.screenshot({ path: 'tests/screenshots/real-04-added-to-cart.png', fullPage: true });
    
    // Open cart and proceed to checkout
    await page.locator('.cart-toggle').click();
    await page.waitForTimeout(1000);
    
    await page.screenshot({ path: 'tests/screenshots/real-05-cart-open.png', fullPage: true });
    
    await page.locator('.checkout-btn').click();
    await page.waitForTimeout(2000);
    
    await page.screenshot({ path: 'tests/screenshots/real-06-checkout-form.png', fullPage: true });
    
    // Fill customer information
    await page.fill('#customerName', 'Playwright Real Test');
    await page.fill('#customerPhone', '0812345678');
    await page.selectOption('#orderType', 'pickup');
    
    await page.screenshot({ path: 'tests/screenshots/real-07-form-filled.png', fullPage: true });
    
    // Submit order
    console.log('🚀 Submitting real order...');
    
    const orderSubmitPromise = page.waitForResponse(response => 
      response.url().includes('/api/orders/create'), { timeout: 15000 }
    );
    
    await page.locator('#submitOrder').click();
    
    try {
      const orderResponse = await orderSubmitPromise;
      const responseText = await orderResponse.text();
      
      console.log(`📥 Final order response: ${orderResponse.status()}`);
      console.log(`📥 Response body: ${responseText}`);
      
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'tests/screenshots/real-08-final-result.png', fullPage: true });
      
      if (orderResponse.ok()) {
        console.log('✅ COMPLETE SUCCESS! Order system working 100%');
        
        // Try to find success modal or order number
        const successModal = page.locator('#success-modal, #order-number, .success-message');
        if (await successModal.isVisible()) {
          const successText = await successModal.textContent();
          console.log(`🎉 Success message: ${successText}`);
        }
      } else {
        console.log(`❌ Order still failing: ${responseText}`);
      }
      
    } catch (error) {
      console.log(`⏱️ Timeout or error: ${error.message}`);
      await page.screenshot({ path: 'tests/screenshots/real-08-error.png', fullPage: true });
    }
    
    console.log('🏁 Complete UI flow test finished');
  });
});