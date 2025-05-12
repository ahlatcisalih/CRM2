import uuid
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

# Style constants
BG_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#3498db"
BUTTON_STYLE = {
    "bg": PRIMARY_COLOR,
    "fg": "white",
    "activebackground": SECONDARY_COLOR,
    "padx": 15,
    "pady": 8,
    "borderwidth": 0,
    "font": ("Helvetica", 10)
}

# Data Model Classes
class Instrument:
    def __init__(self, name, stock):
        self.instrument_id = str(uuid.uuid4())
        self.name = name
        self.stock = stock

    def sell(self, quantity):
        if quantity > self.stock:
            raise ValueError("Yetersiz stok")
        self.stock -= quantity

    def to_dict(self):
        return {"instrument_id": self.instrument_id, "name": self.name, "stock": self.stock}

class Customer:
    def __init__(self, first_name, last_name, phone, email):
        self.customer_id = str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.orders = []
        self.supports = []

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "email": self.email,
            "orders": [order.to_dict() for order in self.orders],
            "supports": [sup.to_dict() for sup in self.supports]
        }

class Sale:
    def __init__(self, customer_id, items):  # items: list of (instrument, qty, price)
        self.sale_id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.items = items  # tuple list
        self.total = sum(qty * price for _, qty, price in items)

    def to_dict(self):
        return {"sale_id": self.sale_id, "customer_id": self.customer_id,
                "date": self.date, "items": [
                    {"instrument_id": inst.instrument_id, "qty": qty, "price": price}
                    for inst, qty, price in self.items
                ], "total": self.total}

class SupportRequest:
    def __init__(self, customer_id, subject, message):
        self.request_id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.subject = subject
        self.message = message
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.status = "Open"

    def to_dict(self):
        return {"request_id": self.request_id, "customer_id": self.customer_id,
                "subject": self.subject, "message": self.message,
                "date": self.date, "status": self.status}

