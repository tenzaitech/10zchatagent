-- 006_create_conversations.sql
-- ตารางบทสนทนา

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    line_user_id VARCHAR(100) NOT NULL, -- LINE User ID
    message_text TEXT, -- ข้อความจากลูกค้า
    response_text TEXT, -- ข้อความตอบกลับ
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- สร้าง indexes
CREATE INDEX idx_conversations_line_user ON conversations(line_user_id);
CREATE INDEX idx_conversations_date ON conversations(created_at);

-- ตัวอย่างข้อมูลบทสนทนา
INSERT INTO conversations (line_user_id, message_text, response_text) VALUES
('U4af4980629example1', 'สวัสดีครับ', 'สวัสดีค่ะ! ยินดีต้อนรับสู่ Tenzai Sushi 🍣 ต้องการดูเมนูหรือสั่งอาหารคะ?'),
('U4af4980629example1', 'อยากดูเมนู', 'เชิญดูเมนูของเราได้ที่ลิงก์นี้ค่ะ: https://n8n-dev.tenzaitech.online/menu'),
('U4af4980629example2', 'มีซูชิอะไรบ้าง', 'เรามีซูชิหลายชนิดค่ะ เช่น แซลมอนซูชิ, ทูน่าซูชิ, วากิวซูชิ ราคาเริ่มต้น 15 บาท/คำ');