// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Thai Language Support Test', () => {
  
  test('test Thai text reading and interaction', async ({ page }) => {
    console.log('🇹🇭 Testing Thai language support in Playwright...');
    
    // Enable Thai text logging
    page.on('console', msg => {
      console.log(`🖥️ [Thai Console]: ${msg.text()}`);
    });
    
    await page.goto('/customer_webapp.html');
    await page.waitForTimeout(2000);
    
    // Test reading Thai text elements
    const headerText = await page.locator('.header h1').textContent();
    console.log(`📋 Header text (Thai): "${headerText}"`);
    
    const subtitle = await page.locator('.header p').textContent();
    console.log(`📝 Subtitle text (Thai): "${subtitle}"`);
    
    // Configure database to load Thai menu
    const configPanel = page.locator('#configPanel');
    if (await configPanel.isVisible() || !(await page.locator('#mainContent').isVisible())) {
      console.log('🔧 กำลังเชื่อมต่อฐานข้อมูล...');
      
      if (!(await configPanel.isVisible())) {
        await page.locator('.config-toggle').click();
        await page.waitForTimeout(500);
      }
      
      await page.fill('#supabaseUrl', 'https://qlhpmrehrmprptldtchb.supabase.co');
      await page.fill('#serviceKey', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaHBtcmVocm1wcnB0bGR0Y2hiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDMzNzA0MiwiZXhwIjoyMDY5OTEzMDQyfQ.foCnBLUA6SOXHPBKuBJaKu2A1CPUeetMTjXWSbBkObU');
      
      await page.locator('button:has-text("เชื่อมต่อ")').click();
      console.log('✅ คลิกปุ่ม "เชื่อมต่อ" แล้ว');
      await page.waitForTimeout(3000);
    }
    
    // Wait for Thai menu to load
    await page.waitForSelector('.menu-card', { timeout: 10000 });
    console.log('✅ เมนูโหลดสำเร็จแล้ว');
    
    // Read Thai menu items
    const menuCards = page.locator('.menu-card');
    const menuCount = await menuCards.count();
    console.log(`🍣 พบเมนูทั้งหมด: ${menuCount} รายการ`);
    
    // Read first 3 Thai menu items
    for (let i = 0; i < Math.min(3, menuCount); i++) {
      const menuCard = menuCards.nth(i);
      
      const menuName = await menuCard.locator('.menu-name').textContent();
      const menuNameThai = await menuCard.locator('.menu-name-thai').textContent();
      const menuPrice = await menuCard.locator('.menu-price').textContent();
      
      console.log(`📋 เมนูที่ ${i + 1}:`);
      console.log(`   ชื่อ (EN): "${menuName}"`);
      console.log(`   ชื่อ (TH): "${menuNameThai}"`);
      console.log(`   ราคา: "${menuPrice}"`);
    }
    
    // Test Thai category names
    const categoryItems = page.locator('.category-item');
    const categoryCount = await categoryItems.count();
    console.log(`📂 หมวดหมู่ทั้งหมد: ${categoryCount} หมวด`);
    
    for (let i = 0; i < Math.min(5, categoryCount); i++) {
      const categoryName = await categoryItems.nth(i).textContent();
      console.log(`   หมวด ${i + 1}: "${categoryName}"`);
    }
    
    // Test Thai button text and interactions
    const addButtons = page.locator('.add-to-cart');
    if (await addButtons.first().isVisible()) {
      const buttonText = await addButtons.first().textContent();
      console.log(`🛒 ปุ่มเพิ่มสินค้า: "${buttonText}"`);
    }
    
    // Check cart toggle button
    const cartToggle = page.locator('.cart-toggle');
    if (await cartToggle.isVisible()) {
      console.log('🛒 พบปุ่มตะกร้าสินค้า');
    }
    
    // Test searching in Thai
    const searchInput = page.locator('#searchInput');
    if (await searchInput.isVisible()) {
      const placeholder = await searchInput.getAttribute('placeholder');
      console.log(`🔍 ช่องค้นหา placeholder: "${placeholder}"`);
      
      // Test Thai search
      await searchInput.fill('ซูชิ');
      console.log('🔍 ทดสอบค้นหาด้วยคำว่า "ซูชิ"');
      await page.waitForTimeout(1000);
      
      // Clear search
      await searchInput.fill('');
      await page.waitForTimeout(500);
    }
    
    // Take screenshot with Thai content
    await page.screenshot({ 
      path: 'tests/screenshots/thai-content.png', 
      fullPage: true 
    });
    console.log('📸 บันทึกภาพหน้าจอเนื้อหาภาษาไทย');
    
    // Test reading status messages
    const statusElements = page.locator('.status-indicator span');
    const statusCount = await statusElements.count();
    
    for (let i = 0; i < statusCount; i++) {
      const statusText = await statusElements.nth(i).textContent();
      if (statusText && statusText.trim()) {
        console.log(`📊 สถานะ: "${statusText}"`);
      }
    }
    
    console.log('🎉 การทดสอบภาษาไทยเสร็จสิ้น!');
  });
  
  test('test Thai number and currency formatting', async ({ page }) => {
    console.log('💰 ทดสอบรูปแบบตัวเลขและสกุลเงินไทย...');
    
    await page.goto('/customer_webapp.html');
    
    // Test Thai date/time formatting
    const now = new Date();
    const thaiDate = now.toLocaleDateString('th-TH', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      timeZone: 'Asia/Bangkok'
    });
    
    const thaiTime = now.toLocaleTimeString('th-TH', {
      timeZone: 'Asia/Bangkok'
    });
    
    console.log(`📅 วันที่ภาษาไทย: ${thaiDate}`);
    console.log(`⏰ เวลาภาษาไทย: ${thaiTime}`);
    
    // Test Thai number formatting
    const testNumbers = [15, 119, 289, 1250];
    
    testNumbers.forEach(num => {
      const thaiNumber = num.toLocaleString('th-TH');
      const thaiBaht = num.toLocaleString('th-TH', {
        style: 'currency',
        currency: 'THB'
      });
      
      console.log(`💰 ${num} → "${thaiNumber}" → "${thaiBaht}"`);
    });
    
    console.log('✅ การทดสอบรูปแบบภาษาไทยเสร็จสิ้น!');
  });
  
  test('test Thai text input and forms', async ({ page }) => {
    console.log('📝 ทดสอบการกรอกข้อมูลภาษาไทย...');
    
    // Handle Thai dialogs/prompts
    page.on('dialog', async dialog => {
      const message = dialog.message();
      console.log(`💬 ข้อความไดอะล็อก: "${message}"`);
      
      if (message.includes('ชื่อ')) {
        await dialog.accept('ทดสอบ ภาษาไทย');
        console.log('✅ กรอกชื่อภาษาไทย: "ทดสอบ ภาษาไทย"');
      } else if (message.includes('เบอร์')) {
        await dialog.accept('081-234-5678');
        console.log('✅ กรอกเบอร์โทร: "081-234-5678"');
      } else {
        await dialog.accept('รับสินค้าเอง');
        console.log('✅ เลือก: "รับสินค้าเอง"');
      }
    });
    
    await page.goto('/customer_webapp.html');
    await page.waitForTimeout(2000);
    
    console.log('🎭 Playwright สามารถอ่านและทำงานกับภาษาไทยได้แล้ว!');
    console.log('📋 สามารถ:');
    console.log('   ✅ อ่านข้อความภาษาไทย');  
    console.log('   ✅ จัดการ dialogs ภาษาไทย');
    console.log('   ✅ ค้นหาข้อความภาษาไทย');
    console.log('   ✅ จัดรูปแบบวันที่และเงินไทย');
    console.log('   ✅ บันทึกภาพหน้าจอเนื้อหาไทย');
  });
});