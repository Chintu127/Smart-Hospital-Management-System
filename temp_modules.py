class LabModule:
    """Laboratory Management Module for managing lab tests and reports"""
    
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        self.create_widgets()
        self.load_reports()
    
    def create_widgets(self):
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="🔬 Lab Reports", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        # Action Buttons
        btn_frame = tk.Frame(title_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="➕ New Report", font=('Arial', 10, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=self.create_report, padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', relief='flat', cursor='hand2',
                 command=self.load_reports, padx=15, pady=8).pack(side='left', padx=5)
        
        # Table Frame
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('Report ID', 'Patient', 'Test', 'Result', 'Date', 'Remarks')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        self.tree.bind('<Double-1>', self.view_report)
    
    def load_reports(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        reports = self.data_manager.get_lab_reports()
        
        for report in reports:
            self.tree.insert('', 'end', values=(
                report['id'],
                report['patient_name'],
                report['test'],
                report['result'],
                report['date'],
                report.get('remarks', 'N/A')
            ))
    
    def create_report(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Create New Lab Report")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f'500x600+{x}+{y}')
        
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Report ID
        reports = self.data_manager.get_lab_reports()
        new_id = self.data_manager.generate_id('L', reports)
        
        tk.Label(form_frame, text=f"Report ID: {new_id}", font=('Arial', 11, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Patient selection
        tk.Label(form_frame, text="Select Patient:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='w', pady=5)
        
        patients = self.data_manager.get_patients()
        patient_names = [f"{p['id']} - {p['name']}" for p in patients]
        patient_var = tk.StringVar()
        patient_cb = ttk.Combobox(form_frame, textvariable=patient_var, values=patient_names, 
                                state='readonly', font=('Arial', 10), width=30)
        patient_cb.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Test Type
        tk.Label(form_frame, text="Test Type:", font=('Arial', 10)).grid(
            row=2, column=0, sticky='w', pady=5)
        
        test_var = tk.StringVar()
        tests = ['Blood Test', 'Urine Test', 'X-Ray', 'MRI', 'CT Scan', 'Ultrasound']
        test_cb = ttk.Combobox(form_frame, textvariable=test_var, values=tests,
                              state='readonly', font=('Arial', 10), width=30)
        test_cb.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Result
        tk.Label(form_frame, text="Result:", font=('Arial', 10)).grid(
            row=3, column=0, sticky='w', pady=5)
        
        result_var = tk.StringVar()
        results = ['Normal', 'Abnormal', 'Positive', 'Negative', 'Requires Further Testing']
        result_cb = ttk.Combobox(form_frame, textvariable=result_var, values=results,
                               state='readonly', font=('Arial', 10), width=30)
        result_cb.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Remarks
        tk.Label(form_frame, text="Remarks:", font=('Arial', 10)).grid(
            row=4, column=0, sticky='w', pady=5)
        
        remarks_text = tk.Text(form_frame, font=('Arial', 10), width=30, height=5)
        remarks_text.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        def save_report():
            if not patient_var.get() or not test_var.get() or not result_var.get():
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            patient_id = patient_var.get().split(' - ')[0]
            patient_name = patient_var.get().split(' - ')[1]
            
            report_data = {
                'id': new_id,
                'patient_id': patient_id,
                'patient_name': patient_name,
                'test': test_var.get(),
                'result': result_var.get(),
                'remarks': remarks_text.get('1.0', 'end-1c'),
                'date': datetime.now().strftime("%Y-%m-%d")
            }
            
            self.data_manager.add_lab_report(report_data)
            messagebox.showinfo("Success", "Lab report created successfully!")
            dialog.destroy()
            self.load_reports()
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Save Report", font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white', command=save_report,
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Cancel", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='white', command=dialog.destroy,
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
    
    def view_report(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        report_id = item['values'][0]
        
        reports = self.data_manager.get_lab_reports()
        report = next((r for r in reports if r['id'] == report_id), None)
        
        if not report:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Lab Report - {report_id}")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f'500x400+{x}+{y}')
        
        # Content
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Header with report info
        header_frame = tk.Frame(content_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text=f"Report ID: {report['id']}", 
                font=('Arial', 12, 'bold')).pack(anchor='w')
        tk.Label(header_frame, text=f"Date: {report['date']}", 
                font=('Arial', 10)).pack(anchor='w')
        tk.Label(header_frame, text=f"Patient: {report['patient_name']}", 
                font=('Arial', 10)).pack(anchor='w')
        
        # Test details
        test_frame = tk.Frame(content_frame)
        test_frame.pack(fill='x', pady=10)
        
        tk.Label(test_frame, text="Test Type:", 
                font=('Arial', 10, 'bold')).pack(side='left')
        tk.Label(test_frame, text=report['test'], 
                font=('Arial', 10)).pack(side='left', padx=(5, 0))
        
        # Result
        result_frame = tk.Frame(content_frame)
        result_frame.pack(fill='x', pady=10)
        
        tk.Label(result_frame, text="Result:", 
                font=('Arial', 10, 'bold')).pack(side='left')
        tk.Label(result_frame, text=report['result'], 
                font=('Arial', 10)).pack(side='left', padx=(5, 0))
        
        # Remarks
        if report.get('remarks'):
            remarks_frame = tk.Frame(content_frame)
            remarks_frame.pack(fill='x', pady=10)
            
            tk.Label(remarks_frame, text="Remarks:", 
                    font=('Arial', 10, 'bold')).pack(anchor='w')
            tk.Label(remarks_frame, text=report['remarks'], 
                    font=('Arial', 10), wraplength=450).pack(anchor='w', pady=(5, 0))
        
        # Close button
        tk.Button(content_frame, text="Close", font=('Arial', 10),
                 command=dialog.destroy, width=10).pack(pady=20)

class BillReportsModule:
    """Bill Reports Management Module for viewing and managing billing reports"""
    
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        self.create_widgets()
        self.load_reports()
    
    def create_widgets(self):
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="💰 Billing Reports", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        # Action Buttons
        btn_frame = tk.Frame(title_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="🔄 Refresh", font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', relief='flat', cursor='hand2',
                 command=self.load_reports, padx=15, pady=8).pack(side='left', padx=5)
        
        # Patient Selection
        select_frame = tk.Frame(self.parent, bg='white')
        select_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(select_frame, text="Select Patient:", font=('Arial', 11),
                bg='white').pack(side='left', padx=(0,10))
        
        patients = self.data_manager.get_patients()
        patient_names = ["All Patients"] + [f"{p['id']} - {p['name']}" for p in patients]
        self.patient_var = tk.StringVar(value="All Patients")
        patient_cb = ttk.Combobox(select_frame, textvariable=self.patient_var, values=patient_names,
                                 state='readonly', font=('Arial', 10), width=40)
        patient_cb.pack(side='left')
        patient_cb.bind('<<ComboboxSelected>>', lambda e: self.load_reports())
        
        # Date Filter
        filter_frame = tk.Frame(select_frame, bg='white')
        filter_frame.pack(side='right')
        
        tk.Label(filter_frame, text="Filter by:", font=('Arial', 11),
                bg='white').pack(side='left', padx=(20, 10))
        
        self.filter_var = tk.StringVar(value="All")
        ttk.Combobox(filter_frame, textvariable=self.filter_var,
                    values=["All", "Today", "This Week", "This Month"],
                    state='readonly', width=15).pack(side='left')
        self.filter_var.trace('w', lambda *args: self.load_reports())
        
        # Table Frame
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical')
        scrollbar.pack(side='right', fill='y')
        
        columns = ('Bill No', 'Patient', 'Date', 'Services', 'Amount', 'Payment Method', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)
        
        # Column widths and headings
        widths = [100, 150, 100, 200, 100, 120, 100]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        self.tree.bind('<Double-1>', self.view_bill)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def load_reports(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        bills = self.data_manager.get_bills()
        
        # Apply patient filter
        selected_patient = self.patient_var.get()
        if selected_patient != "All Patients":
            patient_id = selected_patient.split(' - ')[0]
            bills = [b for b in bills if b['patient_id'] == patient_id]
        
        # Apply date filter
        filter_option = self.filter_var.get()
        if filter_option != "All":
            today = datetime.now()
            if filter_option == "Today":
                bills = [b for b in bills if b['date'] == today.strftime("%Y-%m-%d")]
            elif filter_option == "This Week":
                week_ago = today - timedelta(days=7)
                bills = [b for b in bills if datetime.strptime(b['date'], "%Y-%m-%d") >= week_ago]
            elif filter_option == "This Month":
                month_ago = today - timedelta(days=30)
                bills = [b for b in bills if datetime.strptime(b['date'], "%Y-%m-%d") >= month_ago]
        
        for bill in bills:
            self.tree.insert('', 'end', values=(
                bill['bill_no'],
                bill['patient_name'],
                bill['date'],
                bill['services'],
                f"₹{bill['total']:.2f}",
                bill['payment_method'],
                bill['status']
            ))
    
    def view_bill(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        bill_no = item['values'][0]
        
        bills = self.data_manager.get_bills()
        bill = next((b for b in bills if b['bill_no'] == bill_no), None)
        
        if not bill:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Bill Details - {bill_no}")
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f'600x500+{x}+{y}')
        
        # Header
        header = tk.Frame(dialog, bg='#2ecc71', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text=f"Bill #{bill['bill_no']}", font=('Arial', 16, 'bold'),
                bg='#2ecc71', fg='white').pack(pady=(10, 5))
        tk.Label(header, text=f"Date: {bill['date']}", font=('Arial', 10),
                bg='#2ecc71', fg='white').pack()
        
        # Details
        details_frame = tk.Frame(dialog, padx=30, pady=20)
        details_frame.pack(fill='both', expand=True)
        
        details = [
            ('Patient Name', bill['patient_name']),
            ('Patient ID', bill['patient_id']),
            ('Services', bill['services']),
            ('Payment Method', bill['payment_method']),
            ('Status', bill['status']),
            ('Subtotal', f"₹{bill['subtotal']:.2f}"),
            ('Tax (10%)', f"₹{bill['tax']:.2f}"),
            ('Total Amount', f"₹{bill['total']:.2f}")
        ]
        
        for i, (label, value) in enumerate(details):
            tk.Label(details_frame, text=f"{label}:", font=('Arial', 11, 'bold')).grid(
                row=i, column=0, sticky='w', pady=10)
            tk.Label(details_frame, text=str(value), font=('Arial', 11)).grid(
                row=i, column=1, sticky='w', padx=20, pady=10)
        
        btn_frame = tk.Frame(details_frame)
        btn_frame.grid(row=len(details), column=0, columnspan=2, pady=20)
        
        # Print/Download button
        tk.Button(btn_frame, text="🖨️ Print Bill", font=('Arial', 11, 'bold'),
                 bg='#3498db', fg='white', command=lambda: self.generate_bill_pdf(bill),
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Close", font=('Arial', 11, 'bold'),
                 bg='#95a5a6', fg='white', command=dialog.destroy,
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
    
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            menu = tk.Menu(self.parent, tearoff=0)
            menu.add_command(label="👁️ View Bill Details",
                           command=lambda: self.view_bill(None))
            menu.add_separator()
            menu.add_command(label="📋 Copy Bill No",
                           command=self.copy_bill_no)
            
            menu.post(event.x_root, event.y_root)
    
    def copy_bill_no(self):
        selected = self.tree.selection()
        if selected:
            bill_no = self.tree.item(selected[0])['values'][0]
            self.parent.clipboard_clear()
            self.parent.clipboard_append(bill_no)
    
    def generate_bill_pdf(self, bill_data):
        filename = f"{self.data_manager.data_dir}/bill_{bill_data['bill_no']}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        
        # Header
        header_text = "BILLING STATEMENT"
        story.append(Paragraph(header_text, styles['Center']))
        story.append(Spacer(1, 20))
        
        # Bill info
        info_data = [
            ['Bill No:', bill_data['bill_no']],
            ['Date:', bill_data['date']],
            ['Patient ID:', bill_data['patient_id']],
            ['Patient Name:', bill_data['patient_name']],
            ['Payment Method:', bill_data['payment_method']],
            ['Status:', bill_data['status']]
        ]
        
        info_table = Table(info_data, colWidths=[100, 400])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Services
        story.append(Paragraph("Services", styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(bill_data['services'], styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Amount details
        amounts = [
            ['Subtotal:', f"₹{bill_data['subtotal']:.2f}"],
            ['Tax (10%):', f"₹{bill_data['tax']:.2f}"],
            ['Total Amount:', f"₹{bill_data['total']:.2f}"]
        ]
        
        amount_table = Table(amounts, colWidths=[100, 400])
        amount_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ]))
        story.append(amount_table)
        
        doc.build(story)
        os.startfile(filename)