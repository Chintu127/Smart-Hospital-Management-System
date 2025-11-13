import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import uuid
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class BillingModule:
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        
        self.create_widgets()
        self.load_bills()
    
    def create_widgets(self):
     # Title Bar
     title_frame = tk.Frame(self.parent, bg='white')
     title_frame.pack(fill='x', padx=20, pady=20)

     tk.Label(title_frame, text="💰 Billing Management",
           font=('Arial', 20, 'bold'),
           bg='white', fg='#2c3e50').pack(side='left')

     # Action Buttons
     btn_frame = tk.Frame(title_frame, bg='white')
     btn_frame.pack(side='right')

     tk.Button(btn_frame, text="📋 Patients", font=('Arial', 10, 'bold'),
            bg='#8e44ad', fg='white', relief='flat', cursor='hand2',
            command=self.show_patient_list, padx=12, pady=6).pack(side='left', padx=5)

     tk.Button(btn_frame, text="💊 Medicines", font=('Arial', 10, 'bold'),
            bg='#16a085', fg='white', relief='flat', cursor='hand2',
            command=self.show_medicine_catalog, padx=12, pady=6).pack(side='left', padx=5)

     tk.Button(btn_frame, text="📥 Export Meds", font=('Arial', 10, 'bold'),
            bg='#d35400', fg='white', relief='flat', cursor='hand2',
            command=self.export_medicines_csv, padx=12, pady=6).pack(side='left', padx=5)

     tk.Button(btn_frame, text="🕘 Recent Bills", font=('Arial', 10, 'bold'),
            bg='#34495e', fg='white', relief='flat', cursor='hand2',
            command=self.show_recent_bills, padx=12, pady=6).pack(side='left', padx=5)

     tk.Button(btn_frame, text="➕ New Bill",
            font=('Arial', 10, 'bold'),
            bg='#2ecc71', fg='white',
            relief='flat', cursor='hand2',
            command=self.create_new_bill,
            padx=15, pady=8).pack(side='left', padx=5)

     tk.Button(btn_frame, text="🔄 Refresh",
            font=('Arial', 10, 'bold'),
            bg='#3498db', fg='white',
            relief='flat', cursor='hand2',
            command=self.load_bills,
            padx=15, pady=8).pack(side='left', padx=5)

     # Search Bar
     search_frame = tk.Frame(self.parent, bg='white')
     search_frame.pack(fill='x', padx=20, pady=10)

     tk.Label(search_frame, text="🔍 Search:",
           font=('Arial', 11),
           bg='white').pack(side='left', padx=(0, 10))

     self.search_var = tk.StringVar()
     self.search_var.trace('w', lambda *args: self.search_bills())

     search_entry = tk.Entry(search_frame,
                    textvariable=self.search_var,
                    font=('Arial', 11),
                    width=40)
     search_entry.pack(side='left', ipady=5)

     # Filter Options
     filter_frame = tk.Frame(search_frame, bg='white')
     filter_frame.pack(side='right')

     tk.Label(filter_frame, text="Status:",
           font=('Arial', 11),
           bg='white').pack(side='left', padx=5)

     self.status_var = tk.StringVar(value="All")
     status_cb = ttk.Combobox(filter_frame,
                     textvariable=self.status_var,
                     values=["All", "Pending", "Paid", "Cancelled"],
                     width=10)
     status_cb.pack(side='left')
     status_cb.bind('<<ComboboxSelected>>', lambda e: self.search_bills())

     # Bills Table
     table_frame = tk.Frame(self.parent, bg='white')
     table_frame.pack(fill='both', expand=True, padx=20, pady=10)

     # Scrollbars
     y_scroll = tk.Scrollbar(table_frame, orient='vertical')
     y_scroll.pack(side='right', fill='y')

     x_scroll = tk.Scrollbar(table_frame, orient='horizontal')
     x_scroll.pack(side='bottom', fill='x')

     # Treeview
     columns = ('Bill No', 'Patient ID', 'Patient Name', 'Date', 'Services',
             'Subtotal', 'Tax', 'Total', 'Status', 'Payment Method')
     self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                    yscrollcommand=y_scroll.set,
                    xscrollcommand=x_scroll.set)

     y_scroll.config(command=self.tree.yview)
     x_scroll.config(command=self.tree.xview)

     # Define column headings
     for col in columns:
         self.tree.heading(col, text=col)
         self.tree.column(col, width=100, anchor='center')

     # Adjust specific column widths
     self.tree.column('Services', width=200)
     self.tree.column('Patient Name', width=150)

     self.tree.pack(fill='both', expand=True)

     # Bind events
     self.tree.bind('<Double-1>', self.view_bill)
     self.tree.bind('<Button-3>', self.show_context_menu)

     # Style
     style = ttk.Style()
     style.configure('Treeview', rowheight=30, font=('Arial', 10))
     style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def load_bills(self):
        """Load all bills into the table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        bills = self.data_manager.get_bills()
        for bill in bills:
            self.insert_bill_to_tree(bill)
    
    def insert_bill_to_tree(self, bill):
        """Insert a bill into the treeview"""
        values = (
            bill['bill_no'],
            bill['patient_id'],
            bill['patient_name'],
            bill['date'],
            bill['services'],
            f"₹{bill['subtotal']:.2f}",
            f"₹{bill['tax']:.2f}",
            f"₹{bill['total']:.2f}",
            bill['status'],
            bill.get('payment_method', 'N/A')
        )
        
        self.tree.insert('', 'end', values=values, tags=(bill['status'].lower(),))
    
    def search_bills(self):
        """Search bills by bill number or patient name"""
        search_term = self.search_var.get().lower()
        status_filter = self.status_var.get()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        bills = self.data_manager.get_bills()
        
        for bill in bills:
            if (search_term in bill['bill_no'].lower() or 
                search_term in bill['patient_name'].lower()):
                if status_filter == "All" or bill['status'] == status_filter:
                    self.insert_bill_to_tree(bill)
    
    def create_new_bill(self):
        """Open dialog to create new bill with item-level entry (item, qty, cost)"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Create New Bill")
        dialog.geometry("700x700")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f'700x700+{x}+{y}')

        form_frame = tk.Frame(dialog, padx=20, pady=10)
        form_frame.pack(fill='both', expand=True)

        tk.Label(form_frame, text="New Bill", font=('Arial', 16, 'bold')).pack(pady=10)

        bill_no = f"B{str(uuid.uuid4())[:8].upper()}"

        # Patient info
        pframe = tk.Frame(form_frame)
        pframe.pack(fill='x', pady=5)
        tk.Label(pframe, text="Patient ID:", width=12).pack(side='left')
        self.patient_id_entry = tk.Entry(pframe, width=20)
        self.patient_id_entry.pack(side='left', padx=5)
        tk.Label(pframe, text="Patient Name:", width=12).pack(side='left')
        self.patient_name_entry = tk.Entry(pframe, width=30)
        self.patient_name_entry.pack(side='left', padx=5)

        # Items entry
        items_frame = tk.LabelFrame(form_frame, text="Items", padx=10, pady=10)
        items_frame.pack(fill='both', expand=True, pady=10)

        item_entry_frame = tk.Frame(items_frame)
        item_entry_frame.pack(fill='x', pady=5)
        tk.Label(item_entry_frame, text="Item", width=20).pack(side='left')
        self.item_name_entry = tk.Entry(item_entry_frame, width=25)
        self.item_name_entry.pack(side='left', padx=5)
        tk.Label(item_entry_frame, text="Qty", width=5).pack(side='left')
        self.item_qty_entry = tk.Entry(item_entry_frame, width=5)
        self.item_qty_entry.insert(0, '1')
        self.item_qty_entry.pack(side='left', padx=5)
        tk.Label(item_entry_frame, text="Price (₹)", width=10).pack(side='left')
        self.item_price_entry = tk.Entry(item_entry_frame, width=10)
        self.item_price_entry.pack(side='left', padx=5)
        tk.Button(item_entry_frame, text="Add Item", command=self.add_item_to_list).pack(side='left', padx=5)

        # Items list
        cols = ('Item', 'Qty', 'Price', 'Total')
        self.items_tree = ttk.Treeview(items_frame, columns=cols, show='headings', height=6)
        for c in cols:
            self.items_tree.heading(c, text=c)
            self.items_tree.column(c, anchor='center')
        self.items_tree.pack(fill='both', expand=True, pady=5)

        # Remove item button
        tk.Button(items_frame, text="Remove Selected Item", command=self.remove_selected_item).pack(pady=5)

        # Amounts
        amt_frame = tk.Frame(form_frame)
        amt_frame.pack(fill='x', pady=10)
        tk.Label(amt_frame, text="Subtotal:", width=12).grid(row=0, column=0)
        self.subtotal_var = tk.StringVar(value="0.00")
        tk.Label(amt_frame, textvariable=self.subtotal_var).grid(row=0, column=1)
        tk.Label(amt_frame, text="Tax (10%):", width=12).grid(row=1, column=0)
        self.tax_var = tk.StringVar(value="0.00")
        tk.Label(amt_frame, textvariable=self.tax_var).grid(row=1, column=1)
        tk.Label(amt_frame, text="Total:", width=12).grid(row=2, column=0)
        self.total_var = tk.StringVar(value="0.00")
        tk.Label(amt_frame, textvariable=self.total_var).grid(row=2, column=1)

        # Payment method
        pay_frame = tk.Frame(form_frame)
        pay_frame.pack(fill='x', pady=10)
        tk.Label(pay_frame, text="Payment Method:", width=15).pack(side='left')
        self.payment_var = tk.StringVar(value='Cash')
        ttk.Combobox(pay_frame, textvariable=self.payment_var, values=['Cash', 'Card', 'UPI', 'Insurance'], width=20).pack(side='left', padx=5)

        tk.Label(pay_frame, text="Transaction ID:", width=12).pack(side='left', padx=5)
        self.txn_entry = tk.Entry(pay_frame, width=20)
        self.txn_entry.pack(side='left')

        # Action buttons: Process (simulates payment), Save, Print
        action_frame = tk.Frame(form_frame)
        action_frame.pack(fill='x', pady=15)

        def process_payment_local():
            if not self.items_tree.get_children():
                messagebox.showerror('Error', 'Add at least one item')
                return
            # compute totals
            self.recalculate_amounts()
            messagebox.showinfo('Processed', 'Payment processed locally. Click Save Bill to persist.')
            save_btn.config(state='normal')

        process_btn = tk.Button(action_frame, text='Process Payment', bg='#f39c12', fg='white', command=process_payment_local)
        process_btn.pack(side='left', padx=5)

        def save_bill_action():
            # validate patient
            pid = self.patient_id_entry.get().strip()
            pname = self.patient_name_entry.get().strip()
            if not pid or not pname:
                messagebox.showerror('Error', 'Enter patient ID and name')
                return
            if not self.items_tree.get_children():
                messagebox.showerror('Error', 'Add at least one item')
                return

            # build services string and amounts
            services = []
            for iid in self.items_tree.get_children():
                it, qty, price, total = self.items_tree.item(iid)['values']
                services.append(f"{it} x{qty} @ ₹{float(price):.2f}")

            subtotal = float(self.subtotal_var.get())
            tax = float(self.tax_var.get())
            total = float(self.total_var.get())

            bill = {
                'bill_no': bill_no,
                'patient_id': pid,
                'patient_name': pname,
                'services': ', '.join(services),
                'subtotal': subtotal,
                'tax': tax,
                'total': total,
                'payment_method': self.payment_var.get(),
                'transaction_id': self.txn_entry.get().strip(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'status': 'Paid'
            }

            # persist
            try:
                self.data_manager.add_bill(bill)
            except Exception as e:
                messagebox.showerror('Error', f'Unable to save bill: {e}')
                return

            messagebox.showinfo('Saved', f'Bill {bill_no} saved successfully')
            save_btn.config(state='disabled')
            print_btn.config(state='normal')
            self.load_bills()

        save_btn = tk.Button(action_frame, text='Save Bill', bg='#2ecc71', fg='white', command=save_bill_action)
        save_btn.pack(side='left', padx=5)
        save_btn.config(state='disabled')

        def print_preview_action():
            # create a preview window with bill details
            bills = self.data_manager.get_bills()
            bill = next((b for b in bills if b['bill_no'] == bill_no), None)
            if not bill:
                messagebox.showerror('Error', 'Bill not found. Save first.')
                return
            self.show_print_preview(bill)

        print_btn = tk.Button(action_frame, text='Print Bill', bg='#3498db', fg='white', command=print_preview_action)
        print_btn.pack(side='left', padx=5)
        print_btn.config(state='disabled')

        tk.Button(action_frame, text='Cancel', command=dialog.destroy, bg='#e74c3c', fg='white').pack(side='right', padx=5)
    
    def add_custom_service(self):
        """Add custom service to services list"""
        service = self.custom_service.get().strip()
        if service:
            if not service.endswith(')'):
                service += " - ₹0"
            self.services_listbox.insert('end', service)
            self.custom_service.delete(0, 'end')

    def add_item_to_list(self):
        """Add an item (name, qty, price) to the items tree"""
        name = self.item_name_entry.get().strip()
        try:
            qty = int(self.item_qty_entry.get())
        except:
            messagebox.showerror('Error', 'Invalid quantity')
            return
        try:
            price = float(self.item_price_entry.get())
        except:
            messagebox.showerror('Error', 'Invalid price')
            return

        total = qty * price
        self.items_tree.insert('', 'end', values=(name, qty, f"{price:.2f}", f"{total:.2f}"))
        self.item_name_entry.delete(0, 'end')
        self.item_qty_entry.delete(0, 'end')
        self.item_qty_entry.insert(0, '1')
        self.item_price_entry.delete(0, 'end')
        self.recalculate_amounts()

    # ----------------- Patient List and Medicine Catalog -----------------
    def show_patient_list(self):
        patients = self.data_manager.get_patients()
        dialog = tk.Toplevel(self.parent)
        dialog.title('Patients')
        dialog.geometry('600x400')
        dialog.transient(self.parent)

        header = tk.Frame(dialog)
        header.pack(fill='x', padx=10, pady=5)
        tk.Label(header, text=f'Total Patients: {len(patients)}', font=('Arial', 12, 'bold')).pack(side='left')

        cols = ('ID', 'Name', 'Age', 'Contact')
        tree = ttk.Treeview(dialog, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120)
        for p in patients:
            tree.insert('', 'end', values=(p.get('id'), p.get('name'), p.get('age', ''), p.get('contact', '')))
        tree.pack(fill='both', expand=True, padx=10, pady=5)

        def load_selected():
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0])['values']
            pid, name = vals[0], vals[1]
            # populate billing form fields if open
            try:
                self.patient_id_entry.delete(0, 'end')
                self.patient_id_entry.insert(0, pid)
                self.patient_name_entry.delete(0, 'end')
                self.patient_name_entry.insert(0, name)
            except Exception:
                pass
            dialog.destroy()

        tk.Button(dialog, text='Load Selected', command=load_selected, bg='#2ecc71', fg='white').pack(pady=5)

    def show_medicine_catalog(self):
        meds = self.data_manager.get_medicines()
        dialog = tk.Toplevel(self.parent)
        dialog.title('Medicine Catalog')
        dialog.geometry('800x500')
        dialog.transient(self.parent)

        cols = ('Med ID', 'Name', 'Unit Price', 'Stock')
        tree = ttk.Treeview(dialog, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150)
        for m in meds:
            tree.insert('', 'end', values=(m.get('id'), m.get('name'), f"₹{m.get('price',0):.2f}", m.get('stock',0)))
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        def add_med_to_bill():
            sel = tree.selection()
            if not sel:
                messagebox.showerror('Error', 'Select a medicine')
                return
            vals = tree.item(sel[0])['values']
            med_id, name, price, stock = vals
            # price is string like ₹xx.xx
            price = float(str(price).replace('₹',''))
            # Add to current bill items tree
            try:
                self.items_tree.insert('', 'end', values=(name, 1, f"{price:.2f}", f"{price:.2f}"))
                self.recalculate_amounts()
            except Exception:
                messagebox.showerror('Error', 'Open or create a bill first')

        tk.Button(dialog, text='Add to Bill', command=add_med_to_bill, bg='#16a085', fg='white').pack(pady=5)

    def export_medicines_csv(self):
        meds = self.data_manager.get_medicines()
        if not meds:
            messagebox.showinfo('Export', 'No medicines to export')
            return
        filepath = os.path.join(os.path.expanduser('~'), 'medicine_catalog.csv')
        try:
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['id','name','price','stock','category'])
                for m in meds:
                    w.writerow([m.get('id'), m.get('name'), m.get('price'), m.get('stock'), m.get('category')])
            messagebox.showinfo('Export', f'Medicine catalog exported to {filepath}')
        except Exception as e:
            messagebox.showerror('Error', f'Export failed: {e}')

    def show_recent_bills(self):
        bills = self.data_manager.get_bills()
        dialog = tk.Toplevel(self.parent)
        dialog.title('Recent Bills')
        dialog.geometry('800x400')
        dialog.transient(self.parent)

        cols = ('Date','Bill ID','Patient','Total')
        tree = ttk.Treeview(dialog, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=150)
        for b in sorted(bills, key=lambda x: x.get('date',''), reverse=True):
            tree.insert('', 'end', values=(b.get('date'), b.get('bill_no'), b.get('patient_name'), f"₹{b.get('total',0):.2f}"))
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        def view_bill():
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0])['values']
            bill_no = vals[1]
            bill = next((x for x in bills if x.get('bill_no')==bill_no), None)
            if bill:
                self.show_print_preview(bill)

        tk.Button(dialog, text='View / Print', command=view_bill, bg='#3498db', fg='white').pack(pady=5)

    def remove_selected_item(self):
        sel = self.items_tree.selection()
        for s in sel:
            self.items_tree.delete(s)
        self.recalculate_amounts()

    def recalculate_amounts(self):
        subtotal = 0.0
        for iid in self.items_tree.get_children():
            vals = self.items_tree.item(iid)['values']
            subtotal += float(vals[3])
        tax = subtotal * 0.10
        total = subtotal + tax
        self.subtotal_var.set(f"{subtotal:.2f}")
        self.tax_var.set(f"{tax:.2f}")
        self.total_var.set(f"{total:.2f}")

    def show_print_preview(self, bill):
        """Open a clean printable preview window; also allow PDF export"""
        preview = tk.Toplevel(self.parent)
        preview.title(f"Print Preview - {bill['bill_no']}")
        preview.geometry("600x700")
        preview.transient(self.parent)

        canvas_frame = tk.Frame(preview, padx=20, pady=20)
        canvas_frame.pack(fill='both', expand=True)

        # Header
        tk.Label(canvas_frame, text="SMART HOSPITAL", font=('Arial', 18, 'bold')).pack()
        tk.Label(canvas_frame, text=f"Bill No: {bill['bill_no']}", font=('Arial', 12)).pack()
        tk.Label(canvas_frame, text=f"Date: {bill['date']}", font=('Arial', 12)).pack()

        # Details
        details_frame = tk.Frame(canvas_frame)
        details_frame.pack(fill='both', expand=True, pady=10)

        tk.Label(details_frame, text=f"Patient: {bill['patient_name']} ({bill['patient_id']})", font=('Arial', 12)).pack(anchor='w')
        tk.Label(details_frame, text="Services:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(10,0))

        for s in bill['services'].split(','):
            tk.Label(details_frame, text=s.strip(), font=('Arial', 11)).pack(anchor='w')

        tk.Label(details_frame, text=f"Subtotal: ₹{bill['subtotal']:.2f}", font=('Arial', 12)).pack(anchor='e', pady=(10,0))
        tk.Label(details_frame, text=f"Tax: ₹{bill['tax']:.2f}", font=('Arial', 12)).pack(anchor='e')
        tk.Label(details_frame, text=f"Total: ₹{bill['total']:.2f}", font=('Arial', 14, 'bold')).pack(anchor='e', pady=(5,0))

        # Buttons
        btn_frame = tk.Frame(preview)
        btn_frame.pack(fill='x', pady=10)

        def export_pdf():
            filename = f"bill_{bill['bill_no']}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph('SMART HOSPITAL', styles['Title']))
            rows = [
                ['Bill No', bill['bill_no']],
                ['Date', bill['date']],
                ['Patient', f"{bill['patient_name']} ({bill['patient_id']})"],
            ]
            for s in bill['services'].split(','):
                rows.append(['Service', s.strip()])
            rows.append(['Subtotal', f"₹{bill['subtotal']:.2f}"])
            rows.append(['Tax', f"₹{bill['tax']:.2f}"])
            rows.append(['Total', f"₹{bill['total']:.2f}"])
            table = Table(rows, colWidths=[150, 350])
            table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ]))
            elements.append(table)
            doc.build(elements)
            try:
                if os.name == 'nt':
                    os.startfile(filename)
                else:
                    import subprocess
                    opener = 'xdg-open' if os.name == 'posix' else 'open'
                    subprocess.Popen([opener, filename])
            except Exception as e:
                messagebox.showerror('Error', f'Could not open PDF: {e}')

        tk.Button(btn_frame, text='Export PDF / Print', bg='#3498db', fg='white', command=export_pdf).pack(side='left', padx=10)
        tk.Button(btn_frame, text='Close', command=preview.destroy).pack(side='right', padx=10)
    
    def calculate_total(self):
        """Calculate bill total based on selected services"""
        selected_indices = self.services_listbox.curselection()
        
        subtotal = 0
        selected_services = []
        
        for index in selected_indices:
            service = self.services_listbox.get(index)
            price = float(service.split('$')[1].strip())
            subtotal += price
            selected_services.append(service.split(' - ')[0])
        
        tax = subtotal * 0.10  # 10% tax
        total = subtotal + tax
        
        self.subtotal_var.set(f"{subtotal:.2f}")
        self.tax_var.set(f"{tax:.2f}")
        self.total_var.set(f"{total:.2f}")
    
    def save_bill(self, bill_no, dialog):
        """Save new bill"""
        if not self.patient_var.get():
            messagebox.showerror("Error", "Please select a patient")
            return
        
        selected_services = [self.services_listbox.get(i) 
                           for i in self.services_listbox.curselection()]
        
        if not selected_services:
            messagebox.showerror("Error", "Please select services")
            return
        
        patient_id, patient_name = self.patient_var.get().split(' - ')
        
        new_bill = {
            'bill_no': bill_no,
            'patient_id': patient_id,
            'patient_name': patient_name,
            'services': ', '.join(s.split(' - ')[0] for s in selected_services),
            'subtotal': float(self.subtotal_var.get()),
            'tax': float(self.tax_var.get()),
            'total': float(self.total_var.get()),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'status': 'Pending'
        }
        
        
        # Close the bill creation dialog
        dialog.destroy()
        
        # Launch payment processor
        from payment_processor import PaymentProcessor
        PaymentProcessor(self.parent, new_bill, self.process_payment)
        
        self.data_manager.create_bill(new_bill, self.user['id'])
        self.load_bills()
        dialog.destroy()
        messagebox.showinfo("Success", "Bill created successfully!")
        
    def view_bill(self, event=None):
        """View bill details"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        bill_no = self.tree.item(selected_item[0])['values'][0]
        bills = self.data_manager.get_bills()
        bill = next((b for b in bills if b['bill_no'] == bill_no), None)
        
        if bill:
            self.show_bill_details(bill)
    
    def show_bill_details(self, bill):
        """Show bill details dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Bill Details - {bill['bill_no']}")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f'500x600+{x}+{y}')
        
        # Content Frame
        frame = tk.Frame(dialog, padx=30, pady=20)
        frame.pack(fill='both', expand=True)
        
        # Title
        tk.Label(frame, text=f"Bill #{bill['bill_no']}", 
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Details
        details = [
            ("Patient ID:", bill['patient_id']),
            ("Patient Name:", bill['patient_name']),
            ("Date:", bill['date']),
            ("Services:", bill['services']),
            ("Subtotal:", f"₹{bill['subtotal']:.2f}"),
            ("Tax:", f"₹{bill['tax']:.2f}"),
            ("Total:", f"₹{bill['total']:.2f}"),
            ("Status:", bill['status']),
            ("Payment Method:", bill.get('payment_method', 'N/A'))
        ]
        
        for label, value in details:
            detail_frame = tk.Frame(frame)
            detail_frame.pack(fill='x', pady=5)
            
            tk.Label(detail_frame, text=label, 
                    font=('Arial', 11, 'bold')).pack(side='left')
            tk.Label(detail_frame, text=str(value),
                    font=('Arial', 11)).pack(side='left', padx=(10, 0))
        
        # Action Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill='x', pady=20)
        
        if bill['status'] == 'Pending':
            tk.Button(btn_frame, text="Mark as Paid",
                     command=lambda: self.update_bill_status(bill['bill_no'], 
                                                           'Paid', 
                                                           dialog)).pack(side='left')
            
            tk.Button(btn_frame, text="Cancel Bill",
                     command=lambda: self.update_bill_status(bill['bill_no'], 
                                                           'Cancelled', 
                                                           dialog)).pack(side='left', 
                                                                       padx=10)
        
        tk.Button(btn_frame, text="Print",
                 command=lambda: self.print_bill(bill)).pack(side='left')
        
        tk.Button(btn_frame, text="Close",
                 command=dialog.destroy).pack(side='right')
    
    def update_bill_status(self, bill_no, status, dialog):
        """Update bill status"""
        bills = self.data_manager.get_bills()
        for i, bill in enumerate(bills):
            if bill['bill_no'] == bill_no:
                bills[i]['status'] = status
                self.data_manager.save_data(self.data_manager.billing_file, bills)
                break
        
        self.load_bills()
        dialog.destroy()
        messagebox.showinfo("Success", f"Bill marked as {status}")
    
    def print_bill(self, bill):
        """Generate and print bill"""
        filename = f"bill_{bill['bill_no']}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30
        )
        
        # Title
        elements.append(Paragraph("Hospital Bill", title_style))
        
        # Bill details
        details = [
            ["Bill No:", bill['bill_no']],
            ["Date:", bill['date']],
            ["Patient ID:", bill['patient_id']],
            ["Patient Name:", bill['patient_name']],
            ["Services:", bill['services']],
            ["Subtotal:", f"₹{bill['subtotal']:.2f}"],
            ["Tax:", f"₹{bill['tax']:.2f}"],
            ["Total:", f"₹{bill['total']:.2f}"],
            ["Status:", bill['status']],
            ["Payment Method:", bill.get('payment_method', 'N/A')]
        ]
        
        # Create table
        table = Table(details, colWidths=[100, 400])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        # Open PDF
        os.startfile(filename)
    
    def process_payment(self, updated_bill):
        """Handle payment completion and update bill"""
        self.data_manager.create_bill(updated_bill, self.user['id'])
        self.load_bills()
        
        # Generate and show PDF
        self.print_bill(updated_bill)
        
        messagebox.showinfo("Success", 
                          f"Bill {updated_bill['bill_no']} has been processed and saved!")

    def show_context_menu(self, event):
        """Show right-click context menu"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        menu = tk.Menu(self.parent, tearoff=0)
        menu.add_command(label="View Details", 
                        command=self.view_bill)
        menu.add_separator()
        
        bill_no = self.tree.item(selected_item[0])['values'][0]
        bills = self.data_manager.get_bills()
        bill = next((b for b in bills if b['bill_no'] == bill_no), None)
        
        if bill and bill['status'] == 'Pending':
            menu.add_command(label="Mark as Paid",
                           command=lambda: self.update_bill_status(bill_no, 
                                                                 'Paid', 
                                                                 None))
            menu.add_command(label="Cancel Bill",
                           command=lambda: self.update_bill_status(bill_no, 
                                                                 'Cancelled', 
                                                                 None))
        
        menu.add_command(label="Print Bill",
                        command=lambda: self.print_bill(bill))
        
        menu.post(event.x_root, event.y_root)