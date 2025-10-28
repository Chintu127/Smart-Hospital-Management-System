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
            f"${bill['subtotal']:.2f}",
            f"${bill['tax']:.2f}",
            f"${bill['total']:.2f}",
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
        """Open dialog to create new bill"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Create New Bill")
        dialog.geometry("600x700")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f'600x700+{x}+{y}')
        
        # Form Frame
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Title
        tk.Label(form_frame, text="New Bill", 
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Bill Number (Auto-generated)
        bill_no = f"B{str(uuid.uuid4())[:8].upper()}"
        
        # Patient Selection
        patient_frame = tk.Frame(form_frame)
        patient_frame.pack(fill='x', pady=10)
        
        tk.Label(patient_frame, text="Patient:", 
                font=('Arial', 11)).pack(side='left')
        
        # Get patients list
        patients = self.data_manager.get_patients()
        patient_list = [f"{p['id']} - {p['name']}" for p in patients]
        
        self.patient_var = tk.StringVar()
        patient_cb = ttk.Combobox(patient_frame, 
                                 textvariable=self.patient_var,
                                 values=patient_list,
                                 width=40)
        patient_cb.pack(side='left', padx=10)
        
        # Services
        tk.Label(form_frame, text="Services:", 
                font=('Arial', 11)).pack(anchor='w', pady=(10, 5))
        
        services_frame = tk.Frame(form_frame)
        services_frame.pack(fill='x')
        
        self.services_listbox = tk.Listbox(services_frame, 
                                         height=6,
                                         selectmode='multiple')
        self.services_listbox.pack(side='left', fill='x', expand=True)
        
        services_scroll = tk.Scrollbar(services_frame, 
                                     orient='vertical',
                                     command=self.services_listbox.yview)
        services_scroll.pack(side='right', fill='y')
        
        self.services_listbox.config(yscrollcommand=services_scroll.set)
        
        # Add common services
        services = [
            "Consultation - $50",
            "Blood Test - $100",
            "X-Ray - $150",
            "MRI Scan - $500",
            "CT Scan - $400",
            "Ultrasound - $200",
            "ECG - $100",
            "Vaccination - $75",
            "Minor Surgery - $1000",
            "Major Surgery - $5000"
        ]
        
        for service in services:
            self.services_listbox.insert('end', service)
        
        # Custom Service Entry
        custom_frame = tk.Frame(form_frame)
        custom_frame.pack(fill='x', pady=10)
        
        self.custom_service = tk.Entry(custom_frame, width=30)
        self.custom_service.pack(side='left')
        
        tk.Button(custom_frame, text="Add Service",
                 command=self.add_custom_service).pack(side='left', padx=5)
        
        # Amount Details
        amounts_frame = tk.Frame(form_frame)
        amounts_frame.pack(fill='x', pady=20)
        
        # Subtotal
        tk.Label(amounts_frame, text="Subtotal: $").grid(row=0, column=0)
        self.subtotal_var = tk.StringVar(value="0.00")
        subtotal_entry = tk.Entry(amounts_frame, 
                                textvariable=self.subtotal_var,
                                state='readonly',
                                width=10)
        subtotal_entry.grid(row=0, column=1)
        
        # Tax
        tk.Label(amounts_frame, text="Tax (10%): $").grid(row=1, column=0)
        self.tax_var = tk.StringVar(value="0.00")
        tax_entry = tk.Entry(amounts_frame, 
                           textvariable=self.tax_var,
                           state='readonly',
                           width=10)
        tax_entry.grid(row=1, column=1)
        
        # Total
        tk.Label(amounts_frame, text="Total: $").grid(row=2, column=0)
        self.total_var = tk.StringVar(value="0.00")
        total_entry = tk.Entry(amounts_frame, 
                             textvariable=self.total_var,
                             state='readonly',
                             width=10)
        total_entry.grid(row=2, column=1)
        
        # Calculate Button
        tk.Button(form_frame, text="Calculate Total",
                 command=self.calculate_total).pack(pady=10)
        
        # Payment Method
        payment_frame = tk.Frame(form_frame)
        payment_frame.pack(fill='x', pady=10)
        
        tk.Label(payment_frame, text="Payment Method:").pack(side='left')
        
        self.payment_var = tk.StringVar(value="Cash")
        methods = ["Cash", "Credit Card", "Debit Card", "Insurance", "Bank Transfer"]
        payment_cb = ttk.Combobox(payment_frame, 
                                 textvariable=self.payment_var,
                                 values=methods,
                                 width=15)
        payment_cb.pack(side='left', padx=10)
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=20)
        
        tk.Button(btn_frame, text="Save",
                 command=lambda: self.save_bill(bill_no, dialog)).pack(side='right')
        
        tk.Button(btn_frame, text="Cancel",
                 command=dialog.destroy).pack(side='right', padx=10)
    
    def add_custom_service(self):
        """Add custom service to services list"""
        service = self.custom_service.get().strip()
        if service:
            if not service.endswith(')'):
                service += " - $0"
            self.services_listbox.insert('end', service)
            self.custom_service.delete(0, 'end')
    
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
            ("Subtotal:", f"${bill['subtotal']:.2f}"),
            ("Tax:", f"${bill['tax']:.2f}"),
            ("Total:", f"${bill['total']:.2f}"),
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
            ["Subtotal:", f"${bill['subtotal']:.2f}"],
            ["Tax:", f"${bill['tax']:.2f}"],
            ["Total:", f"${bill['total']:.2f}"],
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