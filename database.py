import sqlite3
import json
from datetime import datetime

class ShabuDatabase:
    """คลาสสำหรับจัดการฐานข้อมูล SQLite ของระบบ POS"""
    
    def __init__(self, db_name="shabu_pos.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """เชื่อมต่อกับฐานข้อมูล"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"✓ เชื่อมต่อฐานข้อมูล {self.db_name} สำเร็จ")
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
    
    def create_tables(self):
        """สร้างตารางทั้งหมดในฐานข้อมูล"""
        try:
            # ตาราง menu_items - เก็บรายการเมนูอาหาร
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    price INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ตาราง tables - เก็บข้อมูลโต๊ะ
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ตาราง orders - เก็บออเดอร์ปัจจุบัน (บิลที่ยังไม่ชำระ)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_id INTEGER NOT NULL,
                    menu_item_id INTEGER NOT NULL,
                    menu_name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (table_id) REFERENCES tables(id),
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
                )
            ''')
            
            # ตาราง sales_history - เก็บประวัติการขาย (บิลที่ชำระแล้ว)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id TEXT NOT NULL UNIQUE,
                    table_name TEXT NOT NULL,
                    total_amount INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ตาราง sale_items - เก็บรายการในแต่ละบิล
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    menu_name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales_history(id)
                )
            ''')
            
            self.conn.commit()
            print("✓ สร้างตารางฐานข้อมูลสำเร็จ")
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาดในการสร้างตาราง: {e}")
    
    # ==================== Menu Items ====================
    
    def add_menu_item(self, name, price):
        """เพิ่มเมนูอาหาร"""
        try:
            self.cursor.execute(
                "INSERT INTO menu_items (name, price) VALUES (?, ?)",
                (name, price)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # ชื่อซ้ำ
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return False
    
    def update_menu_item(self, old_name, new_name, price):
        """แก้ไขเมนูอาหาร"""
        try:
            self.cursor.execute(
                "UPDATE menu_items SET name=?, price=?, updated_at=CURRENT_TIMESTAMP WHERE name=?",
                (new_name, price, old_name)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return False
    
    def delete_menu_item(self, name):
        """ลบเมนูอาหาร"""
        try:
            self.cursor.execute("DELETE FROM menu_items WHERE name=?", (name,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return False
    
    def get_all_menu_items(self):
        """ดึงรายการเมนูทั้งหมด"""
        try:
            self.cursor.execute("SELECT name, price FROM menu_items ORDER BY name")
            return {row[0]: row[1] for row in self.cursor.fetchall()}
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return {}
    
    def get_menu_item_id(self, name):
        """ดึง ID ของเมนู"""
        try:
            self.cursor.execute("SELECT id FROM menu_items WHERE name=?", (name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return None
    
    # ==================== Tables ====================
    
    def add_table(self, table_name):
        """เพิ่มโต๊ะ"""
        try:
            self.cursor.execute(
                "INSERT INTO tables (table_name) VALUES (?)",
                (table_name,)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # ชื่อซ้ำ
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return False
    
    def rename_table(self, old_name, new_name):
        """เปลี่ยนชื่อโต๊ะ"""
        try:
            self.cursor.execute(
                "UPDATE tables SET table_name=? WHERE table_name=?",
                (new_name, old_name)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return False
    
    def delete_table(self, table_name):
        """ลบโต๊ะ"""
        try:
            # ลบออเดอร์ของโต๊ะนี้ก่อน
            table_id = self.get_table_id(table_name)
            if table_id:
                self.cursor.execute("DELETE FROM orders WHERE table_id=?", (table_id,))
            
            # ลบโต๊ะ
            self.cursor.execute("DELETE FROM tables WHERE table_name=?", (table_name,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return False
    
    def get_all_tables(self):
        """ดึงรายการโต๊ะทั้งหมด"""
        try:
            self.cursor.execute("SELECT table_name FROM tables ORDER BY table_name")
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return []
    
    def get_table_id(self, table_name):
        """ดึง ID ของโต๊ะ"""
        try:
            self.cursor.execute("SELECT id FROM tables WHERE table_name=?", (table_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return None
    
    # ==================== Orders ====================
    
    def add_order_item(self, table_name, menu_name, price):
        """เพิ่มรายการในออเดอร์"""
        try:
            table_id = self.get_table_id(table_name)
            menu_id = self.get_menu_item_id(menu_name)
            
            if not table_id or not menu_id:
                return False
            
            self.cursor.execute(
                "INSERT INTO orders (table_id, menu_item_id, menu_name, price) VALUES (?, ?, ?, ?)",
                (table_id, menu_id, menu_name, price)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return False
    
    def get_table_orders(self, table_name):
        """ดึงรายการออเดอร์ของโต๊ะ"""
        try:
            table_id = self.get_table_id(table_name)
            if not table_id:
                return []
            
            self.cursor.execute(
                "SELECT id, menu_name, price FROM orders WHERE table_id=? ORDER BY created_at",
                (table_id,)
            )
            return [{"id": row[0], "name": row[1], "price": row[2]} for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return []
    
    def delete_order_item(self, order_id):
        """ลบรายการจากออเดอร์"""
        try:
            self.cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return False
    
    def clear_table_orders(self, table_name):
        """ล้างออเดอร์ทั้งหมดของโต๊ะ"""
        try:
            table_id = self.get_table_id(table_name)
            if not table_id:
                return False
            
            self.cursor.execute("DELETE FROM orders WHERE table_id=?", (table_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return False
    
    # ==================== Sales History ====================
    
    def add_sale(self, bill_id, table_name, items, total):
        """บันทึกการขาย"""
        try:
            # เพิ่มข้อมูลหลักของบิล
            self.cursor.execute(
                "INSERT INTO sales_history (bill_id, table_name, total_amount) VALUES (?, ?, ?)",
                (bill_id, table_name, total)
            )
            sale_id = self.cursor.lastrowid
            
            # เพิ่มรายการในบิล
            for item in items:
                self.cursor.execute(
                    "INSERT INTO sale_items (sale_id, menu_name, price) VALUES (?, ?, ?)",
                    (sale_id, item['name'], item['price'])
                )
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            self.conn.rollback()
            return False
    
    def get_all_sales(self):
        """ดึงประวัติการขายทั้งหมด"""
        try:
            self.cursor.execute("""
                SELECT bill_id, table_name, total_amount, created_at 
                FROM sales_history 
                ORDER BY created_at DESC
            """)
            
            sales = []
            for row in self.cursor.fetchall():
                sales.append({
                    'id': row[0],
                    'table': row[1],
                    'total': row[2],
                    'timestamp': row[3]
                })
            return sales
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return []
    
    def get_sale_details(self, bill_id):
        """ดึงรายละเอียดของบิล"""
        try:
            # ดึงข้อมูลหลักของบิล
            self.cursor.execute(
                "SELECT id, table_name, total_amount, created_at FROM sales_history WHERE bill_id=?",
                (bill_id,)
            )
            sale = self.cursor.fetchone()
            
            if not sale:
                return None
            
            sale_id, table_name, total, timestamp = sale
            
            # ดึงรายการในบิล
            self.cursor.execute(
                "SELECT menu_name, price FROM sale_items WHERE sale_id=?",
                (sale_id,)
            )
            items = [{'name': row[0], 'price': row[1]} for row in self.cursor.fetchall()]
            
            return {
                'id': bill_id,
                'table': table_name,
                'total': total,
                'timestamp': timestamp,
                'items': items
            }
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return None
    
    def delete_sale(self, bill_id):
        """ลบประวัติการขาย"""
        try:
            # ดึง sale_id
            self.cursor.execute("SELECT id FROM sales_history WHERE bill_id=?", (bill_id,))
            result = self.cursor.fetchone()
            
            if not result:
                return False
            
            sale_id = result[0]
            
            # ลบรายการในบิล
            self.cursor.execute("DELETE FROM sale_items WHERE sale_id=?", (sale_id,))
            
            # ลบบิล
            self.cursor.execute("DELETE FROM sales_history WHERE id=?", (sale_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            self.conn.rollback()
            return False
    
    def clear_all_sales(self):
        """ล้างประวัติการขายทั้งหมด"""
        try:
            self.cursor.execute("DELETE FROM sale_items")
            self.cursor.execute("DELETE FROM sales_history")
            self.conn.commit()
            return True
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            self.conn.rollback()
            return False
    
    def search_sales(self, search_text, search_field="all"):
        """ค้นหาประวัติการขาย"""
        try:
            search_text = f"%{search_text}%"
            
            if search_field == "all":
                query = """
                    SELECT bill_id, table_name, total_amount, created_at 
                    FROM sales_history 
                    WHERE bill_id LIKE ? OR table_name LIKE ? OR 
                          CAST(total_amount AS TEXT) LIKE ? OR created_at LIKE ?
                    ORDER BY created_at DESC
                """
                params = (search_text, search_text, search_text, search_text)
            elif search_field == "bill_id":
                query = "SELECT bill_id, table_name, total_amount, created_at FROM sales_history WHERE bill_id LIKE ? ORDER BY created_at DESC"
                params = (search_text,)
            elif search_field == "table":
                query = "SELECT bill_id, table_name, total_amount, created_at FROM sales_history WHERE table_name LIKE ? ORDER BY created_at DESC"
                params = (search_text,)
            elif search_field == "date":
                query = "SELECT bill_id, table_name, total_amount, created_at FROM sales_history WHERE created_at LIKE ? ORDER BY created_at DESC"
                params = (search_text,)
            elif search_field == "total":
                query = "SELECT bill_id, table_name, total_amount, created_at FROM sales_history WHERE CAST(total_amount AS TEXT) LIKE ? ORDER BY created_at DESC"
                params = (search_text,)
            else:
                return []
            
            self.cursor.execute(query, params)
            
            sales = []
            for row in self.cursor.fetchall():
                sales.append({
                    'id': row[0],
                    'table': row[1],
                    'total': row[2],
                    'timestamp': row[3]
                })
            return sales
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาด: {e}")
            return []
    
    # ==================== Utility ====================
    
    def initialize_default_data(self):
        """สร้างข้อมูลเริ่มต้น"""
        # เพิ่มเมนูเริ่มต้น
        default_menu = {
            "ชุดหมูสไลด์": 159,
            "ชุดเนื้อสไลด์": 199,
            "ชุดผักรวม": 59,
            "ลูกชิ้นรวม": 69,
            "กุ้งสด": 89,
            "หมึกสด": 79,
            "ข้าวผัดกระเทียม": 35,
            "น้ำรีฟิล": 39
        }
        
        for name, price in default_menu.items():
            self.add_menu_item(name, price)
        
        # เพิ่มโต๊ะเริ่มต้น
        for i in range(1, 10):
            self.add_table(f"T{i}")
        
        print("✓ สร้างข้อมูลเริ่มต้นสำเร็จ")
    
    def close(self):
        """ปิดการเชื่อมต่อฐานข้อมูล"""
        if self.conn:
            self.conn.close()
            print("✓ ปิดการเชื่อมต่อฐานข้อมูล")
    
    def __del__(self):
        """Destructor - ปิดการเชื่อมต่ออัตโนมัติ"""
        self.close()


# ทดสอบการใช้งาน
if __name__ == "__main__":
    # สร้างฐานข้อมูล
    db = ShabuDatabase()
    
    # ตรวจสอบว่ามีข้อมูลหรือยัง
    if not db.get_all_menu_items():
        print("ไม่มีข้อมูล - กำลังสร้างข้อมูลเริ่มต้น...")
        db.initialize_default_data()
    
    # แสดงข้อมูล
    print("\n=== รายการเมนู ===")
    for name, price in db.get_all_menu_items().items():
        print(f"{name}: {price} บาท")
    
    print("\n=== รายการโต๊ะ ===")
    for table in db.get_all_tables():
        print(f"- {table}")
    
    print("\nทดสอบฐานข้อมูลสำเร็จ!")
