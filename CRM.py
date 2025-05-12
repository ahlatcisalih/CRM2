import uuid
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from tkinter.font import Font

# Stil sabitleri
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

class ModernCRMApp:
    def __init__(self, crm):
        self.crm = crm
        self.root = tk.Tk()
        self.root.title("Modern CRM Sistemi")
        self.root.geometry("1000x600")
        self.root.configure(bg=BG_COLOR)
        
        # Yazı tipleri
        self.title_font = Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = Font(family="Helvetica", size=10)
        
        self.create_widgets()
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Sol panel (Butonlar)
        left_panel = ttk.Frame(main_frame, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Sağ panel (İçerik)
        self.content_area = ttk.Frame(main_frame)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Butonlar
        buttons = [
            ("Müşteri Ekle", self.musteri_ekle),
            ("Müşteri Listesi", self.show_musteri_listesi),
            ("Satış Ekle", self.satis_ekle),
            ("Destek Talebi", self.destek_ekle),
            ("Müşteri Güncelle", self.musteri_guncelle),
            ("Raporlar", self.show_raporlar),
            ("Verileri Kaydet", self.crm.verileri_kaydet)
        ]

        for text, command in buttons:
            btn = tk.Button(left_panel, text=text, command=command, **BUTTON_STYLE)
            btn.pack(fill=tk.X, pady=2)

        # Müşteri Listesi Tablosu
        self.create_liste_tablosu()
        
        
    def create_liste_tablosu(self):
        # Treeview için çerçeve
        table_frame = ttk.Frame(self.content_area)
        self.table_frame = table_frame 
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Tablo
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Ad", "Soyad", "Telefon", "Email", "Satış", "Destek"),
            yscrollcommand=scroll_y.set,
            selectmode="browse"
        )
        scroll_y.config(command=self.tree.yview)

        # Sütunlar
        self.tree.heading("#0", text="No")
        self.tree.column("#0", width=50, stretch=tk.NO)
        self.tree.heading("ID", text="Müşteri ID")
        self.tree.heading("Ad", text="Ad")
        self.tree.heading("Soyad", text="Soyad")
        self.tree.heading("Telefon", text="Telefon")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Satış", text="Satış Sayısı")
        self.tree.heading("Destek", text="Destek Talebi")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.update_table()

    def update_table(self):
        # Tabloyu güncelle
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for i, musteri in enumerate(self.crm.musteriler.values(), 1):
            self.tree.insert("", "end", text=str(i), values=(
                musteri.musteri_id,
                musteri.ad,
                musteri.soyad,
                musteri.telefon,
                musteri.email,
                len(musteri.satislar),
                len(musteri.destek_talepleri)
            ))

    def musteri_ekle(self):
        self.clear_content()
        form_frame = ttk.Frame(self.content_area)
        form_frame.pack(pady=20)

        labels = ["Ad:", "Soyad:", "Telefon:", "Email:"]
        entries = []
        
        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        def save():
            values = [e.get() for e in entries]
            if all(values):
                self.crm.musteri_ekle(*values)
                self.update_table()
                messagebox.showinfo("Başarılı", "Müşteri eklendi!")
                self.show_musteri_listesi()
            else:
                messagebox.showerror("Hata", "Tüm alanları doldurun!")

        ttk.Button(form_frame, text="Kaydet", command=save).grid(row=4, columnspan=2, pady=10)

    def show_musteri_listesi(self):
        self.clear_content()
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        self.update_table()

    def satis_ekle(self):
        self.clear_content()
        musteri_id = self.get_selected_musteri_id()
        if not musteri_id:
            return

        form_frame = ttk.Frame(self.content_area)
        form_frame.pack(pady=20)

        labels = ["Ürün Adı:", "Miktar:", "Toplam Tutar:"]
        entries = []
        
        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        def save():
            try:
                urun = entries[0].get()
                miktar = int(entries[1].get())
                tutar = float(entries[2].get())
                musteri = self.crm.musteri_getir(musteri_id)
                musteri.satis_ekle(urun, miktar, tutar)
                self.update_table()
                messagebox.showinfo("Başarılı", "Satış eklendi!")
                self.show_musteri_listesi()
            except ValueError:
                messagebox.showerror("Hata", "Geçersiz değer!")

        ttk.Button(form_frame, text="Kaydet", command=save).grid(row=3, columnspan=2, pady=10)

    def destek_ekle(self):
        self.clear_content()
        musteri_id = self.get_selected_musteri_id()
        if not musteri_id:
            return

        form_frame = ttk.Frame(self.content_area)
        form_frame.pack(pady=20)

        ttk.Label(form_frame, text="Konu:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        konu_entry = ttk.Entry(form_frame, width=30)
        konu_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="Açıklama:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        aciklama_entry = tk.Text(form_frame, width=30, height=4)
        aciklama_entry.grid(row=1, column=1, padx=10, pady=5)

        def save():
            konu = konu_entry.get()
            aciklama = aciklama_entry.get("1.0", tk.END).strip()
            if konu and aciklama:
                musteri = self.crm.musteri_getir(musteri_id)
                musteri.destek_talebi_olustur(konu, aciklama)
                self.update_table()
                messagebox.showinfo("Başarılı", "Destek talebi eklendi!")
                self.show_musteri_listesi()
            else:
                messagebox.showerror("Hata", "Tüm alanları doldurun!")

        ttk.Button(form_frame, text="Kaydet", command=save).grid(row=2, columnspan=2, pady=10)

    def show_raporlar(self):
        self.clear_content()
        report_frame = ttk.Frame(self.content_area)
        report_frame.pack(pady=20)

        # Toplam Satış
        ttk.Label(report_frame, text="Toplam Satış Tutarı:", font=self.title_font).grid(row=0, column=0, padx=10, pady=5)
        total_sales = self.crm.toplam_satis_tutar()
        ttk.Label(report_frame, text=f"{total_sales} ₺", font=self.normal_font).grid(row=0, column=1, padx=10, pady=5)

        # En Çok Satış Yapan
        ttk.Label(report_frame, text="En Çok Satış Yapan:", font=self.title_font).grid(row=1, column=0, padx=10, pady=5)
        best_customer = self.crm.en_cok_satis_yapan()
        best_text = f"{best_customer.ad} {best_customer.soyad} - {sum(s.toplam_tutar for s in best_customer.satislar)} ₺" if best_customer else "Kayıt yok"
        ttk.Label(report_frame, text=best_text, font=self.normal_font).grid(row=1, column=1, padx=10, pady=5)

    def get_selected_musteri_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Hata", "Lütfen bir müşteri seçin!")
            return None
        return self.tree.item(selection[0])['values'][0]

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            if widget != self.table_frame:
                widget.destroy()
    # Tabloyu gizler
        self.table_frame.pack_forget()

    def musteri_guncelle(self):
        musteri_id = self.get_selected_musteri_id()
        if not musteri_id:
            return

        musteri = self.crm.musteri_getir(musteri_id)
        self.clear_content()
        form_frame = ttk.Frame(self.content_area)
        form_frame.pack(pady=20)

        labels = ["Ad:", "Soyad:", "Telefon:", "Email:"]
        entries = []
        initial_values = [musteri.ad, musteri.soyad, musteri.telefon, musteri.email]
        
        for i, (label, value) in enumerate(zip(labels, initial_values)):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry = ttk.Entry(form_frame, width=30)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        def save():
            new_values = [e.get() for e in entries]
            musteri.musteri_guncelle(*new_values)
            self.update_table()
            messagebox.showinfo("Başarılı", "Bilgiler güncellendi!")
            self.show_musteri_listesi()

        ttk.Button(form_frame, text="Kaydet", command=save).grid(row=4, columnspan=2, pady=10)

    def run(self):
        self.root.mainloop()

class CRM:
    def __init__(self):
        self.musteriler = {}

    def musteri_ekle(self, ad, soyad, telefon, email):
        musteri = Musteri(ad, soyad, telefon, email)
        self.musteriler[musteri.musteri_id] = musteri
        return musteri.musteri_id

    def musteri_getir(self, musteri_id):
        return self.musteriler.get(musteri_id)

    def musteri_listele(self):
        return [m.to_dict() for m in self.musteriler.values()]

    def toplam_satis_tutar(self):
        return sum(s.toplam_tutar for m in self.musteriler.values() for s in m.satislar)

    def en_cok_satis_yapan(self):
        if not self.musteriler:
            return None
        return max(self.musteriler.values(), key=lambda m: sum(s.toplam_tutar for s in m.satislar), default=None)

    def verileri_kaydet(self, dosya="veriler.json"):
        try:
            with open(dosya, "w", encoding="utf-8") as f:
                # Müşteri listesini dict formatına çevir
                kayit_listesi = [m.to_dict() for m in self.musteriler.values()]
                json.dump(kayit_listesi, f, indent=2, ensure_ascii=False)
            print(f"Veriler {dosya} dosyasına kaydedildi")  # Debug için
            return True
        except Exception as e:
            messagebox.showerror("Kayıt Hatası", f"Dosya yazma hatası: {str(e)}")
            return False


    def verileri_yukle(self, dosya="veriler.json"):
        try:
            with open(dosya, "r", encoding="utf-8") as f:
                data = json.load(f)
                for m in data:
                    musteri = Musteri(m['ad'], m['soyad'], m['telefon'], m['email'])
                    musteri.musteri_id = m['musteri_id']
                    for s in m['satislar']:
                        musteri.satislar.append(Satis(s['urun'], s['miktar'], s['toplam_tutar']))
                    for d in m['destek_talepleri']:
                        destek = DestekTalebi(d['konu'], d['aciklama'])
                        destek.tarih = d['tarih']
                        destek.durum = d['durum']
                        destek.talep_id = d['talep_id']
                        musteri.destek_talepleri.append(destek)
                    self.musteriler[musteri.musteri_id] = musteri
        except FileNotFoundError:
            pass

# DİĞER GEREKLİ SINIFLAR
class Satis:
    def __init__(self, urun, miktar, toplam_tutar):
        self.satis_id = str(uuid.uuid4())
        self.tarih = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.urun = urun
        self.miktar = miktar
        self.toplam_tutar = toplam_tutar

    def to_dict(self):
        return self.__dict__

class DestekTalebi:
    def __init__(self, konu, aciklama):
        self.talep_id = str(uuid.uuid4())
        self.konu = konu
        self.aciklama = aciklama
        self.tarih = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.durum = "Açık"

    def to_dict(self):
        return self.__dict__

class Musteri:
    def __init__(self, ad, soyad, telefon, email):
        self.musteri_id = str(uuid.uuid4())
        self.ad = ad
        self.soyad = soyad
        self.telefon = telefon
        self.email = email
        self.satislar = []
        self.destek_talepleri = []

    def musteri_bilgilerini_goster(self):
        return f"{self.ad} {self.soyad} | Tel: {self.telefon} | Email: {self.email}"

    def satis_ekle(self, urun, miktar, toplam_tutar):
        satis = Satis(urun, miktar, toplam_tutar)
        self.satislar.append(satis)

    def destek_talebi_olustur(self, konu, aciklama):
        talep = DestekTalebi(konu, aciklama)
        self.destek_talepleri.append(talep)

    def musteri_guncelle(self, ad=None, soyad=None, telefon=None, email=None):
        if ad: self.ad = ad
        if soyad: self.soyad = soyad
        if telefon: self.telefon = telefon
        if email: self.email = email

    def to_dict(self):
        return {
            "musteri_id": self.musteri_id,
            "ad": self.ad,
            "soyad": self.soyad,
            "telefon": self.telefon,
            "email": self.email,
            "satislar": [s.to_dict() for s in self.satislar],
            "destek_talepleri": [d.to_dict() for d in self.destek_talepleri]
        }

if __name__ == "__main__":
    sistem = CRM()
    sistem.verileri_yukle()

    if not sistem.musteriler:
        mid = sistem.musteri_ekle("Ayşe", "Çelik", "05005556677", "ayse@example.com")
        m = sistem.musteri_getir(mid)
        m.satis_ekle("Telefon", 1, 12000)
        m.destek_talebi_olustur("Teslimat", "Kargo ne zaman gelir?")

    app = ModernCRMApp(sistem)
    app.run()