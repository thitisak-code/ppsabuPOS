import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, ttk
from datetime import datetime
from database import ShabuDatabase

class ShabuPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("ระบบจัดการร้าน: เพลิดเพลินชาบู")
        self.root.geometry("1200x750")
        
        # เชื่อมต่อฐานข้อมูล
        self.db = ShabuDatabase("shabu_pos.db")
        
        # ตรวจสอบและสร้างข้อมูลเริ่มต้น
        if not self.db.get_all_menu_items():
            self.db.initialize_default_data()
        
        # ตั้งค่าฟอนต์ภาษาไทยที่ชัดเจน
        self.thai_font = ("TH Sarabun New", 14)
        self.thai_font_bold = ("TH Sarabun New", 14, "bold")
        self.thai_font_large = ("TH Sarabun New", 18, "bold")
        self.thai_font_xlarge = ("TH Sarabun New", 24, "bold")
        
        # หากไม่มีฟอนต์ TH Sarabun New ให้ใช้ Tahoma แทน
        try:
            test_font = tk.font.Font(family="TH Sarabun New", size=14)
        except:
            self.thai_font = ("Tahoma", 12)
            self.thai_font_bold = ("Tahoma", 12, "bold")
            self.thai_font_large = ("Tahoma", 16, "bold")
            self.thai_font_xlarge = ("Tahoma", 20, "bold")

        # โหลดข้อมูลจากฐานข้อมูล
        self.menu_items = self.db.get_all_menu_items()
        self.tables = {table: [] for table in self.db.get_all_tables()}
        
        # โหลดออเดอร์ที่ยังไม่ได้ชำระ
        for table_name in self.tables:
            orders = self.db.get_table_orders(table_name)
            self.tables[table_name] = orders
        
        self.current_table = list(self.tables.keys())[0] if self.tables else "T1"

        # --- UI Layout ---
        self.create_layout()
        self.refresh_table_buttons()
        self.refresh_menu_buttons()
        self.update_bill_view()
        
        # จัดการการปิดหน้าต่าง
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """ฟังก์ชันสำหรับยืนยันการปิดโปรแกรม"""
        if messagebox.askokcancel("ปิดโปรแกรม", "คุณต้องการปิดโปรแกรมใช่หรือไม่?"):
            self.db.close()
            self.root.destroy()

    def create_layout(self):
        # 1. Left: Table Management
        self.frame_left = tk.Frame(self.root, bg="#333", width=250, padx=5, pady=5)
        self.frame_left.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(self.frame_left, text="เพลิดเพลินชาบู", font=self.thai_font_xlarge, 
                fg="#ffcc00", bg="#333").pack(pady=15)
        tk.Label(self.frame_left, text="จัดการโต๊ะ", font=self.thai_font_large, 
                fg="white", bg="#333").pack(pady=5)
        
        # Table Control Buttons
        btn_frame = tk.Frame(self.frame_left, bg="#333")
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="+ เพิ่ม", command=self.add_table, bg="#aaffaa", 
                 font=self.thai_font_bold).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        tk.Button(btn_frame, text="แก้ไข", command=self.rename_table, bg="#ffffaa",
                 font=self.thai_font_bold).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        tk.Button(btn_frame, text="- ลบ", command=self.delete_table, bg="#ffaaaa",
                 font=self.thai_font_bold).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        self.table_container = tk.Frame(self.frame_left, bg="#333")
        self.table_container.pack(fill=tk.BOTH, expand=True, pady=10)

        # History Button
        tk.Button(self.frame_left, text="📜 ประวัติการขาย / ใบเสร็จ", bg="#ff9900", 
                 fg="white", font=self.thai_font_large, command=self.open_history_window, 
                 height=2).pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Exit Button - ปุ่มปิดโปรแกรม
        tk.Button(self.frame_left, text="❌ ปิดโปรแกรม", bg="#c0392b", 
                 fg="white", font=self.thai_font_large, command=self.on_closing, 
                 height=2).pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        # 2. Center: Menu Management
        self.frame_center = tk.Frame(self.root, bg="white")
        self.frame_center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(self.frame_center, bg="white")
        header_frame.pack(fill=tk.X, pady=5)
        tk.Label(header_frame, text="เมนูอาหาร", font=self.thai_font_xlarge, 
                bg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, text="⚙️ จัดการเมนู (เพิ่ม/ลบ/แก้ไข)", 
                 command=self.open_menu_management, bg="#ddd", 
                 font=self.thai_font).pack(side=tk.RIGHT, padx=10)

        self.menu_container = tk.Frame(self.frame_center, bg="white")
        self.menu_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 3. Right: Bill & Checkout
        self.frame_right = tk.Frame(self.root, bg="#f5f5f5", width=380)
        self.frame_right.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbl_current_table = tk.Label(self.frame_right, text=f"โต๊ะ: {self.current_table}", 
                                         font=self.thai_font_xlarge, bg="#f5f5f5", fg="#d35400")
        self.lbl_current_table.pack(pady=15)

        # Header of Listbox
        tk.Label(self.frame_right, text=f"{'รายการ':<20} {'ราคา':>5}", 
                font=("Courier New", 11, "bold"), bg="#f5f5f5").pack(anchor="w", padx=15)

        self.bill_list = tk.Listbox(self.frame_right, font=("Courier New", 13), 
                                    width=35, height=20, borderwidth=0, bg="#fff")
        self.bill_list.pack(padx=10, expand=True, fill=tk.BOTH)

        tk.Button(self.frame_right, text="ลบรายการที่เลือก (ในบิล)", 
                 command=self.remove_item_from_bill, bg="#e74c3c", fg="white",
                 font=self.thai_font_bold).pack(pady=5, fill=tk.X, padx=10)
        
        self.lbl_total = tk.Label(self.frame_right, text="รวม: 0 บาท", 
                                 font=self.thai_font_xlarge, fg="red", bg="#f5f5f5")
        self.lbl_total.pack(pady=10)

        tk.Button(self.frame_right, text="💰 ชำระเงิน (ออกใบเสร็จ)", bg="#27ae60", 
                 fg="white", font=self.thai_font_xlarge, command=self.checkout, 
                 height=2).pack(fill=tk.X, padx=10, pady=20)

    # --- Table Management Functions ---
    def refresh_table_buttons(self):
        for widget in self.table_container.winfo_children():
            widget.destroy()
        
        row, col = 0, 0
        for table_name in self.tables:
            status_color = "#e74c3c" if self.tables[table_name] else "#ecf0f1"
            fg_color = "white" if self.tables[table_name] else "black"
            
            if table_name == self.current_table:
                status_color = "#2ecc71"
                fg_color = "white"

            btn = tk.Button(self.table_container, text=table_name, bg=status_color, 
                          fg=fg_color, font=self.thai_font_bold, height=2, width=8, 
                          command=lambda t=table_name: self.switch_table(t))
            btn.grid(row=row, column=col, padx=2, pady=2)
            
            col += 1
            if col > 2:
                col = 0
                row += 1

    def switch_table(self, table_name):
        self.current_table = table_name
        self.lbl_current_table.config(text=f"โต๊ะ: {self.current_table}")
        self.refresh_table_buttons()
        self.update_bill_view()

    def add_table(self):
        name = simpledialog.askstring("เพิ่มโต๊ะ", "ตั้งชื่อโต๊ะใหม่:")
        if name:
            if self.db.add_table(name):
                self.tables[name] = []
                self.refresh_table_buttons()
                messagebox.showinfo("สำเร็จ", f"เพิ่มโต๊ะ {name} เรียบร้อย")
            else:
                messagebox.showerror("ข้อผิดพลาด", "ชื่อโต๊ะซ้ำ!")

    def rename_table(self):
        old_name = self.current_table
        new_name = simpledialog.askstring("แก้ไขชื่อ", f"เปลี่ยนชื่อ {old_name} เป็น:")
        if new_name and new_name != old_name:
            if self.db.rename_table(old_name, new_name):
                self.tables[new_name] = self.tables.pop(old_name)
                self.switch_table(new_name)
                messagebox.showinfo("สำเร็จ", f"เปลี่ยนชื่อเป็น {new_name} เรียบร้อย")
            else:
                messagebox.showerror("ข้อผิดพลาด", "ชื่อนี้มีอยู่แล้วหรือเกิดข้อผิดพลาด")

    def delete_table(self):
        if len(self.tables[self.current_table]) > 0:
            messagebox.showwarning("เตือน", "โต๊ะนี้ยังมีลูกค้าอยู่ ลบไม่ได้")
            return
        if messagebox.askyesno("ยืนยัน", f"ต้องการลบ {self.current_table} ใช่ไหม?"):
            if self.db.delete_table(self.current_table):
                del self.tables[self.current_table]
                if self.tables:
                    self.switch_table(list(self.tables.keys())[0])
                else:
                    self.current_table = ""
                    self.refresh_table_buttons()
                    self.update_bill_view()
                messagebox.showinfo("สำเร็จ", "ลบโต๊ะเรียบร้อย")

    # --- Menu Management Functions ---
    def refresh_menu_buttons(self):
        for widget in self.menu_container.winfo_children():
            widget.destroy()
        
        # โหลดเมนูจากฐานข้อมูล
        self.menu_items = self.db.get_all_menu_items()
        
        row, col = 0, 0
        for name, price in self.menu_items.items():
            text = f"{name}\n{price}.-"
            btn = tk.Button(self.menu_container, text=text, font=self.thai_font_large, 
                          width=15, height=3, bg="white", relief="raised",
                          command=lambda n=name, p=price: self.add_item_to_bill(n, p))
            btn.grid(row=row, column=col, padx=8, pady=8)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def open_menu_management(self):
        win = Toplevel(self.root)
        win.title("จัดการเมนูอาหาร")
        win.geometry("500x600")

        list_frame = tk.Frame(win)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        lb = tk.Listbox(list_frame, font=self.thai_font_large)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        lb.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=lb.yview)

        def load_menu_list():
            lb.delete(0, tk.END)
            menu_items = self.db.get_all_menu_items()
            for name, price in menu_items.items():
                lb.insert(tk.END, f"{name} - {price} บาท")
        
        load_menu_list()

        def on_select(event):
            selection = lb.curselection()
            if selection:
                text = lb.get(selection[0])
                name = text.split(" - ")[0]
                menu_items = self.db.get_all_menu_items()
                price = menu_items.get(name, 0)
                entry_name.delete(0, tk.END)
                entry_name.insert(0, name)
                entry_price.delete(0, tk.END)
                entry_price.insert(0, str(price))
        
        lb.bind("<<ListboxSelect>>", on_select)

        control_frame = tk.Frame(win, padx=10, pady=10)
        control_frame.pack(fill=tk.X)
        
        tk.Label(control_frame, text="ชื่อเมนู:", font=self.thai_font).grid(row=0, column=0, sticky="w", pady=5)
        entry_name = tk.Entry(control_frame, font=self.thai_font, width=30)
        entry_name.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(control_frame, text="ราคา:", font=self.thai_font).grid(row=1, column=0, sticky="w", pady=5)
        entry_price = tk.Entry(control_frame, font=self.thai_font, width=30)
        entry_price.grid(row=1, column=1, pady=5, padx=5)

        def save_menu():
            name = entry_name.get().strip()
            if not name: return
            try:
                price = int(entry_price.get())
                
                # ตรวจสอบว่ามีเมนูนี้อยู่แล้วหรือไม่
                menu_items = self.db.get_all_menu_items()
                if name in menu_items:
                    # แก้ไขเมนูเดิม
                    self.db.update_menu_item(name, name, price)
                else:
                    # เพิ่มเมนูใหม่
                    self.db.add_menu_item(name, price)
                
                load_menu_list()
                self.refresh_menu_buttons()
                entry_name.delete(0, tk.END)
                entry_price.delete(0, tk.END)
                messagebox.showinfo("สำเร็จ", "บันทึกเมนูเรียบร้อย")
            except ValueError:
                messagebox.showerror("ข้อผิดพลาด", "ราคาต้องเป็นตัวเลข")

        def delete_menu():
            name = entry_name.get().strip()
            if name:
                if messagebox.askyesno("ยืนยัน", f"ลบเมนู {name}?"):
                    if self.db.delete_menu_item(name):
                        load_menu_list()
                        self.refresh_menu_buttons()
                        entry_name.delete(0, tk.END)
                        entry_price.delete(0, tk.END)
                        messagebox.showinfo("สำเร็จ", "ลบเมนูเรียบร้อย")

        tk.Button(control_frame, text="บันทึก / เพิ่มใหม่", command=save_menu, 
                 bg="#2ecc71", fg="white", font=self.thai_font_bold).grid(row=2, column=0, 
                 columnspan=2, sticky="ew", pady=5)
        tk.Button(control_frame, text="ลบเมนู", command=delete_menu, bg="#e74c3c", 
                 fg="white", font=self.thai_font_bold).grid(row=3, column=0, 
                 columnspan=2, sticky="ew")

    # --- Billing & Checkout Functions ---
    def add_item_to_bill(self, name, price):
        if not self.current_table:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกหรือสร้างโต๊ะก่อน")
            return
        
        # เพิ่มลงฐานข้อมูล
        if self.db.add_order_item(self.current_table, name, price):
            # โหลดออเดอร์ใหม่จากฐานข้อมูล
            self.tables[self.current_table] = self.db.get_table_orders(self.current_table)
            self.update_bill_view()
            self.refresh_table_buttons()

    def remove_item_from_bill(self):
        selection = self.bill_list.curselection()
        if selection:
            idx = selection[0]
            order = self.tables[self.current_table][idx]
            
            # ลบจากฐานข้อมูล
            if self.db.delete_order_item(order['id']):
                # โหลดออเดอร์ใหม่
                self.tables[self.current_table] = self.db.get_table_orders(self.current_table)
                self.update_bill_view()
                self.refresh_table_buttons()

    def update_bill_view(self):
        self.bill_list.delete(0, tk.END)
        total = 0
        if self.current_table in self.tables:
            for item in self.tables[self.current_table]:
                name_display = f"{item['name']}"
                price_display = f"{item['price']}"
                space = 35 - len(name_display) - len(price_display) 
                if space < 1: space = 1
                
                self.bill_list.insert(tk.END, f"{name_display}{' '*space}{price_display}")
                total += item['price']
        self.lbl_total.config(text=f"รวม: {total} บาท")

    def generate_receipt_text(self, table_name, items, total, timestamp, bill_id):
        text = "========= เพลิดเพลินชาบู =========\n"
        text += "       ใบเสร็จรับเงิน (Receipt)\n"
        text += f"Bill ID: {bill_id}\n"
        text += f"วันที่: {timestamp}\n"
        text += f"โต๊ะ: {table_name}\n"
        text += "--------------------------------\n"
        for item in items:
            text += f"{item['name']:<20} {item['price']:>5}\n"
        text += "--------------------------------\n"
        text += f"ยอดสุทธิ:           {total:>5} บาท\n"
        text += "================================"
        return text

    def checkout(self):
        if not self.current_table or not self.tables[self.current_table]:
            return

        items = self.tables[self.current_table]
        total = sum(i['price'] for i in items)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # สร้าง bill_id
        sales_count = len(self.db.get_all_sales())
        bill_id = f"S-{sales_count + 1:05d}"

        # บันทึกลงฐานข้อมูล
        if self.db.add_sale(bill_id, self.current_table, items, total):
            # ล้างออเดอร์ของโต๊ะนี้
            self.db.clear_table_orders(self.current_table)
            
            # แสดงใบเสร็จ
            receipt_text = self.generate_receipt_text(self.current_table, items, total, timestamp, bill_id)
            messagebox.showinfo("ใบเสร็จ - เพลิดเพลินชาบู", receipt_text)

            # อัปเดต UI
            self.tables[self.current_table] = []
            self.update_bill_view()
            self.refresh_table_buttons()
        else:
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถบันทึกการขายได้")

    # --- History Functions with SEARCH capability ---
    def open_history_window(self):
        win = Toplevel(self.root)
        win.title("ประวัติการขาย - เพลิดเพลินชาบู")
        win.geometry("900x650")

        # Search Frame
        search_frame = tk.Frame(win, bg="#ecf0f1", padx=10, pady=10)
        search_frame.pack(fill=tk.X)
        
        tk.Label(search_frame, text="🔍 ค้นหา:", font=self.thai_font_bold, 
                bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        
        search_entry = tk.Entry(search_frame, font=self.thai_font, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_type = tk.StringVar(value="all")
        search_options = [("ทั้งหมด", "all"), ("Bill ID", "bill_id"), 
                         ("โต๊ะ", "table"), ("วันที่", "date"), ("ยอดรวม", "total")]
        
        tk.Label(search_frame, text="ค้นหาจาก:", font=self.thai_font, 
                bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        
        search_combo = ttk.Combobox(search_frame, textvariable=search_type, 
                                   values=[opt[0] for opt in search_options], 
                                   state="readonly", font=self.thai_font, width=15)
        search_combo.pack(side=tk.LEFT, padx=5)

        # Treeview
        columns = ("id", "time", "table", "total")
        tree = ttk.Treeview(win, columns=columns, show="headings", height=20)
        tree.heading("id", text="Bill ID")
        tree.heading("time", text="เวลา")
        tree.heading("table", text="โต๊ะ")
        tree.heading("total", text="ยอดรวม (บาท)")
        
        tree.column("id", width=120, anchor="center")
        tree.column("time", width=180, anchor="center")
        tree.column("table", width=100, anchor="center")
        tree.column("total", width=120, anchor="e")
        
        scrollbar = ttk.Scrollbar(win, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def refresh_tree(search_text=""):
            for item in tree.get_children():
                tree.delete(item)
            
            # แปลงประเภทการค้นหา
            search_field_map = {opt[0]: opt[1] for opt in search_options}
            field = search_field_map.get(search_type.get(), "all")
            
            # ค้นหาจากฐานข้อมูล
            if search_text:
                sales = self.db.search_sales(search_text, field)
            else:
                sales = self.db.get_all_sales()
            
            for sale in sales:
                tree.insert("", tk.END, values=(sale['id'], sale['timestamp'], 
                                               sale['table'], sale['total']))

        def on_search(*args):
            refresh_tree(search_entry.get())

        search_entry.bind("<KeyRelease>", on_search)
        search_combo.bind("<<ComboboxSelected>>", on_search)
        
        tk.Button(search_frame, text="ค้นหา", command=on_search, bg="#3498db", 
                 fg="white", font=self.thai_font_bold).pack(side=tk.LEFT, padx=5)
        
        def clear_search():
            search_entry.delete(0, tk.END)
            search_type.set("all")
            refresh_tree()
        
        tk.Button(search_frame, text="ล้าง", command=clear_search, bg="#95a5a6", 
                 fg="white", font=self.thai_font_bold).pack(side=tk.LEFT, padx=5)

        refresh_tree()

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill=tk.X, pady=10)

        def reprint_receipt():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("เตือน", "กรุณาเลือกรายการเพื่อพิมพ์ใบเสร็จ")
                return
            
            item_values = tree.item(selected_item, "values")
            bill_id = item_values[0]
            
            # ดึงข้อมูลจากฐานข้อมูล
            sale = self.db.get_sale_details(bill_id)
            if sale:
                text = self.generate_receipt_text(sale['table'], sale['items'], 
                                                 sale['total'], sale['timestamp'], 
                                                 sale['id'])
                messagebox.showinfo(f"ใบเสร็จย้อนหลัง ({bill_id})", text)

        def delete_selected_history():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("เตือน", "กรุณาเลือกรายการที่จะลบ")
                return
            
            item_values = tree.item(selected_item, "values")
            bill_id = item_values[0]

            if messagebox.askyesno("ยืนยัน", f"ต้องการลบประวัติบิล {bill_id} ใช่หรือไม่?"):
                if self.db.delete_sale(bill_id):
                    refresh_tree(search_entry.get())
                    messagebox.showinfo("สำเร็จ", f"ลบบิล {bill_id} เรียบร้อยแล้ว")

        def delete_all_history():
            if messagebox.askyesno("ยืนยัน", "ต้องการล้างประวัติทั้งหมด (กู้คืนไม่ได้)?"):
                if self.db.clear_all_sales():
                    refresh_tree()
                    messagebox.showinfo("สำเร็จ", "ล้างประวัติทั้งหมดเรียบร้อยแล้ว")

        tk.Button(btn_frame, text="🖨️ พิมพ์ใบเสร็จย้อนหลัง", command=reprint_receipt, 
                 bg="#3498db", fg="white", font=self.thai_font_bold).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ ลบรายการที่เลือก", command=delete_selected_history, 
                 bg="#e67e22", fg="white", font=self.thai_font_bold).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="🗑️ ล้างประวัติทั้งหมด", command=delete_all_history, 
                 bg="#c0392b", fg="white", font=self.thai_font_bold).pack(side=tk.RIGHT, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShabuPOS(root)
    root.mainloop()
