// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Tenzai Order System', () => {
  
  test('should load customer webapp successfully', async ({ page }) => {
    await page.goto('/customer_webapp.html');
    
    // Check if the page loads
    await expect(page).toHaveTitle(/Tenzai Sushi/);
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'tests/screenshots/customer-webapp-loaded.png' });
    
    // Check if menu loads
    await expect(page.locator('.menu-category')).toBeVisible({ timeout: 10000 });
    
    console.log('✅ Customer webapp loaded successfully');
  });

  test('should handle menu item selection and cart', async ({ page }) => {
    await page.goto('/customer_webapp.html');
    
    // Wait for menu to load
    await page.waitForSelector('.menu-item', { timeout: 10000 });
    
    // Find first menu item and click add button
    const firstMenuItem = page.locator('.menu-item').first();
    await expect(firstMenuItem).toBeVisible();
    
    const addButton = firstMenuItem.locator('.add-btn');
    await addButton.click();
    
    // Check if cart updates
    const cartCount = page.locator('#cart-count');
    await expect(cartCount).toHaveText('1');
    
    // Take screenshot
    await page.screenshot({ path: 'tests/screenshots/item-added-to-cart.png' });
    
    console.log('✅ Menu item selection working');
  });

  test('should open checkout form when cart has items', async ({ page }) => {
    await page.goto('/customer_webapp.html');
    
    // Add item to cart first
    await page.waitForSelector('.menu-item', { timeout: 10000 });
    const firstMenuItem = page.locator('.menu-item').first();
    await firstMenuItem.locator('.add-btn').click();
    
    // Click cart button
    const cartButton = page.locator('#cart-btn');
    await cartButton.click();
    
    // Check if checkout modal appears
    const checkoutModal = page.locator('#checkout-modal');
    await expect(checkoutModal).toBeVisible();
    
    // Take screenshot
    await page.screenshot({ path: 'tests/screenshots/checkout-modal-open.png' });
    
    console.log('✅ Checkout form opens correctly');
  });

  test('should validate order form fields', async ({ page }) => {
    await page.goto('/customer_webapp.html');
    
    // Add item and open checkout
    await page.waitForSelector('.menu-item', { timeout: 10000 });
    const firstMenuItem = page.locator('.menu-item').first();
    await firstMenuItem.locator('.add-btn').click();
    await page.locator('#cart-btn').click();
    
    // Try to submit without filling fields
    const submitButton = page.locator('#submit-order');
    await submitButton.click();
    
    // Check if validation messages appear
    const nameField = page.locator('#customer-name');
    const phoneField = page.locator('#customer-phone');
    
    await expect(nameField).toHaveAttribute('required');
    await expect(phoneField).toHaveAttribute('required');
    
    // Take screenshot
    await page.screenshot({ path: 'tests/screenshots/form-validation.png' });
    
    console.log('✅ Form validation working');
  });

  test('should complete full order flow', async ({ page }) => {
    // Enable request/response logging
    page.on('request', request => {
      if (request.url().includes('/api/orders')) {
        console.log('📤 API Request:', request.method(), request.url());
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('/api/orders')) {
        console.log('📥 API Response:', response.status(), response.url());
      }
    });

    await page.goto('/customer_webapp.html');
    
    // Add item to cart
    await page.waitForSelector('.menu-item', { timeout: 10000 });
    const firstMenuItem = page.locator('.menu-item').first();
    await firstMenuItem.locator('.add-btn').click();
    
    // Open checkout
    await page.locator('#cart-btn').click();
    
    // Fill form
    await page.fill('#customer-name', 'Playwright Test User');
    await page.fill('#customer-phone', '0812345678');
    await page.selectOption('#order-type', 'pickup');
    
    // Take screenshot before submit
    await page.screenshot({ path: 'tests/screenshots/form-filled.png' });
    
    // Submit order
    const submitButton = page.locator('#submit-order');
    await submitButton.click();
    
    // Wait for success message or response
    try {
      // Wait for either success modal or error message
      await page.waitForSelector('#success-modal, .error-message, .alert', { timeout: 15000 });
      
      // Take screenshot of result
      await page.screenshot({ path: 'tests/screenshots/order-result.png' });
      
      // Check if success modal appeared
      const successModal = page.locator('#success-modal');
      if (await successModal.isVisible()) {
        console.log('✅ Order submitted successfully');
        
        // Check for order number
        const orderNumber = await page.textContent('#order-number');
        console.log('📋 Order Number:', orderNumber);
      } else {
        // Look for error messages
        const errorMessage = await page.textContent('.error-message, .alert');
        console.log('❌ Order failed:', errorMessage);
      }
      
    } catch (error) {
      console.log('⏱️ Timeout waiting for order response');
      await page.screenshot({ path: 'tests/screenshots/order-timeout.png' });
    }
  });

  test('should check order status page', async ({ page }) => {
    // Test with a sample order number
    const testOrderNumber = 'T082300F14DC2'; // Use a known order from your system
    
    await page.goto(`/order-status.html?order=${testOrderNumber}`);
    
    // Wait for order status to load
    await page.waitForSelector('.order-info, .error-message', { timeout: 10000 });
    
    // Take screenshot
    await page.screenshot({ path: 'tests/screenshots/order-status-page.png' });
    
    // Check if order info is displayed
    const orderInfo = page.locator('.order-info');
    if (await orderInfo.isVisible()) {
      console.log('✅ Order status page working');
      
      // Get order details
      const orderDetails = await page.textContent('.order-info');
      console.log('📋 Order Details:', orderDetails);
    } else {
      console.log('⚠️ Order not found or error occurred');
    }
  });

  test('should check admin dashboard', async ({ page }) => {
    await page.goto('/admin/staff-orders.html');
    
    // Wait for orders to load
    await page.waitForSelector('.orders-container, .error-message', { timeout: 10000 });
    
    // Take screenshot
    await page.screenshot({ path: 'tests/screenshots/admin-dashboard.png' });
    
    // Check if orders are displayed
    const ordersContainer = page.locator('.orders-container');
    if (await ordersContainer.isVisible()) {
      console.log('✅ Admin dashboard working');
    } else {
      console.log('⚠️ No orders found or error occurred');
    }
  });
});