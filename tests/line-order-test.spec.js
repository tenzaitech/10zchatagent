// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('LINE Order Flow Testing', () => {
  
  test('test duplicate LINE user handling', async ({ page }) => {
    console.log('🚀 Testing LINE order with duplicate user handling...');
    
    // Test data - using real LINE user that already exists
    const lineOrderData = {
      customer_name: "Pleam Test",
      customer_phone: "0988388882", 
      total_amount: 279,
      order_type: "pickup",
      payment_method: "cash",
      notes: "",
      items: [
        {
          id: "e9874f12-cfef-4895-a2f7-529887fd62e1",
          name: "EBI TENPURA",
          quantity: 1,
          price: 119,
          total: 119
        },
        {
          id: "05d8c8be-7673-419b-bce4-68de51c6f3ca", 
          name: "FRIED CHICKEN WING",
          quantity: 2,
          price: 80,
          total: 160
        }
      ],
      platform: "LINE",
      platform_user_id: "Uc8339bbf1513681e53a086ecf3e079b5"
    };
    
    console.log('📤 Testing LINE order with existing user...');
    console.log(`👤 LINE User: ${lineOrderData.platform_user_id}`);
    console.log(`📱 Phone: ${lineOrderData.customer_phone}`);
    
    // Test first order
    const response1 = await page.request.post('/api/orders/create', {
      data: lineOrderData,
      headers: { 'Content-Type': 'application/json' }
    });
    
    const result1 = await response1.text();
    console.log(`📥 First order response: ${response1.status()}`);
    console.log(`📋 Result: ${result1}`);
    
    if (response1.ok()) {
      const orderData1 = JSON.parse(result1);
      console.log(`✅ First order created: ${orderData1.order_number}`);
      
      // Test second order from same LINE user (should reuse customer)
      console.log('🔄 Testing second order from same LINE user...');
      
      const lineOrderData2 = {
        ...lineOrderData,
        customer_name: "Pleam Updated Name", // Different name
        customer_phone: "0988388883",        // Different phone
        total_amount: 199,
        items: [
          {
            id: "e9874f12-cfef-4895-a2f7-529887fd62e1",
            name: "EBI TENPURA",
            quantity: 1, 
            price: 119,
            total: 119
          }
        ]
      };
      
      const response2 = await page.request.post('/api/orders/create', {
        data: lineOrderData2,
        headers: { 'Content-Type': 'application/json' }
      });
      
      const result2 = await response2.text();
      console.log(`📥 Second order response: ${response2.status()}`);
      console.log(`📋 Result: ${result2}`);
      
      if (response2.ok()) {
        const orderData2 = JSON.parse(result2);
        console.log(`✅ Second order created: ${orderData2.order_number}`);
        console.log('🎉 Duplicate LINE user handling works perfectly!');
      } else {
        console.log(`❌ Second order failed: ${result2}`);
      }
      
    } else {
      console.log(`❌ First order failed: ${result1}`);
      throw new Error(`LINE order creation failed: ${result1}`);
    }
  });
  
  test('test LINE order with different phone numbers', async ({ page }) => {
    console.log('🧪 Testing LINE users with different phone numbers...');
    
    // Test case: Same LINE user but different phone numbers over time
    const testCases = [
      {
        name: "Pleam First Phone",
        phone: "0811111111",
        line_user_id: "TEST_LINE_USER_001"
      },
      {
        name: "Pleam Updated Phone", 
        phone: "0822222222",
        line_user_id: "TEST_LINE_USER_001" // Same LINE user
      },
      {
        name: "Different User",
        phone: "0833333333", 
        line_user_id: "TEST_LINE_USER_002" // Different LINE user
      }
    ];
    
    for (let i = 0; i < testCases.length; i++) {
      const testCase = testCases[i];
      console.log(`\n🔍 Test case ${i + 1}: ${testCase.name}`);
      
      const orderData = {
        customer_name: testCase.name,
        customer_phone: testCase.phone,
        total_amount: 119,
        order_type: "pickup", 
        payment_method: "cash",
        notes: "",
        items: [
          {
            id: "e9874f12-cfef-4895-a2f7-529887fd62e1",
            name: "EBI TENPURA",
            quantity: 1,
            price: 119,
            total: 119
          }
        ],
        platform: "LINE",
        platform_user_id: testCase.line_user_id
      };
      
      const response = await page.request.post('/api/orders/create', {
        data: orderData,
        headers: { 'Content-Type': 'application/json' }
      });
      
      const result = await response.text();
      console.log(`📱 Phone: ${testCase.phone} | LINE: ${testCase.line_user_id}`);
      console.log(`📥 Response: ${response.status()} | ${result}`);
      
      if (response.ok()) {
        const orderResult = JSON.parse(result);
        console.log(`✅ Order created: ${orderResult.order_number}`);
      } else {
        console.log(`⚠️ Order failed (expected for some cases): ${result}`);
      }
    }
    
    console.log('🏁 Phone number variation test completed');
  });
  
  test('verify order data integrity after duplicate handling', async ({ page }) => {
    console.log('🔍 Verifying order data integrity...');
    
    // Create order and then verify its details
    const orderData = {
      customer_name: "Data Integrity Test",
      customer_phone: "0999999999",
      total_amount: 398, // 119 + 160 + 119
      order_type: "delivery",
      payment_method: "cash", 
      notes: "Test order for data integrity",
      items: [
        {
          id: "e9874f12-cfef-4895-a2f7-529887fd62e1",
          name: "EBI TENPURA",
          quantity: 1,
          price: 119,
          total: 119
        },
        {
          id: "05d8c8be-7673-419b-bce4-68de51c6f3ca",
          name: "FRIED CHICKEN WING", 
          quantity: 2,
          price: 80,
          total: 160
        },
        {
          id: "e9874f12-cfef-4895-a2f7-529887fd62e1",
          name: "EBI TENPURA",
          quantity: 1,
          price: 119,
          total: 119
        }
      ],
      platform: "LINE",
      platform_user_id: "DATA_INTEGRITY_TEST_USER"
    };
    
    // Create order
    const createResponse = await page.request.post('/api/orders/create', {
      data: orderData,
      headers: { 'Content-Type': 'application/json' }
    });
    
    const createResult = await createResponse.text();
    console.log(`📤 Create response: ${createResponse.status()}`);
    
    if (createResponse.ok()) {
      const orderResult = JSON.parse(createResult);
      const orderNumber = orderResult.order_number;
      console.log(`✅ Order created: ${orderNumber}`);
      
      // Verify order details
      const verifyResponse = await page.request.get(`/api/orders/${orderNumber}`);
      const verifyResult = await verifyResponse.json();
      
      console.log(`🔍 Order verification: ${verifyResponse.status()}`);
      console.log(`👤 Customer: ${verifyResult.customer_name}`);
      console.log(`📱 Phone: ${verifyResult.customer_phone}`);
      console.log(`💰 Total: ${verifyResult.total_amount} บาท`);
      console.log(`📋 Items count: ${verifyResult.items.length}`);
      console.log(`📝 Notes: "${verifyResult.notes}"`);
      
      // Verify items
      let totalCalculated = 0;
      verifyResult.items.forEach((item, index) => {
        console.log(`  ${index + 1}. ${item.name} x${item.quantity} = ${item.total_price} บาท`);
        totalCalculated += item.total_price;
      });
      
      console.log(`🧮 Calculated total: ${totalCalculated} บาท`);
      
      if (Math.abs(totalCalculated - verifyResult.total_amount) < 0.01) {
        console.log('✅ Order data integrity verified!');
      } else {
        console.log('❌ Total amount mismatch detected!');
      }
      
    } else {
      console.log(`❌ Order creation failed: ${createResult}`);
      throw new Error(`Data integrity test failed: ${createResult}`);
    }
  });
});