class StoreManager:
    def __init__(self):
        self.instruments = {}
        self.customers = {}
        self.sales = {}
        self.supports = {}
        self.content = None
        self.clear_content = None

    # Instrument methods
    def add_instrument(self, name, stock):
        inst = Instrument(name, stock)
        self.instruments[inst.instrument_id] = inst
        return inst

    def list_instruments(self):
        return list(self.instruments.values())

    # Customer methods
    def add_customer(self, first, last, phone, email):
        cust = Customer(first, last, phone, email)
        self.customers[cust.customer_id] = cust
        return cust

    def list_customers(self):
        return list(self.customers.values())

    # Sale
    def create_sale(self, customer_id, items):
        # reduce stock
        for inst, qty, price in items:
            inst.sell(qty)
        sale = Sale(customer_id, items)
        self.sales[sale.sale_id] = sale
        self.customers[customer_id].orders.append(sale)
        return sale

    # Support
    def create_support(self, customer_id, subject, message):
        sup = SupportRequest(customer_id, subject, message)
        self.supports[sup.request_id] = sup
        self.customers[customer_id].supports.append(sup)
        return sup

    # Persistence
    def save_data(self, filename="store_data.json"):
        data = {
            "instruments": [i.to_dict() for i in self.instruments.values()],
            "customers": [c.to_dict() for c in self.customers.values()],
            "sales": [s.to_dict() for s in self.sales.values()],
            "supports": [sp.to_dict() for sp in self.supports.values()]
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self, filename="store_data.json"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            # load instruments
            for m in data.get("instruments", []):
                inst = Instrument(m['name'], m['stock'])
                inst.instrument_id = m['instrument_id']
                self.instruments[inst.instrument_id] = inst
            # load customers
            for m in data.get("customers", []):
                cust = Customer(m['first_name'], m['last_name'], m['phone'], m['email'])
                cust.customer_id = m['customer_id']
                self.customers[cust.customer_id] = cust
            # sales & supports skip detailed reload for brevity
        except FileNotFoundError:
            pass
    
    def sale_ui(self):                          
        self.clear_content()
        frm = ttk.Frame(self.content)
        frm.pack(pady=20)
        # Müşteri seçimi
        ttk.Label(frm, text="Müşteri:").grid(row=0, column=0, pady=5, sticky=tk.W)
        cust_cb = ttk.Combobox(frm, values=[
            f"{c.first_name} {c.last_name}|{c.customer_id}" 
            for c in self.list_customers()])
        cust_cb.grid(row=0, column=1, padx=5)

        # Enstrüman seçimi
        ttk.Label(frm, text="Enstrüman:").grid(row=1, column=0, pady=5, sticky=tk.W)
        inst_cb = ttk.Combobox(frm, values=[
            f"{i.name}|{i.instrument_id}" 
            for i in self.list_instruments()])
        inst_cb.grid(row=1, column=1, padx=5)

        # Miktar ve fiyat
        ttk.Label(frm, text="Miktar:").grid(row=2, column=0, pady=5, sticky=tk.W)
        qty_e = ttk.Entry(frm); qty_e.grid(row=2, column=1, padx=5)
        ttk.Label(frm, text="Birim Fiyat:").grid(row=3, column=0, pady=5, sticky=tk.W)
        price_e = ttk.Entry(frm); price_e.grid(row=3, column=1, padx=5)
        def save_sale():
            try:
                cust_id = cust_cb.get().split("|")[1]
                inst_id = inst_cb.get().split("|")[1]
                qty = int(qty_e.get())
                price = float(price_e.get())
                inst = self.instruments[inst_id]
                sale = self.create_sale(cust_id, [(inst, qty, price)])
                messagebox.showinfo("Başarılı", f"Satış kaydedildi: {sale.total} ₺")
            except IndexError:
                messagebox.showerror("Hata", "Lütfen müşteri/enstrüman seçin!")
            except KeyError:
                messagebox.showerror("Hata", "Geçersiz enstrüman ID'si!")
            except ValueError as e:
                messagebox.showerror("Hata", str(e))
        ttk.Button(frm, text="Satışı Kaydet", command=save_sale).grid(row=4, columnspan=2, pady=10)

    def support_ui(self):                       
        self.clear_content()
        frm = ttk.Frame(self.content)
        frm.pack(pady=20)
        # Müşteri
        ttk.Label(frm, text="Müşteri:").grid(row=0, column=0, pady=5, sticky=tk.W)
        cust_cb = ttk.Combobox(frm, values=[f"{c.first_name} {c.last_name}|{c.customer_id}" 
                                            for c in self.list_customers()])
        cust_cb.grid(row=0, column=1, padx=5)
        # Konu ve mesaj
        ttk.Label(frm, text="Konu:").grid(row=1, column=0, pady=5, sticky=tk.W)
        subj_e = ttk.Entry(frm); subj_e.grid(row=1, column=1, padx=5)
        ttk.Label(frm, text="Mesaj:").grid(row=2, column=0, pady=5, sticky=tk.W)
        msg_e = tk.Text(frm, width=30, height=4); msg_e.grid(row=2, column=1, padx=5)
        def save_support():
            cust_id = cust_cb.get().split("|")[1]
            subject = subj_e.get()
            message = msg_e.get("1.0", tk.END).strip()
            if not (cust_id and subject and message):
                messagebox.showerror("Hata", "Tüm alanları doldurun")
                return
            sup = self.create_support(cust_id, subject, message)
            messagebox.showinfo("Başarılı", f"Talep oluşturuldu: {sup.request_id}")
        ttk.Button(frm, text="Talebi Kaydet", command=save_support).grid(row=3, columnspan=2, pady=10)


# GUI Application
class InstrumentStoreApp:
    def __init__(self, manager: StoreManager):
        self.manager = manager
        self.root = tk.Tk()
        self.root.title("Müzik Enstrüman Dükkanı Yönetimi")
        self.root.geometry("900x550")
        self.root.configure(bg=BG_COLOR)

        # Fonts
        self.title_font = Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = Font(family="Helvetica", size=10)

        self.create_widgets()
        self.center_window()

        self.manager.content = self.content
        self.manager.clear_content = self.clear_content

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        left = ttk.Frame(main, width=200)
        left.pack(side=tk.LEFT, fill=tk.Y)
        self.content = ttk.Frame(main)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Buttons
        buttons = [
            ("Enstrüman Ekle", self.add_instrument_ui),
            ("Stok Listesi", self.show_instruments),
            ("Müşteri Ekle", self.add_customer_ui),
            ("Müşteri Listesi", self.show_customers),
            ("Satış Yap", self.sale_ui),
            ("Destek Talebi", self.support_ui),
            ("Verileri Kaydet", lambda: self.manager.save_data())
        ]
        for txt, cmd in buttons:
            btn = tk.Button(left, text=txt, command=cmd, **BUTTON_STYLE)
            btn.pack(fill=tk.X, pady=3)

        # Table frame placeholder
        self.table_frame = ttk.Frame(self.content)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()
        self.table_frame = ttk.Frame(self.content)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

    def show_instruments(self):
        self.clear_content()
        cols = ("ID", "Ad", "Stok")
        tree = ttk.Treeview(self.table_frame, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
        for inst in self.manager.list_instruments():
            tree.insert('', 'end', values=(inst.instrument_id, inst.name, inst.stock))
        tree.pack(fill=tk.BOTH, expand=True)

    def show_customers(self):
        self.clear_content()
        cols = ("ID", "Ad Soyad", "Telefon", "Email")
        tree = ttk.Treeview(self.table_frame, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
        for cust in self.manager.list_customers():
            name = f"{cust.first_name} {cust.last_name}"
            tree.insert('', 'end', values=(cust.customer_id, name, cust.phone, cust.email))
        tree.pack(fill=tk.BOTH, expand=True)

    def add_instrument_ui(self):
        self.clear_content()
        frm = ttk.Frame(self.content)
        frm.pack(pady=20)
        ttk.Label(frm, text="Enstrüman Adı:").grid(row=0, column=0, pady=5)
        name_e = ttk.Entry(frm)
        name_e.grid(row=0, column=1, padx=5)
        ttk.Label(frm, text="Stok:").grid(row=1, column=0, pady=5)
        stk_e = ttk.Entry(frm)
        stk_e.grid(row=1, column=1, padx=5)

        def save():
            try:
                name = name_e.get()
                stk = int(stk_e.get())
                self.manager.add_instrument(name, stk)
                messagebox.showinfo("Başarılı", "Enstrüman eklendi")
            except ValueError:
                messagebox.showerror("Hata", "Geçersiz stok değeri")
        ttk.Button(frm, text="Kaydet", command=save).grid(row=2, columnspan=2, pady=10)

    def add_customer_ui(self):
        self.clear_content()
        frm = ttk.Frame(self.content)
        frm.pack(pady=20)
        labels = ["Ad:", "Soyad:", "Telefon:", "Email:"]
        entries = []
        for i, lbl in enumerate(labels):
            ttk.Label(frm, text=lbl).grid(row=i, column=0, pady=5)
            e = ttk.Entry(frm)
            e.grid(row=i, column=1, padx=5)
            entries.append(e)
        def save():
            vals = [e.get() for e in entries]
            if all(vals):
                self.manager.add_customer(*vals)
                messagebox.showinfo("Başarılı", "Müşteri eklendi")
            else:
                messagebox.showerror("Hata", "Tüm alanları doldurun")
        ttk.Button(frm, text="Kaydet", command=save).grid(row=4, columnspan=2, pady=10)

    def sale_ui(self):
        self.manager.sale_ui()

    def support_ui(self):
        self.manager.support_ui()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    mgr = StoreManager()
    mgr.load_data()
    app = InstrumentStoreApp(mgr)
    app.run()
