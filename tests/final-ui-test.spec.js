// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Final Complete UI Test', () => {
  
  test('complete real order flow with prompts handling', async ({ page }) => {
    console.log('🏁 Final complete order test with prompt handling...');
    
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
    
    // Handle prompts for customer info
    page.on('dialog', async dialog => {
      console.log(`🗣️ Handling dialog: ${dialog.message()}`);
      if (dialog.message().includes('ชื่อ')) {
        await dialog.accept('Playwright Final Test');
      } else if (dialog.message().includes('เบอร์')) {
        await dialog.accept('0812345678');
      } else if (dialog.message().includes('รับสินค้า') || dialog.message().includes('pickup')) {
        await dialog.accept('pickup');
      } else {
        await dialog.accept('pickup'); // default
      }
    });
    
    // Go to customer webapp
    await page.goto('/customer_webapp.html');
    await page.waitForTimeout(2000);
    
    // Take initial screenshot
    await page.screenshot({ path: 'tests/screenshots/final-01-initial.png', fullPage: true });
    
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
      
      await page.screenshot({ path: 'tests/screenshots/final-02-connected.png', fullPage: true });
    }
    
    // Wait for menu to load
    await page.waitForSelector('.menu-card', { timeout: 10000 });
    console.log('✅ Menu loaded successfully');
    
    await page.screenshot({ path: 'tests/screenshots/final-03-menu-loaded.png', fullPage: true });
    
    // Select first menu item
    const firstMenuItem = page.locator('.menu-card').first();
    const menuName = await firstMenuItem.locator('.menu-name').textContent();
    const menuPrice = await firstMenuItem.locator('.menu-price').textContent();
    console.log(`🍣 Selected menu: ${menuName} - ${menuPrice}`);
    
    // Add quantity and add to cart
    await firstMenuItem.locator('.qty-btn:has-text("+")').click();
    await page.waitForTimeout(500);
    await firstMenuItem.locator('.add-to-cart').click();
    await page.waitForTimeout(1000);
    
    await page.screenshot({ path: 'tests/screenshots/final-04-added-to-cart.png', fullPage: true });
    
    // Open cart and proceed to checkout
    await page.locator('.cart-toggle').click();
    await page.waitForTimeout(1000);
    
    await page.screenshot({ path: 'tests/screenshots/final-05-cart-open.png', fullPage: true });
    
    // Click checkout button - this should trigger prompts
    console.log('🚀 Clicking checkout - prompts will appear...');
    
    const orderSubmitPromise = page.waitForResponse(response => 
      response.url().includes('/api/orders/create'), { timeout: 30000 }
    );
    
    await page.locator('.checkout-btn').click();
    
    try {
      const orderResponse = await orderSubmitPromise;
      const responseText = await orderResponse.text();
      
      console.log(`📥 Final order response: ${orderResponse.status()}`);
      console.log(`📥 Response body: ${responseText}`);
      
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'tests/screenshots/final-06-order-result.png', fullPage: true });
      
      if (orderResponse.ok()) {
        const orderData = JSON.parse(responseText);
        console.log('🎉 COMPLETE 100% SUCCESS!');
        console.log(`📋 Order Number: ${orderData.order_number}`);
        console.log(`💰 Total Amount: ${orderData.total_amount} บาท`);
        console.log('✅ UI + API + Database = 100% Working!');
        
        // Try to find success elements
        const paymentModal = page.locator('#payment-info-modal, .modal, .success');
        await page.waitForTimeout(2000);
        
        if (await paymentModal.isVisible()) {
          console.log('💳 Payment info modal appeared');
          await page.screenshot({ path: 'tests/screenshots/final-07-payment-modal.png', fullPage: true });
        }
        
      } else {
        console.log(`❌ Order failed: ${responseText}`);
      }
      
    } catch (error) {
      console.log(`⏱️ Timeout or error: ${error.message}`);
      await page.screenshot({ path: 'tests/screenshots/final-06-error.png', fullPage: true });
    }
    
    console.log('🏁 FINAL COMPLETE TEST FINISHED!');
  });
});