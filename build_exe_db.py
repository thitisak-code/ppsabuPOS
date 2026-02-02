"""
สคริปต์สำหรับแปลง main_with_database.py เป็นไฟล์ .exe
ใช้งาน: python build_exe_db.py
"""

import os
import sys

def build_exe():
    """สร้างไฟล์ .exe จาก main_with_database.py"""
    
    print("=" * 60)
    print("กำลังแปลงโปรแกรมเป็นไฟล์ .exe (เวอร์ชัน Database)")
    print("=" * 60)
    
    # ตรวจสอบว่าติดตั้ง PyInstaller แล้วหรือยัง
    try:
        import PyInstaller
        print("✓ พบ PyInstaller แล้ว")
    except ImportError:
        print("✗ ไม่พบ PyInstaller")
        print("\nกำลังติดตั้ง PyInstaller...")
        os.system(f"{sys.executable} -m pip install pyinstaller")
        print("✓ ติดตั้ง PyInstaller เรียบร้อย")
    
    # คำสั่งสร้าง .exe
    # --onefile = รวมทุกอย่างเป็นไฟล์เดียว
    # --windowed = ไม่แสดง console window
    # --name = ชื่อไฟล์ .exe
    # --add-data = เพิ่มไฟล์ database.py
    
    command = f'pyinstaller --onefile --windowed --name "POS ชาบู (Database)" --hidden-import=database main_with_database.py'
    
    print("\nกำลังสร้างไฟล์ .exe...")
    print(f"คำสั่ง: {command}")
    print("-" * 60)
    
    result = os.system(command)
    
    if result == 0:
        print("\n" + "=" * 60)
        print("✓ สร้างไฟล์ .exe สำเร็จ!")
        print("=" * 60)
        print("\nไฟล์ .exe อยู่ที่: dist/POS ชาบู (Database).exe")
        print("\nวิธีใช้งาน:")
        print("1. คลิกเปิดไฟล์ .exe ได้เลย (ไม่ต้องติดตั้ง Python)")
        print("2. ข้อมูลจะถูกบันทึกในไฟล์ shabu_pos.db (SQLite)")
        print("3. เปิด-ปิดโปรแกรมได้ตามต้องการ ข้อมูลจะไม่หาย")
        print("4. ไม่กินแรมเมื่อไม่ได้ใช้งาน")
        print("\nข้อดี:")
        print("- ✓ ใช้ SQLite Database (รวดเร็ว ปลอดภัย)")
        print("- ✓ ค้นหาข้อมูลได้เร็ว")
        print("- ✓ รองรับข้อมูลจำนวนมาก")
        print("- ✓ ข้อมูลจัดเก็บเป็นระเบียบ")
    else:
        print("\n" + "=" * 60)
        print("✗ เกิดข้อผิดพลาดในการสร้างไฟล์ .exe")
        print("=" * 60)

if __name__ == "__main__":
    build_exe()
