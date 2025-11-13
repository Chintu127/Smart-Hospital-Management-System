import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
import json
import csv
import os
from datetime import datetime, timedelta
import random
import string
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk, ImageDraw, ImageFont
import qrcode
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from date_picker import DatePicker
from notification_manager import NotificationManager
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import seaborn as sns
from analytics_manager import AnalyticsManager
from billing_module import BillingModule
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk, ImageDraw, ImageFont
import qrcode
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ==================== DATA STRUCTURES ====================

class Stack:
    """Stack for Undo operations"""
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None
    
    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

class Queue:
    """Queue for Appointment Management"""
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        return None
    
    def front(self):
        if not self.is_empty():
            return self.items[0]
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# ==================== DATA MANAGER ====================

class DataManager:
    """Centralized data management with CSV/JSON support"""
    
    def __init__(self):
        # Set data directory in the user's home folder
        self.data_dir = os.path.join(os.path.expanduser('~'), 'hospital_data')
        self.ensure_data_directory()
        
        # Initialize data files
        self.patients_file = os.path.join(self.data_dir, "patients.json")
        self.doctors_file = os.path.join(self.data_dir, "doctors.json")
        self.appointments_file = os.path.join(self.data_dir, "appointments.json")
        self.pharmacy_file = os.path.join(self.data_dir, "pharmacy.json")
        self.lab_file = os.path.join(self.data_dir, "lab_reports.json")
        self.billing_file = os.path.join(self.data_dir, "billing.json")
        self.users_file = os.path.join(self.data_dir, "users.json")
        
        # Initialize default data
        self.initialize_default_data()
        
        # Undo stack for billing operations
        self.billing_undo_stack = Stack()
        
        # Appointment queue
        self.appointment_queue = Queue()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def initialize_default_data(self):
        """Initialize with sample data if files don't exist"""
        
        # Users
        if not os.path.exists(self.users_file):
            users = {
                "admin": {"password": "admin123", "role": "admin", "name": "Administrator"},
                "reception": {"password": "reception123", "role": "reception", "name": "Reception Desk"},
                "doctor1": {"password": "doctor123", "role": "doctor", "name": "Dr. Smith"},
                "pharmacy": {"password": "pharmacy123", "role": "pharmacy", "name": "Pharmacy Dept"},
                "lab": {"password": "lab123", "role": "lab", "name": "Lab Technician"}
            }
            self.save_data(self.users_file, users)
        
        # Doctors
        if not os.path.exists(self.doctors_file):
            doctors = [
                {"id": "D001", "name": "Dr. Sarah Smith", "specialization": "Cardiology", 
                 "contact": "555-0101", "availability": "Mon-Fri 9AM-5PM", "email": "sarah.smith@hospital.com"},
                {"id": "D002", "name": "Dr. John Davis", "specialization": "Neurology", 
                 "contact": "555-0102", "availability": "Mon-Wed 10AM-4PM", "email": "john.davis@hospital.com"},
                {"id": "D003", "name": "Dr. Emily Johnson", "specialization": "Pediatrics", 
                 "contact": "555-0103", "availability": "Tue-Sat 8AM-3PM", "email": "emily.johnson@hospital.com"},
                {"id": "D004", "name": "Dr. Michael Brown", "specialization": "Orthopedics", 
                 "contact": "555-0104", "availability": "Mon-Fri 11AM-6PM", "email": "michael.brown@hospital.com"},
                {"id": "D005", "name": "Dr. Lisa Wilson", "specialization": "General Medicine", 
                 "contact": "555-0105", "availability": "Daily 9AM-5PM", "email": "lisa.wilson@hospital.com"}
            ]
            self.save_data(self.doctors_file, doctors)
        
        # Patients
        if not os.path.exists(self.patients_file):
            patients = [
                {"id": "P001", "name": "Robert Anderson", "age": 45, "gender": "Male", 
                 "disease": "Hypertension", "doctor": "Dr. Sarah Smith", "admit_date": "2025-01-15",
                 "contact": "555-1001", "address": "123 Main St", "blood_group": "O+"},
                {"id": "P002", "name": "Maria Garcia", "age": 32, "gender": "Female", 
                 "disease": "Migraine", "doctor": "Dr. John Davis", "admit_date": "2025-01-20",
                 "contact": "555-1002", "address": "456 Oak Ave", "blood_group": "A+"},
                {"id": "P003", "name": "James Wilson", "age": 8, "gender": "Male", 
                 "disease": "Fever", "doctor": "Dr. Emily Johnson", "admit_date": "2025-01-22",
                 "contact": "555-1003", "address": "789 Pine Rd", "blood_group": "B+"}
            ]
            self.save_data(self.patients_file, patients)
        
        # Pharmacy
        if not os.path.exists(self.pharmacy_file):
            pharmacy = [
                {"id": "M001", "name": "Paracetamol", "stock": 500, "price": 2.50, "category": "Pain Relief"},
                {"id": "M002", "name": "Amoxicillin", "stock": 300, "price": 15.00, "category": "Antibiotic"},
                {"id": "M003", "name": "Ibuprofen", "stock": 400, "price": 5.00, "category": "Pain Relief"},
                {"id": "M004", "name": "Aspirin", "stock": 600, "price": 3.00, "category": "Pain Relief"},
                {"id": "M005", "name": "Insulin", "stock": 150, "price": 45.00, "category": "Diabetes"}
            ]
            self.save_data(self.pharmacy_file, pharmacy)
        
        # Lab Reports
        if not os.path.exists(self.lab_file):
            lab_reports = [
                {"id": "L001", "patient_id": "P001", "patient_name": "Robert Anderson", 
                 "test": "Blood Test", "result": "Normal", "date": "2025-01-16", "remarks": "All parameters within range"},
                {"id": "L002", "patient_id": "P002", "patient_name": "Maria Garcia", 
                 "test": "MRI Scan", "result": "No abnormalities", "date": "2025-01-21", "remarks": "Brain scan clear"}
            ]
            self.save_data(self.lab_file, lab_reports)
        
        # Appointments
        if not os.path.exists(self.appointments_file):
            appointments = [
                {"id": "A001", "patient_name": "Robert Anderson", "patient_id": "P001", 
                 "doctor": "Dr. Sarah Smith", "doctor_id": "D001",
                 "date": "2025-01-25", "time": "10:00",
                 "duration": "30 min", "purpose": "Follow-up",
                 "status": "Scheduled", "emergency": False},
                {"id": "A002", "patient_name": "Maria Garcia", "patient_id": "P002", 
                 "doctor": "Dr. John Davis", "doctor_id": "D002",
                 "date": "2025-01-26", "time": "14:00", 
                 "duration": "30 min", "purpose": "Initial consultation",
                 "status": "Scheduled", "emergency": False}
            ]
            self.save_data(self.appointments_file, appointments)
        
        # Billing
        if not os.path.exists(self.billing_file):
            billing = [
                {"bill_no": "B001", "patient_id": "P001", "patient_name": "Robert Anderson", 
                 "services": "Consultation, Blood Test", "subtotal": 150.00, "tax": 15.00, 
                 "total": 165.00, "payment_method": "Cash", "date": "2025-01-16", "status": "Paid"}
            ]
            self.save_data(self.billing_file, billing)
    
    def save_data(self, filepath, data):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_data(self, filepath):
        """Load data from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return [] if filepath != self.users_file else {}
    
    # Patient operations
    def get_patients(self):
        return self.load_data(self.patients_file)
    
    def add_patient(self, patient):
        patients = self.get_patients()
        patients.append(patient)
        self.save_data(self.patients_file, patients)
    
    def update_patient(self, patient_id, updated_data):
        patients = self.get_patients()
        for i, patient in enumerate(patients):
            if patient['id'] == patient_id:
                patients[i].update(updated_data)
                self.save_data(self.patients_file, patients)
                return True
        return False
    
    def delete_patient(self, patient_id):
        patients = self.get_patients()
        patients = [p for p in patients if p['id'] != patient_id]
        self.save_data(self.patients_file, patients)
    
    def get_patient_by_id(self, patient_id):
        """Dictionary lookup for O(n) search"""
        patients = self.get_patients()
        patient_dict = {p['id']: p for p in patients}
        return patient_dict.get(patient_id)
    
    # Doctor operations
    def get_doctors(self):
        return self.load_data(self.doctors_file)
    
    def add_doctor(self, doctor):
        doctors = self.get_doctors()
        doctors.append(doctor)
        self.save_data(self.doctors_file, doctors)
    
    def update_doctor(self, doctor_id, updated_data):
        doctors = self.get_doctors()
        for i, doctor in enumerate(doctors):
            if doctor['id'] == doctor_id:
                doctors[i].update(updated_data)
                self.save_data(self.doctors_file, doctors)
                return True
        return False
    
    def delete_doctor(self, doctor_id):
        doctors = self.get_doctors()
        doctors = [d for d in doctors if d['id'] != doctor_id]
        self.save_data(self.doctors_file, doctors)
    
    # Appointment operations
    def get_appointments(self):
        return self.load_data(self.appointments_file)
    
    def add_appointment(self, appointment):
        appointments = self.get_appointments()
        appointments.append(appointment)
        self.save_data(self.appointments_file, appointments)
        self.appointment_queue.enqueue(appointment)
    
    def update_appointment(self, appointment_id, updated_data):
        appointments = self.get_appointments()
        for i, appt in enumerate(appointments):
            if appt['id'] == appointment_id:
                appointments[i].update(updated_data)
                self.save_data(self.appointments_file, appointments)
                return True
        return False
    
    def delete_appointment(self, appointment_id):
        appointments = self.get_appointments()
        appointments = [a for a in appointments if a['id'] != appointment_id]
        self.save_data(self.appointments_file, appointments)
    
    # Pharmacy operations
    def get_medicines(self):
        return self.load_data(self.pharmacy_file)
    
    def add_medicine(self, medicine):
        medicines = self.get_medicines()
        medicines.append(medicine)
        self.save_data(self.pharmacy_file, medicines)
    
    def update_medicine(self, medicine_id, updated_data):
        medicines = self.get_medicines()
        for i, med in enumerate(medicines):
            if med['id'] == medicine_id:
                medicines[i].update(updated_data)
                self.save_data(self.pharmacy_file, medicines)
                return True
        return False
    
    def delete_medicine(self, medicine_id):
        medicines = self.get_medicines()
        medicines = [m for m in medicines if m['id'] != medicine_id]
        self.save_data(self.pharmacy_file, medicines)
    
    # Lab operations
    def get_lab_reports(self):
        return self.load_data(self.lab_file)
    
    def add_lab_report(self, report):
        reports = self.get_lab_reports()
        reports.append(report)
        self.save_data(self.lab_file, reports)
    
    def update_lab_report(self, report_id, updated_data):
        reports = self.get_lab_reports()
        for i, report in enumerate(reports):
            if report['id'] == report_id:
                reports[i].update(updated_data)
                self.save_data(self.lab_file, reports)
                return True
        return False
    
    def delete_lab_report(self, report_id):
        reports = self.get_lab_reports()
        reports = [r for r in reports if r['id'] != report_id]
        self.save_data(self.lab_file, reports)
    
    # Billing operations
    def get_bills(self):
        return self.load_data(self.billing_file)
    
    def add_bill(self, bill):
        bills = self.get_bills()
        # Push to undo stack
        self.billing_undo_stack.push(('add', bill))
        bills.append(bill)
        self.save_data(self.billing_file, bills)

    def update_bill(self, bill):
        """Update an existing bill by bill_no; if not present, add it."""
        bills = self.get_bills()
        for i, b in enumerate(bills):
            if b.get('bill_no') == bill.get('bill_no'):
                bills[i].update(bill)
                self.save_data(self.billing_file, bills)
                return True
        # Not found -> append
        bills.append(bill)
        self.save_data(self.billing_file, bills)
        return True
    
    def undo_last_bill(self):
        """Undo last billing operation using Stack"""
        if not self.billing_undo_stack.is_empty():
            operation, bill = self.billing_undo_stack.pop()
            if operation == 'add':
                bills = self.get_bills()
                bills = [b for b in bills if b['bill_no'] != bill['bill_no']]
                self.save_data(self.billing_file, bills)
                return True
        return False
    
    # User operations
    def get_users(self):
        """Return list of user dicts converted from users file mapping.
        The users file stores a mapping username -> {password, role, name}.
        This function converts it to a list of dicts with 'id' set to username.
        """
        data = self.load_data(self.users_file)
        if isinstance(data, dict):
            users = []
            for uname, info in data.items():
                u = {'id': uname}
                u.update(info)
                users.append(u)
            return users
        return data
    
    def verify_user(self, username, password):
        # The users file stores a dict mapping usernames to info. Verify against it.
        data = self.load_data(self.users_file)
        if isinstance(data, dict) and username in data:
            if data[username].get('password') == password:
                user = data[username].copy()
                user['id'] = username
                return user
        return None

    def add_user(self, username, password, role, name, **kwargs):
        """Add a new user into the users file. Password is stored as plain text here
        to remain compatible with the existing simple verifier. If you prefer hashed
        passwords we can migrate to hashed storage (recommended).
        """
        data = self.load_data(self.users_file)
        if not isinstance(data, dict):
            data = {}
        if username in data:
            raise ValueError('Username already exists')
        data[username] = {'password': password, 'role': role, 'name': name}
        # Merge extra fields
        for k, v in kwargs.items():
            data[username][k] = v
        self.save_data(self.users_file, data)
        return {'id': username, **data[username]}
    
    def generate_id(self, prefix, existing_list):
        """Generate unique ID"""
        if not existing_list:
            return f"{prefix}001"
        
        max_num = 0
        for item in existing_list:
            if 'id' in item:
                num_part = int(item['id'][len(prefix):])
                max_num = max(max_num, num_part)
        
        return f"{prefix}{str(max_num + 1).zfill(3)}"

# ==================== LOGIN WINDOW ====================

class LoginWindow:
    """Modern Login Screen"""
    
    def __init__(self, root, data_manager):
        self.root = root
        self.data_manager = data_manager
        self.root.title("Smart Hospital Management System - Login")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e3a5f')
        
        # Center window
        self.center_window()
        
        self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        width = 800
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e3a5f')
        main_frame.pack(expand=True, fill='both')
        
        # Logo/Title Frame
        title_frame = tk.Frame(main_frame, bg='#1e3a5f')
        title_frame.pack(pady=40)
        
        # Hospital Icon (emoji style)
        icon_label = tk.Label(title_frame, text="🏥", font=('Arial', 60), bg='#1e3a5f', fg='white')
        icon_label.pack()
        
        title_label = tk.Label(title_frame, text="Smart Hospital Management", 
                               font=('Arial', 28, 'bold'), bg='#1e3a5f', fg='white')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Separate Dashboard", 
                                  font=('Arial', 14), bg='#1e3a5f', fg='#a0c4ff')
        subtitle_label.pack()
        
        # Login Form Frame
        form_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        form_frame.pack(pady=30, padx=100, fill='x')
        
        # Inner padding
        inner_frame = tk.Frame(form_frame, bg='white')
        inner_frame.pack(padx=40, pady=40)
        
        # Username
        tk.Label(inner_frame, text="👤 Username", font=('Arial', 12, 'bold'), 
                bg='white', fg='#333').grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.username_entry = tk.Entry(inner_frame, font=('Arial', 12), width=30, relief='solid', bd=1)
        self.username_entry.grid(row=1, column=0, pady=(0, 20), ipady=8)
        
        # Password
        tk.Label(inner_frame, text="🔒 Password", font=('Arial', 12, 'bold'), 
                bg='white', fg='#333').grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.password_entry = tk.Entry(inner_frame, font=('Arial', 12), width=30, 
                                       show='●', relief='solid', bd=1)
        self.password_entry.grid(row=3, column=0, pady=(0, 20), ipady=8)
        
        # Role Selection
        tk.Label(inner_frame, text="🎭 Select Role", font=('Arial', 12, 'bold'), 
                bg='white', fg='#333').grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        self.role_var = tk.StringVar(value="reception")
        roles = [("Reception", "reception"), ("Doctor", "doctor"), ("Pharmacy", "pharmacy"), 
                 ("Lab", "lab"), ("Admin", "admin")]
        
        role_frame = tk.Frame(inner_frame, bg='white')
        role_frame.grid(row=5, column=0, pady=(0, 30))
        
        for i, (text, value) in enumerate(roles):
            rb = tk.Radiobutton(role_frame, text=text, variable=self.role_var, value=value,
                               font=('Arial', 10), bg='white', fg='#333', selectcolor='#a0c4ff')
            rb.pack(side='left', padx=5)
        
        # Login Button
        login_btn = tk.Button(inner_frame, text="LOGIN", font=('Arial', 14, 'bold'),
                             bg='#4CAF50', fg='white', width=25, height=2,
                             relief='flat', cursor='hand2', command=self.login)
        login_btn.grid(row=6, column=0, pady=10)
        
        # Register link
        register_frame = tk.Frame(inner_frame, bg='white')
        register_frame.grid(row=7, column=0)
        tk.Label(register_frame, text="Don't have an account?", font=('Arial', 10), bg='white').pack(side='left')
        tk.Button(register_frame, text="Register", font=('Arial', 10), fg='#3498db', bg='white', bd=0, relief='flat', cursor='hand2', command=self.show_registration).pack(side='left', padx=5)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
        
        # Info Frame
        info_frame = tk.Frame(main_frame, bg='#1e3a5f')
        info_frame.pack(pady=20)
        
        info_text = """
        Default Credentials:
        Admin: admin/admin123  |  Reception: reception/reception123
        Doctor: doctor1/doctor123  |  Pharmacy: pharmacy/pharmacy123  |  Lab: lab/lab123
        """
        
        tk.Label(info_frame, text=info_text, font=('Arial', 9), 
                bg='#1e3a5f', fg='#a0c4ff', justify='center').pack()
    
    def show_registration(self):
        """Show a simple registration dialog and persist to users file via DataManager.add_user
        Note: this creates plain-text passwords to remain compatible with the app's simple verifier.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Register New Account")
        dialog.geometry("480x420")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text="New User Registration", font=('Arial', 16, 'bold')).pack(pady=(0,10))
        
        entries = {}
        fields = [
            ('Full Name', 'name'),
            ('Username', 'username'),
            ('Password', 'password'),
            ('Confirm Password', 'confirm')
        ]
        for label, key in fields:
            tk.Label(frame, text=label+":", font=('Arial', 11)).pack(anchor='w', pady=(8,0))
            if 'password' in key:
                e = tk.Entry(frame, show='•', width=40)
            else:
                e = tk.Entry(frame, width=40)
            e.pack()
            entries[key] = e
        
        # Role
        tk.Label(frame, text="Role:", font=('Arial', 11)).pack(anchor='w', pady=(8,0))
        role_var = tk.StringVar(value='reception')
        role_combo = ttk.Combobox(frame, textvariable=role_var, values=['admin','doctor','reception','pharmacy','lab'], state='readonly', width=37)
        role_combo.pack()
        
        def do_register():
            name = entries['name'].get().strip()
            username = entries['username'].get().strip()
            pwd = entries['password'].get().strip()
            confirm = entries['confirm'].get().strip()
            role = role_var.get()
            if not all([name, username, pwd, confirm]):
                messagebox.showerror('Error','All fields are required')
                return
            if pwd != confirm:
                messagebox.showerror('Error','Passwords do not match')
                return
            if len(pwd) < 6:
                messagebox.showerror('Error','Password must be at least 6 characters')
                return
            try:
                created = self.data_manager.add_user(username=username, password=pwd, role=role, name=name)
                messagebox.showinfo('Success', f"Account created. Username: {created['id']}")
                dialog.destroy()
            except ValueError as ve:
                messagebox.showerror('Error', str(ve))
            except Exception as e:
                messagebox.showerror('Error', f"Unable to create account: {str(e)}")
        
        tk.Button(frame, text='Register', bg='#2ecc71', fg='white', command=do_register).pack(pady=15)
        tk.Button(frame, text='Cancel', command=dialog.destroy).pack()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        selected_role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        user = self.data_manager.verify_user(username, password)
        
        if user and user['role'] == selected_role:
            messagebox.showinfo("Success", f"Welcome, {user['name']}!")
            self.root.destroy()
            
            # Open main dashboard
            main_root = tk.Tk()
            MainDashboard(main_root, self.data_manager, user)
            main_root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials or role mismatch")

# ==================== MAIN DASHBOARD ====================

class MainDashboard:
    """Main Dashboard with Sidebar Navigation"""
    
    def __init__(self, root, data_manager, user):
        self.root = root
        self.data_manager = data_manager
        self.user = user
        
        self.root.title(f"Smart Hospital Management - {user['name']}")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')
        
        # Center window
        self.center_window()
        
        # Current module
        self.current_module = None
        
        self.create_layout()
        
        # Load default module based on role
        self.load_default_module()
    
    def center_window(self):
        self.root.update_idletasks()
        width = 1400
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_layout(self):
        # Top Bar
        self.create_top_bar()
        
        # Main Container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True)
        
        # Left Sidebar
        self.create_sidebar(main_container)
        
        # Right Content Area
        self.content_frame = tk.Frame(main_container, bg='white')
        self.content_frame.pack(side='right', fill='both', expand=True)
    
    def create_top_bar(self):
        top_bar = tk.Frame(self.root, bg='#2c3e50', height=60)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)
        
        # Title
        tk.Label(top_bar, text="🏥 Smart Hospital Management System", 
                font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white').pack(side='left', padx=20)
        
        # User info and logout
        user_frame = tk.Frame(top_bar, bg='#2c3e50')
        user_frame.pack(side='right', padx=20)
        
        tk.Label(user_frame, text=f"👤 {self.user['name']} ({self.user['role'].title()})", 
                font=('Arial', 11), bg='#2c3e50', fg='white').pack(side='left', padx=10)
        
        logout_btn = tk.Button(user_frame, text="🚪 Logout", font=('Arial', 10, 'bold'),
                              bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                              command=self.logout, padx=15, pady=5)
        logout_btn.pack(side='left')
    
    def create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg='#34495e', width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Sidebar Title
        tk.Label(sidebar, text="MENU", font=('Arial', 14, 'bold'), 
                bg='#34495e', fg='white', pady=20).pack()
        
        # Define menu items based on role
        menu_items = self.get_menu_items()
        
        for item in menu_items:
            self.create_menu_button(sidebar, item['text'], item['icon'], item['command'])
    
    def get_menu_items(self):
        """Get menu items based on user role"""
        role = self.user['role']
        
        common_items = []
        
        if role == 'admin':
            common_items = [
                {'text': 'Dashboard', 'icon': '📊', 'command': lambda: self.load_module('dashboard')},
                {'text': 'Patients', 'icon': '🏥', 'command': lambda: self.load_module('patients')},
                {'text': 'Doctors', 'icon': '👨‍⚕️', 'command': lambda: self.load_module('doctors')},
                {'text': 'Appointments', 'icon': '📅', 'command': lambda: self.load_module('appointments')},
                {'text': 'Pharmacy', 'icon': '💊', 'command': lambda: self.load_module('pharmacy')},
                {'text': 'Lab Reports', 'icon': '🔬', 'command': lambda: self.load_module('lab')},
                {'text': 'Billing', 'icon': '💵', 'command': lambda: self.load_module('billing')},
                {'text': 'Bill Reports', 'icon': '📄', 'command': lambda: self.load_module('bill_reports')},
                {'text': 'Analytics', 'icon': '📈', 'command': lambda: self.load_module('analytics')},
                {'text': 'Emergency', 'icon': '🚑', 'command': lambda: self.load_module('emergency')},
            ]
        elif role == 'reception':
            common_items = [
                {'text': 'Dashboard', 'icon': '📊', 'command': lambda: self.load_module('dashboard')},
                {'text': 'Patients', 'icon': '🏥', 'command': lambda: self.load_module('patients')},
                {'text': 'Appointments', 'icon': '📅', 'command': lambda: self.load_module('appointments')},
                {'text': 'Billing', 'icon': '💵', 'command': lambda: self.load_module('billing')},
                {'text': 'Bill Reports', 'icon': '📄', 'command': lambda: self.load_module('bill_reports')},
                {'text': 'Emergency', 'icon': '🚑', 'command': lambda: self.load_module('emergency')},
            ]
        elif role == 'doctor':
            common_items = [
                {'text': 'Dashboard', 'icon': '📊', 'command': lambda: self.load_module('dashboard')},
                {'text': 'My Patients', 'icon': '🏥', 'command': lambda: self.load_module('patients')},
                {'text': 'Appointments', 'icon': '📅', 'command': lambda: self.load_module('appointments')},
                {'text': 'Lab Reports', 'icon': '🔬', 'command': lambda: self.load_module('lab')},
            ]
        elif role == 'pharmacy':
            common_items = [
                {'text': 'Dashboard', 'icon': '📊', 'command': lambda: self.load_module('dashboard')},
                {'text': 'Pharmacy', 'icon': '💊', 'command': lambda: self.load_module('pharmacy')},
                {'text': 'Patients', 'icon': '🏥', 'command': lambda: self.load_module('patients')},
            ]
        elif role == 'lab':
            common_items = [
                {'text': 'Dashboard', 'icon': '📊', 'command': lambda: self.load_module('dashboard')},
                {'text': 'Lab Reports', 'icon': '🔬', 'command': lambda: self.load_module('lab')},
                {'text': 'Patients', 'icon': '🏥', 'command': lambda: self.load_module('patients')},
            ]
        
        return common_items
    
    def create_menu_button(self, parent, text, icon, command):
        btn = tk.Button(parent, text=f"{icon}  {text}", font=('Arial', 11),
                       bg='#34495e', fg='white', relief='flat', cursor='hand2',
                       anchor='w', padx=20, pady=15, command=command)
        btn.pack(fill='x', padx=5, pady=2)
        
        # Hover effects
        btn.bind('<Enter>', lambda e: btn.config(bg='#4a6278'))
        btn.bind('<Leave>', lambda e: btn.config(bg='#34495e'))
    
    def load_module(self, module_name):
        """Load different modules"""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.current_module = module_name
        
        if module_name == 'dashboard':
            DashboardModule(self.content_frame, self.data_manager, self.user)
        elif module_name == 'patients':
            PatientsModule(self.content_frame, self.data_manager, self.user)
        elif module_name == 'doctors':
            DoctorsModule(self.content_frame, self.data_manager, self.user)
        elif module_name == 'appointments':
            AppointmentsModule(self.content_frame, self.data_manager, self.user)
        elif module_name == 'pharmacy':
            PharmacyModule(self.content_frame, self.data_manager, self.user)
        elif module_name == 'lab':
            LabModule(self.content_frame, self.data_manager, self.user)
        elif module_name == 'billing':
            BillingModule(self.content_frame, self.data_manager, self.user)
        elif module_name == 'bill_reports':
            BillReportsModule(self.content_frame, self.data_manager, self.user)
        elif module_name == 'analytics':
            AnalyticsModule(self.content_frame, self.data_manager, self.user)
        elif module_name == 'emergency':
            EmergencyModule(self.content_frame, self.data_manager, self.user)
    
    def load_default_module(self):
        """Load default module on startup"""
        self.load_module('dashboard')
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            
            # Return to login
            login_root = tk.Tk()
            LoginWindow(login_root, self.data_manager)
            login_root.mainloop()

# ==================== DASHBOARD MODULE ====================

class DashboardModule:
    """Main Dashboard with Statistics and Charts"""
    
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="📊 Dashboard Overview", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        tk.Label(title_frame, text=datetime.now().strftime("%B %d, %Y  %I:%M %p"),
                font=('Arial', 11), bg='white', fg='#7f8c8d').pack(side='right')
        
        # Statistics Cards
        self.create_stat_cards()
        
        # Charts Section
        self.create_charts()
        
        # Quick Actions
        self.create_quick_actions()
    
    def create_stat_cards(self):
        """Create statistics cards"""
        stats_frame = tk.Frame(self.parent, bg='white')
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # Get statistics
        patients = self.data_manager.get_patients()
        doctors = self.data_manager.get_doctors()
        appointments = self.data_manager.get_appointments()
        bills = self.data_manager.get_bills()
        
        total_revenue = sum(bill['total'] for bill in bills if bill.get('status') == 'Paid')
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_appointments = [a for a in appointments if a.get('date') == today]
        
        stats = [
            {'title': 'Total Patients', 'value': len(patients), 'icon': '🏥', 'color': '#3498db'},
            {'title': 'Doctors', 'value': len(doctors), 'icon': '👨‍⚕️', 'color': '#2ecc71'},
            {'title': 'Today Appointments', 'value': len(today_appointments), 'icon': '📅', 'color': '#e74c3c'},
            {'title': 'Total Revenue', 'value': f'₹{total_revenue:,.2f}', 'icon': '💰', 'color': '#f39c12'}
        ]
        
        for stat in stats:
            self.create_stat_card(stats_frame, stat)
    
    def create_stat_card(self, parent, stat):
        card = tk.Frame(parent, bg=stat['color'], relief='raised', bd=2)
        card.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # Icon
        tk.Label(card, text=stat['icon'], font=('Arial', 40), 
                bg=stat['color'], fg='white').pack(pady=(20, 10))
        
        # Value
        tk.Label(card, text=str(stat['value']), font=('Arial', 24, 'bold'),
                bg=stat['color'], fg='white').pack()
        
        # Title
        tk.Label(card, text=stat['title'], font=('Arial', 12),
                bg=stat['color'], fg='white').pack(pady=(5, 20))
    
    def create_charts(self):
        """Create visualization charts"""
        charts_frame = tk.Frame(self.parent, bg='white')
        charts_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left chart - Patient Trends
        left_chart_frame = tk.Frame(charts_frame, bg='white', relief='raised', bd=1)
        left_chart_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left_chart_frame, text="📈 Patient Visit Trends", font=('Arial', 12, 'bold'),
                bg='white').pack(pady=10)
        
        self.create_line_chart(left_chart_frame)
        
        # Right chart - Disease Distribution
        right_chart_frame = tk.Frame(charts_frame, bg='white', relief='raised', bd=1)
        right_chart_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(right_chart_frame, text="🥧 Disease Distribution", font=('Arial', 12, 'bold'),
                bg='white').pack(pady=10)
        
        self.create_pie_chart(right_chart_frame)
    
    def create_line_chart(self, parent):
        """Create line chart for patient trends"""
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Sample data - last 7 days
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        patients = [15, 23, 18, 28, 32, 25, 20]
        
        ax.plot(days, patients, marker='o', linewidth=2, markersize=8, color='#3498db')
        ax.set_ylabel('Number of Patients')
        ax.set_title('Weekly Patient Visits')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_pie_chart(self, parent):
        """Create pie chart for disease distribution"""
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Get disease data
        patients = self.data_manager.get_patients()
        disease_count = {}
        for patient in patients:
            disease = patient.get('disease', 'Unknown')
            disease_count[disease] = disease_count.get(disease, 0) + 1
        
        if disease_count:
            labels = list(disease_count.keys())
            sizes = list(disease_count.values())
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_quick_actions(self):
        """Create quick action buttons"""
        action_frame = tk.Frame(self.parent, bg='white')
        action_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(action_frame, text="⚡ Quick Actions", font=('Arial', 14, 'bold'),
                bg='white').pack(anchor='w', pady=(0, 10))
        
        button_frame = tk.Frame(action_frame, bg='white')
        button_frame.pack(fill='x')
        
        actions = [
            {'text': '➕ Add Patient', 'color': '#3498db'},
            {'text': '📅 New Appointment', 'color': '#2ecc71'},
            {'text': '💊 Pharmacy', 'color': '#e74c3c'},
            {'text': '📋 View Reports', 'color': '#f39c12'}
        ]
        
        for action in actions:
            btn = tk.Button(button_frame, text=action['text'], font=('Arial', 11, 'bold'),
                          bg=action['color'], fg='white', relief='flat', cursor='hand2',
                          padx=20, pady=10)
            btn.pack(side='left', padx=10)

# ==================== PATIENTS MODULE ====================

class PatientsModule:
    """Patient Management Module"""
    
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        
        self.create_widgets()
        self.load_patients()
    
    def create_widgets(self):
        # Title Bar
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="🏥 Patient Management", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        # Action Buttons
        btn_frame = tk.Frame(title_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="➕ Add Patient", font=('Arial', 10, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=self.add_patient, padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', relief='flat', cursor='hand2',
                 command=self.load_patients, padx=15, pady=8).pack(side='left', padx=5)
        
        # Search Bar
        search_frame = tk.Frame(self.parent, bg='white')
        search_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(search_frame, text="🔍 Search:", font=('Arial', 11),
                bg='white').pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_patients())
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 11), width=40)
        search_entry.pack(side='left', ipady=5)
        
        # Table Frame
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollbars
        v_scroll = tk.Scrollbar(table_frame, orient='vertical')
        v_scroll.pack(side='right', fill='y')
        
        h_scroll = tk.Scrollbar(table_frame, orient='horizontal')
        h_scroll.pack(side='bottom', fill='x')
        
        # Treeview
        columns = ('ID', 'Name', 'Age', 'Gender', 'Disease', 'Doctor', 'Admit Date', 'Contact', 'Blood Group')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', rowheight=30, font=('Arial', 10))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background='#34495e', foreground='white')
        
        # Context Menu
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Double-1>', self.view_patient)
    
    def load_patients(self):
        """Load all patients into table"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        patients = self.data_manager.get_patients()
        
        for patient in patients:
            self.tree.insert('', 'end', values=(
                patient['id'],
                patient['name'],
                patient['age'],
                patient['gender'],
                patient['disease'],
                patient['doctor'],
                patient['admit_date'],
                patient['contact'],
                patient.get('blood_group', 'N/A')
            ))
    
    def search_patients(self):
        """Search patients by name or ID"""
        search_term = self.search_var.get().lower()
        
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        patients = self.data_manager.get_patients()
        
        for patient in patients:
            if (search_term in patient['name'].lower() or 
                search_term in patient['id'].lower()):
                self.tree.insert('', 'end', values=(
                    patient['id'],
                    patient['name'],
                    patient['age'],
                    patient['gender'],
                    patient['disease'],
                    patient['doctor'],
                    patient['admit_date'],
                    patient['contact'],
                    patient.get('blood_group', 'N/A')
                ))
    
    def add_patient(self):
        """Open dialog to add new patient"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Patient")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f'500x600+{x}+{y}')
        
        # Form
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        fields = {}
        
        # Patient ID (auto-generated)
        patients = self.data_manager.get_patients()
        new_id = self.data_manager.generate_id('P', patients)
        
        tk.Label(form_frame, text=f"Patient ID: {new_id}", font=('Arial', 11, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Fields
        field_list = [
            ('Name', 'name'),
            ('Age', 'age'),
            ('Gender', 'gender'),
            ('Disease', 'disease'),
            ('Contact', 'contact'),
            ('Address', 'address'),
            ('Blood Group', 'blood_group'),
            ('Doctor', 'doctor')
        ]
        
        for i, (label, key) in enumerate(field_list, start=1):
            tk.Label(form_frame, text=f"{label}:", font=('Arial', 10)).grid(
                row=i, column=0, sticky='w', pady=5)
            
            if key == 'gender':
                fields[key] = ttk.Combobox(form_frame, values=['Male', 'Female', 'Other'], 
                                          state='readonly', font=('Arial', 10), width=28)
            elif key == 'doctor':
                doctors = self.data_manager.get_doctors()
                doctor_names = [d['name'] for d in doctors]
                fields[key] = ttk.Combobox(form_frame, values=doctor_names, 
                                          state='readonly', font=('Arial', 10), width=28)
            elif key == 'blood_group':
                fields[key] = ttk.Combobox(form_frame, values=['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'], 
                                          state='readonly', font=('Arial', 10), width=28)
            else:
                fields[key] = tk.Entry(form_frame, font=('Arial', 10), width=30)
            
            fields[key].grid(row=i, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=len(field_list)+1, column=0, columnspan=2, pady=20)
        
        def save_patient():
            patient_data = {
                'id': new_id,
                'admit_date': datetime.now().strftime("%Y-%m-%d")
            }
            
            for key, widget in fields.items():
                value = widget.get().strip()
                if not value and key in ['name', 'age', 'gender', 'doctor']:
                    messagebox.showerror("Error", f"{key.title()} is required!")
                    return
                patient_data[key] = value
            
            self.data_manager.add_patient(patient_data)
            messagebox.showinfo("Success", "Patient added successfully!")
            dialog.destroy()
            self.load_patients()
        
        tk.Button(btn_frame, text="💾 Save", font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=save_patient, padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                 command=dialog.destroy, padx=20, pady=10).pack(side='left', padx=10)
    
    def view_patient(self, event):
        """View patient details"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        patient_id = item['values'][0]
        
        patient = self.data_manager.get_patient_by_id(patient_id)
        if not patient:
            return
        
        # Create view dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Patient Details - {patient['name']}")
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f'600x500+{x}+{y}')
        
        # Header
        header = tk.Frame(dialog, bg='#3498db', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text=f"👤 {patient['name']}", font=('Arial', 18, 'bold'),
                bg='#3498db', fg='white').pack(pady=10)
        tk.Label(header, text=f"Patient ID: {patient['id']}", font=('Arial', 11),
                bg='#3498db', fg='white').pack()
        
        # Details
        details_frame = tk.Frame(dialog, padx=30, pady=20)
        details_frame.pack(fill='both', expand=True)
        
        details = [
            ('Age', patient.get('age', 'N/A')),
            ('Gender', patient.get('gender', 'N/A')),
            ('Blood Group', patient.get('blood_group', 'N/A')),
            ('Disease', patient.get('disease', 'N/A')),
            ('Doctor', patient.get('doctor', 'N/A')),
            ('Contact', patient.get('contact', 'N/A')),
            ('Address', patient.get('address', 'N/A')),
            ('Admit Date', patient.get('admit_date', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(details):
            tk.Label(details_frame, text=f"{label}:", font=('Arial', 11, 'bold')).grid(
                row=i, column=0, sticky='w', pady=8)
            tk.Label(details_frame, text=str(value), font=('Arial', 11)).grid(
                row=i, column=1, sticky='w', padx=20, pady=8)
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="✏️ Edit", font=('Arial', 10, 'bold'),
                 bg='#f39c12', fg='white', relief='flat', cursor='hand2',
                 command=lambda: self.edit_patient(patient_id, dialog), padx=20, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🗑️ Delete", font=('Arial', 10, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                 command=lambda: self.delete_patient(patient_id, dialog), padx=20, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Close", font=('Arial', 10, 'bold'),
                 bg='#95a5a6', fg='white', relief='flat', cursor='hand2',
                 command=dialog.destroy, padx=20, pady=8).pack(side='left', padx=5)
    
    def edit_patient(self, patient_id, parent_dialog):
        """Edit patient details"""
        patient = self.data_manager.get_patient_by_id(patient_id)
        if not patient:
            return
        
        parent_dialog.destroy()
        
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Edit Patient - {patient['name']}")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f'500x600+{x}+{y}')
        
        # Form
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        fields = {}
        
        tk.Label(form_frame, text=f"Patient ID: {patient['id']}", font=('Arial', 11, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        field_list = [
            ('Name', 'name'),
            ('Age', 'age'),
            ('Gender', 'gender'),
            ('Disease', 'disease'),
            ('Contact', 'contact'),
            ('Address', 'address'),
            ('Blood Group', 'blood_group'),
            ('Doctor', 'doctor')
        ]
        
        for i, (label, key) in enumerate(field_list, start=1):
            tk.Label(form_frame, text=f"{label}:", font=('Arial', 10)).grid(
                row=i, column=0, sticky='w', pady=5)
            
            if key == 'gender':
                fields[key] = ttk.Combobox(form_frame, values=['Male', 'Female', 'Other'], 
                                          state='readonly', font=('Arial', 10), width=28)
                fields[key].set(patient.get(key, ''))
            elif key == 'doctor':
                doctors = self.data_manager.get_doctors()
                doctor_names = [d['name'] for d in doctors]
                fields[key] = ttk.Combobox(form_frame, values=doctor_names, 
                                          state='readonly', font=('Arial', 10), width=28)
                fields[key].set(patient.get(key, ''))
            elif key == 'blood_group':
                fields[key] = ttk.Combobox(form_frame, values=['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'], 
                                          state='readonly', font=('Arial', 10), width=28)
                fields[key].set(patient.get(key, ''))
            else:
                fields[key] = tk.Entry(form_frame, font=('Arial', 10), width=30)
                fields[key].insert(0, patient.get(key, ''))
            
            fields[key].grid(row=i, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=len(field_list)+1, column=0, columnspan=2, pady=20)
        
        def update_patient():
            updated_data = {}
            for key, widget in fields.items():
                value = widget.get().strip()
                if value:
                    updated_data[key] = value
            
            self.data_manager.update_patient(patient_id, updated_data)
            messagebox.showinfo("Success", "Patient updated successfully!")
            dialog.destroy()
            self.load_patients()
        
        tk.Button(btn_frame, text="💾 Update", font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=update_patient, padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                 command=dialog.destroy, padx=20, pady=10).pack(side='left', padx=10)
    
    def delete_patient(self, patient_id, parent_dialog):
        """Delete patient"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient?"):
            self.data_manager.delete_patient(patient_id)
            messagebox.showinfo("Success", "Patient deleted successfully!")
            parent_dialog.destroy()
            self.load_patients()
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        # Select row under mouse
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            
            menu = tk.Menu(self.parent, tearoff=0)
            menu.add_command(label="👁️ View Details", command=lambda: self.view_patient(event))
            menu.add_command(label="✏️ Edit", command=lambda: self.edit_patient_from_context())
            menu.add_command(label="🗑️ Delete", command=lambda: self.delete_patient_from_context())
            
            menu.post(event.x_root, event.y_root)
    
    def edit_patient_from_context(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            patient_id = item['values'][0]
            self.edit_patient(patient_id, tk.Toplevel())
    
    def delete_patient_from_context(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            patient_id = item['values'][0]
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient?"):
                self.data_manager.delete_patient(patient_id)
                messagebox.showinfo("Success", "Patient deleted successfully!")
                self.load_patients()

# ==================== DOCTORS MODULE ====================

class DoctorsModule:
    """Doctor Management Module"""
    
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        
        self.create_widgets()
        self.load_doctors()
    
    def create_widgets(self):
        # Title Bar
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="👨‍⚕️ Doctor Management", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        # Action Buttons
        btn_frame = tk.Frame(title_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="➕ Add Doctor", font=('Arial', 10, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=self.add_doctor, padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', relief='flat', cursor='hand2',
                 command=self.load_doctors, padx=15, pady=8).pack(side='left', padx=5)
        
        # Table Frame
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollbars
        v_scroll = tk.Scrollbar(table_frame, orient='vertical')
        v_scroll.pack(side='right', fill='y')
        
        h_scroll = tk.Scrollbar(table_frame, orient='horizontal')
        h_scroll.pack(side='bottom', fill='x')
        
        # Treeview
        columns = ('ID', 'Name', 'Specialization', 'Contact', 'Email', 'Availability')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        self.tree.bind('<Double-1>', self.view_doctor)
    
    def load_doctors(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        doctors = self.data_manager.get_doctors()
        
        for doctor in doctors:
            self.tree.insert('', 'end', values=(
                doctor['id'],
                doctor['name'],
                doctor['specialization'],
                doctor['contact'],
                doctor.get('email', 'N/A'),
                doctor['availability']
            ))
    
    def add_doctor(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Doctor")
        dialog.geometry("500x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f'500x500+{x}+{y}')
        
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        fields = {}
        
        doctors = self.data_manager.get_doctors()
        new_id = self.data_manager.generate_id('D', doctors)
        
        tk.Label(form_frame, text=f"Doctor ID: {new_id}", font=('Arial', 11, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 20))
        
        field_list = [
            ('Name', 'name'),
            ('Specialization', 'specialization'),
            ('Contact', 'contact'),
            ('Email', 'email'),
            ('Availability', 'availability')
        ]
        
        for i, (label, key) in enumerate(field_list, start=1):
            tk.Label(form_frame, text=f"{label}:", font=('Arial', 10)).grid(
                row=i, column=0, sticky='w', pady=10)
            
            fields[key] = tk.Entry(form_frame, font=('Arial', 10), width=30)
            fields[key].grid(row=i, column=1, pady=10, padx=(10, 0))
        
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=len(field_list)+1, column=0, columnspan=2, pady=20)
        
        def save_doctor():
            doctor_data = {'id': new_id}
            
            for key, widget in fields.items():
                value = widget.get().strip()
                if not value:
                    messagebox.showerror("Error", f"{key.title()} is required!")
                    return
                doctor_data[key] = value
            
            self.data_manager.add_doctor(doctor_data)
            messagebox.showinfo("Success", "Doctor added successfully!")
            dialog.destroy()
            self.load_doctors()
        
        tk.Button(btn_frame, text="💾 Save", font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=save_doctor, padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                 command=dialog.destroy, padx=20, pady=10).pack(side='left', padx=10)
    
    def view_doctor(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        doctor_id = item['values'][0]
        
        doctors = self.data_manager.get_doctors()
        doctor = next((d for d in doctors if d['id'] == doctor_id), None)
        
        if not doctor:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Doctor Details - {doctor['name']}")
        dialog.geometry("600x400")
        dialog.transient(self.parent)
        
        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f'600x400+{x}+{y}')
        
        header = tk.Frame(dialog, bg='#2ecc71', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text=f"👨‍⚕️ {doctor['name']}", font=('Arial', 18, 'bold'),
                bg='#2ecc71', fg='white').pack(pady=10)
        tk.Label(header, text=f"Doctor ID: {doctor['id']}", font=('Arial', 11),
                bg='#2ecc71', fg='white').pack()
        
        details_frame = tk.Frame(dialog, padx=30, pady=20)
        details_frame.pack(fill='both', expand=True)
        
        details = [
            ('Specialization', doctor.get('specialization', 'N/A')),
            ('Contact', doctor.get('contact', 'N/A')),
            ('Email', doctor.get('email', 'N/A')),
            ('Availability', doctor.get('availability', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(details):
            tk.Label(details_frame, text=f"{label}:", font=('Arial', 11, 'bold')).grid(
                row=i, column=0, sticky='w', pady=10)
            tk.Label(details_frame, text=str(value), font=('Arial', 11)).grid(
                row=i, column=1, sticky='w', padx=20, pady=10)
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="❌ Close", font=('Arial', 10, 'bold'),
                 bg='#95a5a6', fg='white', relief='flat', cursor='hand2',
                 command=dialog.destroy, padx=20, pady=8).pack()

# ==================== REMAINING MODULES (Abbreviated for space) ====================

class AppointmentsModule:
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        self.notification_manager = NotificationManager(data_manager)
        self.create_widgets()
        self.load_appointments()
    
    def create_widgets(self):
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="📅 Appointment Management", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        btn_frame = tk.Frame(title_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="➕ New Appointment", font=('Arial', 10, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=self.add_appointment, padx=15, pady=8).pack(side='left', padx=5)
        
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        v_scroll = tk.Scrollbar(table_frame, orient='vertical')
        v_scroll.pack(side='right', fill='y')
        
        columns = ('ID', 'Patient', 'Doctor', 'Date', 'Time', 'Duration', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=v_scroll.set)
        v_scroll.config(command=self.tree.yview)
        
        # Define column widths and headings
        widths = [100, 150, 150, 100, 100, 100, 100]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
    
    def _convert_duration_to_minutes(self, duration_str):
        """Convert duration string to minutes"""
        if 'min' in duration_str:
            return int(duration_str.split()[0])
        elif 'hour' in duration_str:
            hours = float(duration_str.split()[0])
            return int(hours * 60)
        return 30  # default to 30 minutes
    
    def _check_appointment_conflict(self, appointments, start_time, end_time, doctor_id):
        """Check if the appointment time conflicts with existing appointments"""
        doctor_id = doctor_id.split(' - ')[0]  # Extract doctor ID from the combobox value
        for appt in appointments:
            if appt['doctor_id'] == doctor_id:
                # Convert appointment time to datetime
                appt_date = datetime.strptime(f"{appt['date']} {appt['time']}", "%Y-%m-%d %H:%M")
                # Calculate appointment end time based on duration
                duration = self._convert_duration_to_minutes(appt.get('duration', '30 min'))
                appt_end = appt_date + timedelta(minutes=duration)
                
                # Check for overlap
                if not (end_time <= appt_date or start_time >= appt_end):
                    return True
        return False

    def _get_doctor_availability(self, doctor_id):
        """Load doctor availability from data/doctors.json if present.

        Returns availability dict like { 'days': [...], 'timing': '09:00 AM - 05:00 PM' }
        or None if not found.
        """
        try:
            import json
            with open(os.path.join(os.path.dirname(__file__), 'data', 'doctors.json'), 'r') as f:
                data = json.load(f)
                doctors = data.get('doctors', []) if isinstance(data, dict) else data
                for d in doctors:
                    if d.get('id') == doctor_id or d.get('id') == doctor_id.split(' - ')[0]:
                        return d.get('availability')
        except Exception:
            return None

    def _is_within_doctor_availability(self, availability, appt_datetime, duration_minutes):
        """Check whether a datetime and duration fits into doctor's availability.

        availability: {'days': ['Monday', ...], 'timing': '09:00 AM - 05:00 PM'}
        """
        if not availability:
            return True  # If unknown, allow and rely on conflict checks

        # Check day
        appt_day = appt_datetime.strftime('%A')
        days = availability.get('days', [])
        if days and appt_day not in days:
            return False

        # Parse timing
        timing = availability.get('timing', '')
        try:
            parts = timing.split('-')
            start_str = parts[0].strip()
            end_str = parts[1].strip()

            # Convert like '09:00 AM' to 24h time
            start_dt = datetime.strptime(start_str, '%I:%M %p')
            end_dt = datetime.strptime(end_str, '%I:%M %p')

            appt_time_only = appt_datetime.replace(year=start_dt.year, month=start_dt.month, day=start_dt.day)
            # Construct todays start/end with the appt date
            start_today = appt_datetime.replace(hour=start_dt.hour, minute=start_dt.minute, second=0, microsecond=0)
            end_today = appt_datetime.replace(hour=end_dt.hour, minute=end_dt.minute, second=0, microsecond=0)

            appt_end = appt_datetime + timedelta(minutes=duration_minutes)

            # If end time crosses the end_today, it's not allowed
            if appt_datetime < start_today or appt_end > end_today:
                return False
        except Exception:
            # If parsing fails, be permissive and allow booking (but conflict checks still apply)
            return True

        return True

    def load_appointments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        appointments = self.data_manager.get_appointments()
        
        for appt in appointments:
            # Display appointment info using stored names
            self.tree.insert('', 'end', values=(
                appt['id'],
                f"{appt['patient_name']} ({appt['patient_id']})",
                f"{appt['doctor']} ({appt['doctor_id']})",
                appt['date'],
                appt['time'],
                appt.get('duration', '30 min'),
                'EMERGENCY' if appt.get('emergency') else appt['status']
            ))
    
    def add_appointment(self):
        # Create appointment dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Appointment")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f'500x600+{x}+{y}')
        
        # Form frame
        form_frame = tk.Frame(dialog)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(form_frame, text="Schedule New Appointment", 
                font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Patient Selection
        tk.Label(form_frame, text="Patient:", font=('Arial', 11)).pack(anchor='w')
        patients = self.data_manager.get_patients()
        patient_options = [f"{p['id']} - {p['name']}" for p in patients]
        self.patient_var = tk.StringVar()
        patient_cb = ttk.Combobox(form_frame, textvariable=self.patient_var, 
                                 values=patient_options, width=40)
        patient_cb.pack(fill='x', pady=(0, 15))
        
        # Doctor Selection
        tk.Label(form_frame, text="Doctor:", font=('Arial', 11)).pack(anchor='w')
        doctors = [d for d in self.data_manager.get_users() if d.get('role') == 'doctor']
        doctor_options = [f"{d['id']} - {d['name']}" for d in doctors]
        self.doctor_var = tk.StringVar()
        doctor_cb = ttk.Combobox(form_frame, textvariable=self.doctor_var,
                                values=doctor_options, width=40)
        doctor_cb.pack(fill='x', pady=(0, 15))
        
        # Doctor availability display
        self.doctor_avail_label_var = tk.StringVar(value="Availability: N/A")
        tk.Label(form_frame, textvariable=self.doctor_avail_label_var, font=('Arial', 10, 'italic')).pack(anchor='w', pady=(0,10))

        def on_doctor_selected(event=None):
            sel = self.doctor_var.get()
            if not sel:
                self.doctor_avail_label_var.set("Availability: N/A")
                return
            doc_id = sel.split(' - ')[0]
            availability = self._get_doctor_availability(doc_id)
            if availability:
                days = ', '.join(availability.get('days', []))
                timing = availability.get('timing', 'N/A')
                self.doctor_avail_label_var.set(f"Availability: {days} | {timing}")
            else:
                self.doctor_avail_label_var.set("Availability: N/A")

        doctor_cb.bind('<<ComboboxSelected>>', on_doctor_selected)
        
        # Date Selection with Calendar
        date_frame = tk.Frame(form_frame)
        date_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(date_frame, text="Date:", font=('Arial', 11)).pack(side='left')
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(date_frame, textvariable=self.date_var, 
                            font=('Arial', 11), width=30)
        date_entry.pack(side='left', padx=(5, 5))
        
        self.date_picker = DatePicker(self.parent, self.date_var)
        tk.Button(date_frame, text="📅", command=self.date_picker.show_calendar,
                 font=('Arial', 11)).pack(side='left')
        
        # Time and Duration Selection
        time_frame = tk.Frame(form_frame)
        time_frame.pack(fill='x', pady=(0, 15))
        
        # Time Selection
        time_subframe = tk.Frame(time_frame)
        time_subframe.pack(side='left', fill='x', expand=True)
        
        tk.Label(time_subframe, text="Time:", font=('Arial', 11)).pack(anchor='w')
        time_select = tk.Frame(time_subframe)
        time_select.pack(fill='x', pady=(5, 0))
        
        hours = [str(i).zfill(2) for i in range(9, 18)]  # 9 AM to 5 PM
        minutes = ['00', '15', '30', '45']
        
        self.hour_var = tk.StringVar(value="09")
        self.minute_var = tk.StringVar(value="00")
        
        hour_cb = ttk.Combobox(time_select, textvariable=self.hour_var,
                              values=hours, width=5)
        hour_cb.pack(side='left')
        
        tk.Label(time_select, text=":", font=('Arial', 11)).pack(side='left', padx=5)
        
        minute_cb = ttk.Combobox(time_select, textvariable=self.minute_var,
                                values=minutes, width=5)
        minute_cb.pack(side='left')
        
        # Duration Selection
        duration_subframe = tk.Frame(time_frame)
        duration_subframe.pack(side='right', fill='x', expand=True, padx=(20, 0))
        
        tk.Label(duration_subframe, text="Duration:", font=('Arial', 11)).pack(anchor='w')
        duration_select = tk.Frame(duration_subframe)
        duration_select.pack(fill='x', pady=(5, 0))
        
        durations = ['15 min', '30 min', '45 min', '1 hour', '1.5 hours', '2 hours']
        self.duration_var = tk.StringVar(value='30 min')
        duration_cb = ttk.Combobox(duration_select, textvariable=self.duration_var,
                                  values=durations, width=15)
        duration_cb.pack(side='left')
        
        # Purpose/Notes
        tk.Label(form_frame, text="Purpose:", font=('Arial', 11)).pack(anchor='w')
        self.purpose_text = tk.Text(form_frame, height=4, font=('Arial', 11))
        self.purpose_text.pack(fill='x', pady=(0, 15))
        
        # Emergency Checkbox
        self.emergency_var = tk.BooleanVar()
        tk.Checkbutton(form_frame, text="Emergency Appointment", 
                      variable=self.emergency_var,
                      font=('Arial', 11)).pack(anchor='w', pady=(0, 15))
        
        # Buttons frame
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        tk.Button(btn_frame, text="Cancel", font=('Arial', 11),
                 command=dialog.destroy, width=15).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Schedule", font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white', command=lambda: self.save_appointment(dialog),
                 width=15).pack(side='right', padx=5)
                 
    def save_appointment(self, dialog):
        # Get values from form
        patient = self.patient_var.get()
        doctor = self.doctor_var.get()
        time_str = f"{self.hour_var.get()}:{self.minute_var.get()}"
        date_str = self.date_var.get()
        duration = self.duration_var.get()
        
        # Validation
        if not patient or not doctor:
            messagebox.showerror("Error", "Please select both patient and doctor")
            return
            
        # Split IDs from display strings
        patient_id = patient.split(' - ')[0]
        patient_name = patient.split(' - ')[1]
        doctor_id = doctor.split(' - ')[0]
        doctor_name = doctor.split(' - ')[1]
        
        # Convert appointment time to datetime
        try:
            appt_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            # Check if appointment is in the past
            if appt_datetime < datetime.now():
                messagebox.showerror("Error", "Cannot schedule appointments in the past")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid date or time format")
            return
            
        # Convert duration to minutes and calculate end time
        duration_minutes = self._convert_duration_to_minutes(duration)
        appt_end = appt_datetime + timedelta(minutes=duration_minutes)

        # Get existing appointments
        appointments = self.data_manager.get_appointments()

        # Check doctor availability (if defined in data/doctors.json)
        doctor_id = doctor.split(' - ')[0]
        availability = self._get_doctor_availability(doctor_id)
        if availability and not self._is_within_doctor_availability(availability, appt_datetime, duration_minutes):
            timing = availability.get('timing', 'N/A')
            days = ', '.join(availability.get('days', [])) if availability.get('days') else 'N/A'
            messagebox.showerror("Not Available", 
                                 f"Selected doctor is not available on {appt_datetime.strftime('%A')} at {time_str}.\n"
                                 f"Availability: {days} | {timing}")
            return

        # Check for conflicts with existing appointments
        if self._check_appointment_conflict(appointments, appt_datetime, appt_end, doctor):
            messagebox.showerror("Error", "This time slot conflicts with an existing appointment")
            return

        # Generate new appointment ID properly using data manager
        new_id = self.data_manager.generate_id('A', appointments)
        
        # Create appointment data
        appointment_data = {
            'id': new_id,
            'patient_id': patient_id,
            'patient_name': patient_name,
            'doctor_id': doctor_id,
            'doctor': doctor_name,  # Add full doctor name for display
            'date': date_str,
            'time': time_str,
            'duration': duration,
            'purpose': self.purpose_text.get('1.0', 'end-1c'),
            'status': 'Scheduled',
            'emergency': self.emergency_var.get()
        }
        
        # Save to appointment list and update data
        try:
            self.data_manager.add_appointment(appointment_data)
            messagebox.showinfo("Success", 
                              f"Appointment {new_id} scheduled successfully!\n" + 
                              f"Patient: {patient_name}\n" +
                              f"Doctor: {doctor_name}\n" +
                              f"Date: {date_str}\n" +
                              f"Time: {time_str}")
            dialog.destroy()
            self.load_appointments()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save appointment: {str(e)}")
            return
        
        # Send notification
        try:
            self.notification_manager.send_appointment_confirmation(appointment_data)
        except Exception as e:
            messagebox.showwarning("Warning", 
                                 "Appointment saved but notification failed to send\n" +
                                 f"Error: {str(e)}")

class PharmacyModule:
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        self.create_widgets()
        self.load_medicines()
    
    def create_widgets(self):
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="💊 Pharmacy Management", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        # Action Buttons
        btn_frame = tk.Frame(title_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="➕ Add Medicine", font=('Arial', 10, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=self.add_medicine, padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🔄 Update Stock", font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', relief='flat', cursor='hand2',
                 command=self.update_stock, padx=15, pady=8).pack(side='left', padx=5)
        
        # Search frame
        search_frame = tk.Frame(self.parent, bg='white')
        search_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(search_frame, text="🔍 Search:", font=('Arial', 11),
                bg='white').pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_medicines())
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                              font=('Arial', 11), width=40)
        search_entry.pack(side='left')
        
        # Stock alerts frame
        alert_frame = tk.Frame(self.parent, bg='#fff3cd', relief='raised', bd=1)
        alert_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(alert_frame, text="⚠️ Low Stock Alerts", font=('Arial', 11, 'bold'),
                bg='#fff3cd', fg='#856404').pack(pady=5)
        
        self.alert_list = tk.Text(alert_frame, height=3, font=('Arial', 10),
                                 bg='#fff3cd', fg='#856404', relief='flat')
        self.alert_list.pack(fill='x', padx=10, pady=5)
        
        # Table frame
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollbars
        y_scroll = tk.Scrollbar(table_frame, orient='vertical')
        y_scroll.pack(side='right', fill='y')
        
        # Treeview
        columns = ('ID', 'Medicine Name', 'Category', 'Stock', 'Price', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                yscrollcommand=y_scroll.set)
        
        y_scroll.config(command=self.tree.yview)
        
        # Define column widths and headings
        widths = [100, 200, 150, 100, 100, 100]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        # Bind events
        self.tree.bind('<Double-1>', self.view_medicine)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def load_medicines(self):
        """Load medicines and update low stock alerts"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        medicines = self.data_manager.get_medicines()
        low_stock_items = []
        
        for med in medicines:
            stock = med['stock']
            status = "🟢 In Stock" if stock > 20 else "🟡 Low Stock" if stock > 0 else "🔴 Out of Stock"
            
            if stock <= 20:  # Low stock threshold
                low_stock_items.append(f"⚠️ {med['name']}: {stock} units remaining")
            
            self.tree.insert('', 'end', values=(
                med['id'],
                med['name'],
                med['category'],
                stock,
                f"${med['price']:.2f}",
                status
            ))
        
        # Update alerts
        self.alert_list.delete('1.0', 'end')
        if low_stock_items:
            self.alert_list.insert('1.0', '\n'.join(low_stock_items))
        else:
            self.alert_list.insert('1.0', "✅ All items sufficiently stocked")
    
    def search_medicines(self):
        """Search medicines by name or category"""
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        medicines = self.data_manager.get_medicines()
        
        for med in medicines:
            if (search_term in med['name'].lower() or 
                search_term in med['category'].lower()):
                stock = med['stock']
                status = "🟢 In Stock" if stock > 20 else "🟡 Low Stock" if stock > 0 else "🔴 Out of Stock"
                
                self.tree.insert('', 'end', values=(
                    med['id'],
                    med['name'],
                    med['category'],
                    stock,
                    f"${med['price']:.2f}",
                    status
                ))
    
    def add_medicine(self):
        """Add new medicine to inventory"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Medicine")
        dialog.geometry("500x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        tk.Label(form_frame, text="Add New Medicine", 
                font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Form fields
        fields = {}
        
        # Generate new ID
        medicines = self.data_manager.get_medicines()
        new_id = self.data_manager.generate_id('M', medicines)
        
        tk.Label(form_frame, text=f"Medicine ID: {new_id}", 
                font=('Arial', 11, 'bold')).pack(pady=(0, 20))
        
        # Fields with validation
        field_list = [
            ("Medicine Name", "name", r"^[A-Za-z0-9\s\-]{3,50}$"),
            ("Category", "category", r"^[A-Za-z\s]{3,30}$"),
            ("Stock Quantity", "stock", r"^\d+$"),
            ("Price (₹)", "price", r"^\d*\.?\d*$")
        ]
        
        for label, key, pattern in field_list:
            frame = tk.Frame(form_frame)
            frame.pack(fill='x', pady=10)
            
            tk.Label(frame, text=f"{label}:", 
                    font=('Arial', 11, 'bold')).pack(anchor='w')
            
            if key == "category":
                categories = ["Pain Relief", "Antibiotic", "Antiviral", "Cardiovascular",
                            "Respiratory", "Gastrointestinal", "Diabetes", "Other"]
                fields[key] = ttk.Combobox(frame, values=categories,
                                         font=('Arial', 11), width=30)
                fields[key].pack(pady=5)
            else:
                entry = tk.Entry(frame, font=('Arial', 11), width=30)
                
                def validate(P, pattern=pattern):
                    import re
                    if P == "": return True
                    return bool(re.match(pattern, P))
                
                vcmd = (frame.register(validate), '%P')
                entry.config(validate='key', validatecommand=vcmd)
                entry.pack(pady=5)
                fields[key] = entry
        
        # Description
        tk.Label(form_frame, text="Description:", 
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        
        description = tk.Text(form_frame, height=4, font=('Arial', 11))
        description.pack(fill='x', pady=5)
        
        def save_medicine():
            # Validate fields
            for key, widget in fields.items():
                value = widget.get().strip()
                if not value:
                    messagebox.showerror("Error", f"{key.title()} is required!")
                    return
            
            try:
                stock = int(fields['stock'].get())
                price = float(fields['price'].get())
            except ValueError:
                messagebox.showerror("Error", "Invalid stock or price value!")
                return
            
            medicine_data = {
                'id': new_id,
                'name': fields['name'].get(),
                'category': fields['category'].get(),
                'stock': stock,
                'price': price,
                'description': description.get('1.0', 'end-1c')
            }
            
            self.data_manager.add_medicine(medicine_data)
            messagebox.showinfo("Success", "Medicine added successfully!")
            dialog.destroy()
            self.load_medicines()
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Save", font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=save_medicine, padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                 command=dialog.destroy, padx=20, pady=10).pack(side='left', padx=10)
    
    def update_stock(self):
        """Update stock quantities"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine to update stock!")
            return
        
        item = self.tree.item(selected[0])
        medicine_id = item['values'][0]
        current_stock = item['values'][3]
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Update Stock")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        tk.Label(form_frame, text="Update Stock Quantity", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        tk.Label(form_frame, text=f"Medicine: {item['values'][1]}", 
                font=('Arial', 11)).pack(pady=5)
        
        tk.Label(form_frame, text=f"Current Stock: {current_stock}", 
                font=('Arial', 11)).pack(pady=5)
        
        # Stock adjustment
        adj_frame = tk.Frame(form_frame)
        adj_frame.pack(pady=20)
        
        tk.Label(adj_frame, text="Adjust by:", 
                font=('Arial', 11, 'bold')).pack(side='left')
        
        adj_var = tk.StringVar(value='+')
        ttk.Radiobutton(adj_frame, text="Add", variable=adj_var,
                       value='+').pack(side='left', padx=10)
        ttk.Radiobutton(adj_frame, text="Remove", variable=adj_var,
                       value='-').pack(side='left', padx=10)
        
        tk.Label(form_frame, text="Quantity:", 
                font=('Arial', 11, 'bold')).pack(pady=5)
        
        quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(form_frame, textvariable=quantity_var,
                                font=('Arial', 11), width=20)
        quantity_entry.pack(pady=5)
        
        def validate_quantity(P):
            return P.isdigit() or P == ""
        
        vcmd = (form_frame.register(validate_quantity), '%P')
        quantity_entry.config(validate='key', validatecommand=vcmd)
        
        def update():
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Please enter a positive number!")
                    return
                
                new_stock = current_stock + quantity if adj_var.get() == '+' else current_stock - quantity
                
                if new_stock < 0:
                    messagebox.showerror("Error", "Stock cannot be negative!")
                    return
                
                # Update in database
                medicines = self.data_manager.get_medicines()
                for med in medicines:
                    if med['id'] == medicine_id:
                        med['stock'] = new_stock
                        break
                
                self.data_manager.save_data(self.data_manager.pharmacy_file, medicines)
                
                messagebox.showinfo("Success", 
                                  f"Stock updated successfully!\n"
                                  f"New stock: {new_stock}")
                dialog.destroy()
                self.load_medicines()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")
        
        tk.Button(form_frame, text="🔄 Update Stock", font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=update, padx=20, pady=10).pack(pady=20)
    
    def view_medicine(self, event):
        """View medicine details"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        medicine_id = item['values'][0]
        
        medicines = self.data_manager.get_medicines()
        medicine = next((m for m in medicines if m['id'] == medicine_id), None)
        
        if not medicine:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"Medicine Details - {medicine['name']}")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        
        details_frame = tk.Frame(dialog, padx=30, pady=20)
        details_frame.pack(fill='both', expand=True)
        
        # Header with color-coded stock status
        stock = medicine['stock']
        if stock > 20:
            status_color = '#2ecc71'  # Green
            status_text = "In Stock"
        elif stock > 0:
            status_color = '#f1c40f'  # Yellow
            status_text = "Low Stock"
        else:
            status_color = '#e74c3c'  # Red
            status_text = "Out of Stock"
        
        header = tk.Frame(details_frame, bg=status_color)
        header.pack(fill='x', pady=(0, 20))
        
        tk.Label(header, text=medicine['name'], font=('Arial', 16, 'bold'),
                bg=status_color, fg='white').pack(pady=5)
        tk.Label(header, text=f"Status: {status_text}", font=('Arial', 11),
                bg=status_color, fg='white').pack(pady=5)
        
        # Details
        details = [
            ('ID', medicine['id']),
            ('Category', medicine['category']),
            ('Stock', medicine['stock']),
            ('Price', f"₹{medicine['price']:.2f}"),
            ('Description', medicine.get('description', 'N/A'))
        ]
        
        for label, value in details:
            frame = tk.Frame(details_frame)
            frame.pack(fill='x', pady=5)
            
            tk.Label(frame, text=f"{label}:", font=('Arial', 11, 'bold'),
                    width=15, anchor='w').pack(side='left')
            tk.Label(frame, text=str(value), font=('Arial', 11),
                    anchor='w').pack(side='left', padx=10)
        
        tk.Button(details_frame, text="Close", font=('Arial', 11),
                 command=dialog.destroy, padx=20, pady=5).pack(pady=20)
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            menu = tk.Menu(self.parent, tearoff=0)
            menu.add_command(label="👁️ View Details",
                           command=lambda: self.view_medicine(None))
            menu.add_command(label="🔄 Update Stock",
                           command=self.update_stock)
            
            menu.post(event.x_root, event.y_root)

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
        
        tk.Label(title_frame, text="� Billing Reports", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        # Action Buttons
        btn_frame = tk.Frame(title_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="🔄 Refresh", font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', relief='flat', cursor='hand2',
                 command=self.load_reports, padx=15, pady=8).pack(side='left', padx=5)
                 
        tk.Button(btn_frame, text="📊 Analytics", font=('Arial', 10, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=self.show_analytics, padx=15, pady=8).pack(side='left', padx=5)
        
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
                    values=["All", "Today", "This Week", "This Month", "Custom Range"],
                    state='readonly', width=15).pack(side='left')
        self.filter_var.trace('w', lambda *args: self.handle_filter_change())
        
        # Add Summary Cards
        summary_frame = tk.Frame(self.parent, bg='white')
        summary_frame.pack(fill='x', padx=20, pady=10)
        
        # Total Bills Card
        total_card = tk.Frame(summary_frame, bg='#3498db', padx=15, pady=10)
        total_card.pack(side='left', padx=5, fill='x', expand=True)
        self.total_bills_label = tk.Label(total_card, text="0", 
                                        font=('Arial', 20, 'bold'), fg='white', bg='#3498db')
        self.total_bills_label.pack()
        tk.Label(total_card, text="Total Bills", font=('Arial', 10),
                fg='white', bg='#3498db').pack()
        
        # Total Amount Card
        amount_card = tk.Frame(summary_frame, bg='#2ecc71', padx=15, pady=10)
        amount_card.pack(side='left', padx=5, fill='x', expand=True)
        self.total_amount_label = tk.Label(amount_card, text="₹0.00", 
                                         font=('Arial', 20, 'bold'), fg='white', bg='#2ecc71')
        self.total_amount_label.pack()
        tk.Label(amount_card, text="Total Amount", font=('Arial', 10),
                fg='white', bg='#2ecc71').pack()
        
        # Pending Amount Card
        pending_card = tk.Frame(summary_frame, bg='#e74c3c', padx=15, pady=10)
        pending_card.pack(side='left', padx=5, fill='x', expand=True)
        self.pending_amount_label = tk.Label(pending_card, text="₹0.00", 
                                           font=('Arial', 20, 'bold'), fg='white', bg='#e74c3c')
        self.pending_amount_label.pack()
        tk.Label(pending_card, text="Pending Amount", font=('Arial', 10),
                fg='white', bg='#e74c3c').pack()
        
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
    
    def handle_filter_change(self):
        """Handle date filter changes"""
        if self.filter_var.get() == "Custom Range":
            self.show_date_range_dialog()
        else:
            self.load_reports()
            
    def show_date_range_dialog(self):
        """Show dialog for custom date range selection"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Select Date Range")
        dialog.geometry("300x250")
        dialog.transient(self.parent)
        
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Start date
        tk.Label(content_frame, text="Start Date (YYYY-MM-DD):", 
                font=('Arial', 11)).pack(anchor='w')
        start_date = tk.Entry(content_frame, width=30)
        start_date.pack(fill='x', pady=(5, 15))
        start_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # End date
        tk.Label(content_frame, text="End Date (YYYY-MM-DD):", 
                font=('Arial', 11)).pack(anchor='w')
        end_date = tk.Entry(content_frame, width=30)
        end_date.pack(fill='x', pady=(5, 15))
        end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        def apply_filter():
            self.custom_date_range = (start_date.get(), end_date.get())
            self.load_reports()
            dialog.destroy()
        
        # Apply button
        tk.Button(content_frame, text="Apply Filter", font=('Arial', 11, 'bold'),
                 bg='#3498db', fg='white', command=apply_filter,
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(pady=20)
    
    def update_summary(self, bills):
        """Update summary cards with current filtered data"""
        total_bills = len(bills)
        total_amount = sum(float(b['total']) for b in bills)
        pending_amount = sum(float(b['total']) for b in bills 
                           if b['status'].upper() != 'PAID')
        
        self.total_bills_label.config(text=str(total_bills))
        self.total_amount_label.config(text=f"₹{total_amount:,.2f}")
        self.pending_amount_label.config(text=f"₹{pending_amount:,.2f}")
    
    def load_reports(self):
        """Load and filter bill reports"""
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
            elif filter_option == "Custom Range" and hasattr(self, 'custom_date_range'):
                start_date, end_date = self.custom_date_range
                bills = [b for b in bills if start_date <= b['date'] <= end_date]
        
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
        """View bill details with enhanced payment features"""
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
        dialog.geometry("700x600")
        dialog.transient(self.parent)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f'700x600+{x}+{y}')
        
        # Header
        header = tk.Frame(dialog, bg='#2ecc71', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text=f"Bill #{bill['bill_no']}", font=('Arial', 16, 'bold'),
                bg='#2ecc71', fg='white').pack(pady=(10, 5))
        tk.Label(header, text=f"Date: {bill['date']}", font=('Arial', 10),
                bg='#2ecc71', fg='white').pack()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Details tab
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="Bill Details")
        
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
                row=i, column=0, sticky='w', pady=10, padx=20)
            tk.Label(details_frame, text=str(value), font=('Arial', 11)).grid(
                row=i, column=1, sticky='w', padx=20, pady=10)
        
        # Payment tab
        payment_frame = ttk.Frame(notebook)
        notebook.add(payment_frame, text="Payment Management")
        
        # Payment status frame
        status_frame = tk.LabelFrame(payment_frame, text="Payment Status", padx=20, pady=10)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        status_color = '#2ecc71' if bill['status'].upper() == 'PAID' else '#e74c3c'
        tk.Label(status_frame, text=f"Current Status: {bill['status']}", 
                font=('Arial', 12, 'bold'), fg=status_color).pack(pady=5)
        
        # Payment amount frame
        amount_frame = tk.LabelFrame(payment_frame, text="Payment Amount", padx=20, pady=10)
        amount_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(amount_frame, text=f"Total Amount Due: ₹{bill['total']:.2f}", 
                font=('Arial', 12, 'bold')).pack(pady=5)
        
        if bill['status'].upper() != 'PAID':
            # Payment method frame
            method_frame = tk.LabelFrame(payment_frame, text="Update Payment", padx=20, pady=10)
            method_frame.pack(fill='x', padx=20, pady=10)
            
            # Payment method selection
            tk.Label(method_frame, text="Select Payment Method:", 
                    font=('Arial', 11)).pack(anchor='w')
            payment_method = tk.StringVar(value=bill['payment_method'])
            methods = ['Cash', 'Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Insurance']
            method_cb = ttk.Combobox(method_frame, textvariable=payment_method, 
                                   values=methods, state='readonly', width=30)
            method_cb.pack(pady=5, anchor='w')
            
            # Transaction details
            tk.Label(method_frame, text="Transaction ID:", 
                    font=('Arial', 11)).pack(anchor='w', pady=(10,0))
            transaction_id = tk.Entry(method_frame, width=32)
            transaction_id.pack(pady=5, anchor='w')
            
            tk.Label(method_frame, text="Additional Notes:", 
                    font=('Arial', 11)).pack(anchor='w', pady=(10,0))
            notes = tk.Text(method_frame, height=3, width=40)
            notes.pack(pady=5, anchor='w')
            
            # Mark as paid button
            def mark_as_paid():
                if not transaction_id.get().strip():
                    messagebox.showerror("Error", "Please enter transaction ID")
                    return
                    
                bill['status'] = 'PAID'
                bill['payment_method'] = payment_method.get()
                bill['transaction_id'] = transaction_id.get()
                bill['payment_date'] = datetime.now().strftime("%Y-%m-%d")
                bill['payment_notes'] = notes.get('1.0', 'end-1c')
                
                # Update bill in data manager
                self.data_manager.update_bill(bill)
                self.load_reports()
                
                messagebox.showinfo("Success", "Payment recorded successfully!")
                dialog.destroy()
            
            tk.Button(method_frame, text="✓ Mark as Paid", font=('Arial', 11, 'bold'),
                     bg='#2ecc71', fg='white', command=mark_as_paid,
                     relief='flat', cursor='hand2', padx=20, pady=10).pack(pady=20)
        
        else:
            # Payment details frame for paid bills
            paid_frame = tk.LabelFrame(payment_frame, text="Payment Details", padx=20, pady=10)
            paid_frame.pack(fill='x', padx=20, pady=10)
            
            paid_details = [
                ('Payment Date', bill.get('payment_date', '')),
                ('Transaction ID', bill.get('transaction_id', '')),
                ('Payment Method', bill['payment_method']),
                ('Notes', bill.get('payment_notes', ''))
            ]
            
            for i, (label, value) in enumerate(paid_details):
                tk.Label(paid_frame, text=f"{label}:", 
                        font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10 if i > 0 else 0))
                tk.Label(paid_frame, text=str(value), 
                        font=('Arial', 11)).pack(anchor='w', pady=5)
        
        # Actions Frame at the bottom
        actions_frame = tk.Frame(dialog)
        actions_frame.pack(fill='x', padx=20, pady=20)
        
        # Left side buttons
        left_btn_frame = tk.Frame(actions_frame)
        left_btn_frame.pack(side='left')
        
        tk.Button(left_btn_frame, text="🖨️ Print Bill", font=('Arial', 11, 'bold'),
                 bg='#3498db', fg='white', command=lambda: self.generate_bill_pdf(bill),
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
        
        tk.Button(left_btn_frame, text="📧 Email Bill", font=('Arial', 11, 'bold'),
                 bg='#27ae60', fg='white', command=lambda: self.email_bill(bill),
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
        
        # Right side buttons
        right_btn_frame = tk.Frame(actions_frame)
        right_btn_frame.pack(side='right')
        
        if bill['status'].upper() != 'PAID':
            tk.Button(right_btn_frame, text="� Quick Pay", font=('Arial', 11, 'bold'),
                     bg='#2ecc71', fg='white', command=lambda: self.quick_pay(bill, dialog),
                     relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
        
        tk.Button(right_btn_frame, text="❌ Close", font=('Arial', 11, 'bold'),
                 bg='#95a5a6', fg='white', command=dialog.destroy,
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Get bill status
            bill_values = self.tree.item(item)['values']
            bill_status = bill_values[6] if len(bill_values) > 6 else ''
            
            menu = tk.Menu(self.parent, tearoff=0)
            menu.add_command(label="👁️ View Bill Details",
                           command=lambda: self.view_bill(None))
            
            # Add payment related options based on status
            if bill_status.upper() != 'PAID':
                menu.add_command(label="💳 Quick Pay",
                               command=lambda: self.quick_pay_selected())
                menu.add_command(label="📝 Update Payment Status",
                               command=lambda: self.update_payment_status())
            
            menu.add_separator()
            menu.add_command(label="🖨️ Print Bill",
                           command=lambda: self.print_selected_bill())
            menu.add_command(label="📧 Email Bill",
                           command=lambda: self.email_selected_bill())
            menu.add_command(label="📋 Copy Bill No",
                           command=self.copy_bill_no)
            
            # Add admin options if user has privileges
            if hasattr(self.user, 'is_admin') and self.user.is_admin:
                menu.add_separator()
                menu.add_command(label="🗑️ Delete Bill",
                               command=lambda: self.delete_bill())
            
            menu.post(event.x_root, event.y_root)
    
    def quick_pay_selected(self):
        """Open quick pay for selected bill"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        bill_no = item['values'][0]
        
        bills = self.data_manager.get_bills()
        bill = next((b for b in bills if b['bill_no'] == bill_no), None)
        
        if bill:
            self.quick_pay(bill, None)
    
    def update_payment_status(self):
        """Update payment status for selected bill"""
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
        dialog.title("Update Payment Status")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Status selection
        tk.Label(content_frame, text="Select Status:", 
                font=('Arial', 11)).pack(anchor='w')
        status_var = tk.StringVar(value=bill['status'])
        statuses = ['Pending', 'Paid', 'Partially Paid', 'Cancelled']
        status_cb = ttk.Combobox(content_frame, textvariable=status_var,
                               values=statuses, state='readonly')
        status_cb.pack(fill='x', pady=(5, 15))
        
        # Payment method
        tk.Label(content_frame, text="Payment Method:", 
                font=('Arial', 11)).pack(anchor='w')
        method_var = tk.StringVar(value=bill['payment_method'])
        methods = ['Cash', 'Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Insurance']
        method_cb = ttk.Combobox(content_frame, textvariable=method_var,
                               values=methods, state='readonly')
        method_cb.pack(fill='x', pady=(5, 15))
        
        # Notes
        tk.Label(content_frame, text="Notes:", 
                font=('Arial', 11)).pack(anchor='w')
        notes_text = tk.Text(content_frame, height=4)
        notes_text.pack(fill='x', pady=(5, 15))
        
        def update_status():
            bill['status'] = status_var.get()
            bill['payment_method'] = method_var.get()
            bill['payment_notes'] = notes_text.get('1.0', 'end-1c')
            if status_var.get().upper() == 'PAID':
                bill['payment_date'] = datetime.now().strftime("%Y-%m-%d")
            
            self.data_manager.update_bill(bill)
            self.load_reports()
            dialog.destroy()
            messagebox.showinfo("Success", "Payment status updated successfully!")
        
        # Update button
        tk.Button(content_frame, text="Update Status", font=('Arial', 11, 'bold'),
                 bg='#3498db', fg='white', command=update_status,
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(pady=20)
    
    def print_selected_bill(self):
        """Print the selected bill"""
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        bill_no = item['values'][0]
        
        bills = self.data_manager.get_bills()
        bill = next((b for b in bills if b['bill_no'] == bill_no), None)
        
        if bill:
            self.generate_bill_pdf(bill)
    
    def email_selected_bill(self):
        """Email the selected bill"""
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        bill_no = item['values'][0]
        
        bills = self.data_manager.get_bills()
        bill = next((b for b in bills if b['bill_no'] == bill_no), None)
        
        if bill:
            self.email_bill(bill)
    
    def delete_bill(self):
        """Delete the selected bill (admin only)"""
        if not (hasattr(self.user, 'is_admin') and self.user.is_admin):
            messagebox.showerror("Error", "You don't have permission to delete bills")
            return
            
        selected = self.tree.selection()
        if not selected:
            return
            
        if not messagebox.askyesno("Confirm Delete", 
                                  "Are you sure you want to delete this bill?"):
            return
            
        item = self.tree.item(selected[0])
        bill_no = item['values'][0]
        
        self.data_manager.delete_bill(bill_no)
        self.load_reports()
        messagebox.showinfo("Success", "Bill deleted successfully!")
    
    def show_analytics(self):
        """Show billing analytics in a new window"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Billing Analytics")
        dialog.geometry("800x600")
        dialog.transient(self.parent)
        
        # Notebook for different analytics views
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Revenue Trends
        revenue_frame = ttk.Frame(notebook)
        notebook.add(revenue_frame, text="Revenue Trends")
        self.create_revenue_chart(revenue_frame)
        
        # Payment Methods
        payment_frame = ttk.Frame(notebook)
        notebook.add(payment_frame, text="Payment Methods")
        self.create_payment_methods_chart(payment_frame)
        
        # Status Overview
        status_frame = ttk.Frame(notebook)
        notebook.add(status_frame, text="Status Overview")
        self.create_status_overview(status_frame)
        
        # Bills by Month
        monthly_frame = ttk.Frame(notebook)
        notebook.add(monthly_frame, text="Monthly Analysis")
        self.create_monthly_analysis(monthly_frame)
    
    def create_revenue_chart(self, parent):
        """Create revenue trends chart"""
        bills = self.data_manager.get_bills()
        
        # Group bills by date
        dates = {}
        for bill in bills:
            date = datetime.strptime(bill['date'], "%Y-%m-%d")
            if date not in dates:
                dates[date] = 0
            dates[date] += float(bill['total'])
        
        # Sort dates and prepare data
        sorted_dates = sorted(dates.keys())
        revenues = [dates[date] for date in sorted_dates]
        
        # Create figure and plot
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(sorted_dates, revenues, marker='o')
        ax.set_title('Daily Revenue Trend')
        ax.set_xlabel('Date')
        ax.set_ylabel('Revenue (₹)')
        ax.grid(True)
        
        # Rotate date labels for better readability
        plt.xticks(rotation=45)
        
        # Add the plot to the frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add summary statistics
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        stats = [
            ('Total Revenue', f"₹{sum(revenues):,.2f}"),
            ('Average Daily Revenue', f"₹{sum(revenues)/len(revenues):,.2f}"),
            ('Highest Daily Revenue', f"₹{max(revenues):,.2f}"),
            ('Lowest Daily Revenue', f"₹{min(revenues):,.2f}")
        ]
        
        for i, (label, value) in enumerate(stats):
            tk.Label(stats_frame, text=f"{label}:", font=('Arial', 11, 'bold')).grid(
                row=i//2, column=i%2*2, sticky='e', padx=5, pady=5)
            tk.Label(stats_frame, text=value, font=('Arial', 11)).grid(
                row=i//2, column=i%2*2+1, sticky='w', padx=5, pady=5)
    
    def create_payment_methods_chart(self, parent):
        """Create payment methods distribution chart"""
        bills = self.data_manager.get_bills()
        
        # Count payment methods
        methods = {}
        for bill in bills:
            method = bill['payment_method']
            if method not in methods:
                methods[method] = 0
            methods[method] += 1
        
        # Create pie chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Payment method count
        labels = list(methods.keys())
        sizes = list(methods.values())
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax1.set_title('Payment Methods Distribution')
        
        # Payment method by amount
        method_amounts = {}
        for bill in bills:
            method = bill['payment_method']
            if method not in method_amounts:
                method_amounts[method] = 0
            method_amounts[method] += float(bill['total'])
        
        labels = list(method_amounts.keys())
        sizes = list(method_amounts.values())
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax2.set_title('Payment Methods by Amount')
        
        # Add the plot to the frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add statistics
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        for method in methods:
            tk.Label(stats_frame, text=f"{method}:", font=('Arial', 11, 'bold')).pack(
                side='left', padx=10)
            tk.Label(stats_frame, text=f"₹{method_amounts[method]:,.2f}", 
                    font=('Arial', 11)).pack(side='left', padx=5)
    
    def create_status_overview(self, parent):
        """Create payment status overview"""
        bills = self.data_manager.get_bills()
        
        # Group by status
        status_counts = {}
        status_amounts = {}
        for bill in bills:
            status = bill['status'].upper()
            if status not in status_counts:
                status_counts[status] = 0
                status_amounts[status] = 0
            status_counts[status] += 1
            status_amounts[status] += float(bill['total'])
        
        # Create bar chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Status count
        status_labels = list(status_counts.keys())
        counts = list(status_counts.values())
        ax1.bar(status_labels, counts)
        ax1.set_title('Bills by Status')
        ax1.set_ylabel('Number of Bills')
        
        # Status amounts
        amounts = list(status_amounts.values())
        ax2.bar(status_labels, amounts)
        ax2.set_title('Amount by Status')
        ax2.set_ylabel('Amount (₹)')
        
        # Rotate labels for better readability
        ax1.tick_params(axis='x', rotation=45)
        ax2.tick_params(axis='x', rotation=45)
        
        # Add the plot to the frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_monthly_analysis(self, parent):
        """Create monthly bills analysis"""
        bills = self.data_manager.get_bills()
        
        # Group by month
        monthly_data = {}
        for bill in bills:
            date = datetime.strptime(bill['date'], "%Y-%m-%d")
            month_key = date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'count': 0,
                    'amount': 0,
                    'paid': 0,
                    'pending': 0
                }
            
            monthly_data[month_key]['count'] += 1
            amount = float(bill['total'])
            monthly_data[month_key]['amount'] += amount
            
            if bill['status'].upper() == 'PAID':
                monthly_data[month_key]['paid'] += amount
            else:
                monthly_data[month_key]['pending'] += amount
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 4))
        
        months = list(monthly_data.keys())
        paid_amounts = [monthly_data[m]['paid'] for m in months]
        pending_amounts = [monthly_data[m]['pending'] for m in months]
        
        # Create stacked bar chart
        ax.bar(months, paid_amounts, label='Paid')
        ax.bar(months, pending_amounts, bottom=paid_amounts, label='Pending')
        
        ax.set_title('Monthly Revenue Analysis')
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount (₹)')
        ax.legend()
        
        # Rotate labels for better readability
        plt.xticks(rotation=45)
        
        # Add the plot to the frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def copy_bill_no(self):
        """Copy selected bill number to clipboard"""
        selected = self.tree.selection()
        if selected:
            bill_no = self.tree.item(selected[0])['values'][0]
            self.parent.clipboard_clear()
            self.parent.clipboard_append(bill_no)
            
    def email_bill(self, bill):
        """Email bill to patient"""
        # First generate the PDF
        pdf_path = self.generate_bill_pdf(bill)
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Email Bill")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f'400x300+{x}+{y}')
        
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Email form
        tk.Label(content_frame, text="Recipient Email:", 
                font=('Arial', 11)).pack(anchor='w')
        email_entry = tk.Entry(content_frame, width=40)
        email_entry.pack(fill='x', pady=(5, 15))
        
        tk.Label(content_frame, text="Subject:", 
                font=('Arial', 11)).pack(anchor='w')
        subject_entry = tk.Entry(content_frame, width=40)
        subject_entry.insert(0, f"Bill Statement - {bill['bill_no']}")
        subject_entry.pack(fill='x', pady=(5, 15))
        
        tk.Label(content_frame, text="Message:", 
                font=('Arial', 11)).pack(anchor='w')
        message_text = tk.Text(content_frame, height=5)
        default_msg = f"Dear {bill['patient_name']},\n\nPlease find attached your bill statement ({bill['bill_no']}).\n\nRegards,\nSmart Hospital"
        message_text.insert('1.0', default_msg)
        message_text.pack(fill='x', pady=(5, 15))
        
        def send_email():
            # Here you would implement actual email sending logic
            # For now, just show a success message
            messagebox.showinfo("Success", "Bill has been sent successfully!")
            dialog.destroy()
        
        # Send button
        tk.Button(content_frame, text="📧 Send Email", font=('Arial', 11, 'bold'),
                 bg='#27ae60', fg='white', command=send_email,
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(pady=20)
    
    def quick_pay(self, bill, parent_dialog):
        """Quick payment processing"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Quick Payment")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f'500x400+{x}+{y}')
        
        # Header
        header = tk.Frame(dialog, bg='#2ecc71', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="Quick Payment", font=('Arial', 16, 'bold'),
                bg='#2ecc71', fg='white').pack(pady=(10, 5))
        tk.Label(header, text=f"Amount: ₹{bill['total']:.2f}", font=('Arial', 12),
                bg='#2ecc71', fg='white').pack()
        
        content_frame = tk.Frame(dialog, padx=30, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Payment method
        tk.Label(content_frame, text="Select Payment Method:", 
                font=('Arial', 11, 'bold')).pack(anchor='w')
        payment_method = tk.StringVar(value='UPI')
        methods = ['UPI', 'Credit Card', 'Debit Card', 'Net Banking']
        
        for method in methods:
            tk.Radiobutton(content_frame, text=method, variable=payment_method,
                         value=method, font=('Arial', 10)).pack(anchor='w', pady=5)
        
        # Transaction frame
        transaction_frame = tk.LabelFrame(content_frame, text="Transaction Details",
                                        padx=20, pady=10)
        transaction_frame.pack(fill='x', pady=15)
        
        tk.Label(transaction_frame, text="Transaction ID:", 
                font=('Arial', 10)).pack(anchor='w')
        transaction_id = tk.Entry(transaction_frame, width=40)
        transaction_id.pack(fill='x', pady=5)
        
        def process_payment():
            if not transaction_id.get().strip():
                messagebox.showerror("Error", "Please enter transaction ID")
                return
                
            # Update bill status
            # Update bill in-memory (not yet saved)
            bill['_pending_payment'] = {
                'status': 'PAID',
                'payment_method': payment_method.get(),
                'transaction_id': transaction_id.get(),
                'payment_date': datetime.now().strftime("%Y-%m-%d")
            }
            # Enable Save button
            save_btn.config(state='normal')
            messagebox.showinfo("Processed", "Payment processed locally. Click Save to persist the payment.")
        
        # Process payment button
        # Action buttons: Process -> Save -> Print
        action_frame = tk.Frame(content_frame)
        action_frame.pack(pady=20)

        process_button = tk.Button(action_frame, text="💳 Process", font=('Arial', 11, 'bold'),
                 bg='#f39c12', fg='white', command=process_payment,
                 relief='flat', cursor='hand2', padx=20, pady=10)
        process_button.pack(side='left', padx=5)

        def save_payment():
            pending = bill.get('_pending_payment')
            if not pending:
                messagebox.showerror("Error", "No processed payment to save. Click Process first.")
                return
            # Apply pending payment fields to bill and persist
            bill['status'] = f"PAID"
            bill['payment_method'] = pending.get('payment_method')
            bill['transaction_id'] = pending.get('transaction_id')
            bill['payment_date'] = pending.get('payment_date')
            # Remove pending marker
            if '_pending_payment' in bill:
                del bill['_pending_payment']

            # Persist
            self.data_manager.update_bill(bill)
            self.load_reports()
            messagebox.showinfo("Saved", "Payment saved successfully.")
            # Enable print button
            print_btn.config(state='normal')
            save_btn.config(state='disabled')
            # Close parent dialog if requested
            # Do not auto-close so user can print/email

        save_btn = tk.Button(action_frame, text="💾 Save", font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white', command=save_payment,
                 relief='flat', cursor='hand2', padx=20, pady=10)
        save_btn.pack(side='left', padx=5)
        save_btn.config(state='disabled')

        def print_bill():
            # Generate PDF (or regenerate) and open it
            pdf_path = self.generate_bill_pdf(bill)
            try:
                if os.name == 'nt':
                    os.startfile(pdf_path)
                else:
                    # Try xdg-open / open
                    import subprocess
                    opener = 'xdg-open' if os.name == 'posix' else 'open'
                    subprocess.Popen([opener, pdf_path])
            except Exception as e:
                messagebox.showerror("Error", f"Unable to open PDF: {e}")

        print_btn = tk.Button(action_frame, text="🖨️ Print", font=('Arial', 11, 'bold'),
                 bg='#3498db', fg='white', command=print_bill,
                 relief='flat', cursor='hand2', padx=20, pady=10)
        print_btn.pack(side='left', padx=5)
        print_btn.config(state='disabled')
            
    def generate_bill_pdf(self, bill_data):
        """Generate PDF bill with QR code and enhanced features"""
        # Get downloads folder path based on OS
        if os.name == 'nt':  # Windows
            downloads_path = os.path.expanduser('~\\Downloads')
        else:  # Unix/Linux/Mac
            downloads_path = os.path.expanduser('~/Downloads')
            
        filename = os.path.join(downloads_path, f"bill_{bill_data['bill_no']}.pdf")
        
        # Use SimpleDocTemplate for better formatting
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Prepare story elements
        story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='Watermark', textColor=colors.lightgrey))
        
        # Create header with logo (if available)
        try:
            logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
            if os.path.exists(logo_path):
                img = Image(logo_path)
                img.drawHeight = 1.5*inch
                img.drawWidth = 1.5*inch
                story.append(img)
        except:
            pass
        
        # Create header
        header_text = "SMART HOSPITAL"
        story.append(Paragraph(header_text, styles['Center']))
        story.append(Spacer(1, 12))
        
        # Hospital details
        hospital_details = """123 Medical Center Drive<br/>
                            Healthcare City, State 12345<br/>
                            Phone: (555) 123-4567<br/>
                            Email: info@smarthospital.com<br/>
                            GST No: XXXXXXXXXXXX"""
        story.append(Paragraph(hospital_details, styles['Center']))
        story.append(Spacer(1, 20))
        
        # Bill header with status watermark
        story.append(Paragraph("BILL STATEMENT", styles['Center']))
        if bill_data['status'].upper() == 'PAID':
            story.append(Paragraph("PAID", ParagraphStyle(
                'Watermark',
                parent=styles['Normal'],
                fontSize=60,
                textColor=colors.green,
                alignment=TA_CENTER
            )))
        story.append(Spacer(1, 20))
        
        # Generate QR Code for bill verification
        qr_data = f"Bill#{bill_data['bill_no']}|Date:{bill_data['date']}|Amount:₹{bill_data['total']}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(downloads_path, f"temp_qr_{bill_data['bill_no']}.png")
        qr_img.save(qr_path)
        
        # Bill and patient information with QR code
        info_data = [
            ['Bill No:', bill_data['bill_no'], Image(qr_path)],
            ['Date:', bill_data['date'], ''],
            ['Patient ID:', bill_data['patient_id'], ''],
            ['Patient Name:', bill_data['patient_name'], ''],
            ['Payment Method:', bill_data['payment_method'], ''],
            ['Status:', bill_data['status'], '']
        ]
        
        info_table = Table(info_data, colWidths=[120, 280, 100])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('SPAN', (2, 0), (2, -1)),  # Span QR code across rows
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Services with prices
        services = bill_data.get('service_details', [])
        if not services:  # Fallback to old format if service_details not available
            services = [{'name': s, 'amount': ''} for s in bill_data['services'].split(', ')]
            
        service_data = [['Service', 'Amount', 'Date']]
        for service in services:
            service_data.append([
                service.get('name', ''),
                f"₹{service.get('amount', '')}" if service.get('amount') else '',
                service.get('date', '')
            ])
        
        service_table = Table(service_data, colWidths=[300, 100, 100])
        service_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(service_table)
        story.append(Spacer(1, 20))
        
        # Payment details with additional information
        payment_data = [
            ['Subtotal:', f"₹{bill_data['subtotal']:.2f}"],
            ['Tax (10%):', f"₹{bill_data['tax']:.2f}"],
            ['Discount:', f"-₹{bill_data.get('discount', 0):.2f}"],
            ['Total Amount:', f"₹{bill_data['total']:.2f}"]
        ]
        
        # Add payment status details
        if bill_data['status'].upper() == 'PAID':
            payment_data.extend([
                ['Payment Date:', bill_data.get('payment_date', '')],
                ['Transaction ID:', bill_data.get('transaction_id', '')],
                ['Payment Method:', bill_data['payment_method']]
            ])
        
        payment_table = Table(payment_data, colWidths=[450, 50])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, -4), (-1, -4), 1, colors.black),
        ]))
        story.append(payment_table)
        story.append(Spacer(1, 30))
        
        # Terms and conditions
        terms_text = """Terms & Conditions:<br/>
                       1. All payments are non-refundable<br/>
                       2. Please keep this bill for future reference<br/>
                       3. Any disputes must be reported within 7 days"""
        story.append(Paragraph(terms_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Footer with payment instructions if unpaid
        if bill_data['status'].upper() != 'PAID':
            payment_instructions = """Payment Methods:<br/>
                                   UPI: hospital@upi<br/>
                                   Bank: XXXX Bank<br/>
                                   A/C: XXXXXXXXXXXX<br/>
                                   IFSC: XXXXX0000"""
            story.append(Paragraph(payment_instructions, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Footer text
        footer_text = f"""Thank you for choosing Smart Hospital!<br/>
                         For any queries, please contact our billing department.<br/>
                         Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        story.append(Paragraph(footer_text, styles['Center']))
        
        # Build PDF
        doc.build(story)
        
        # Clean up temporary QR code file
        try:
            os.remove(qr_path)
        except:
            pass
            
        return filename

        # Remarks / Interpretation
        remarks_frame = tk.Frame(dialog, padx=20, pady=10)
        remarks_frame.pack(fill='x')
        tk.Label(remarks_frame, text="Remarks / Interpretation:", font=('Arial', 12, 'bold')).pack(anchor='w')
        remarks_text = tk.Text(remarks_frame, height=6, font=('Arial', 11))
        remarks_text.pack(fill='x')
        remarks_text.insert('1.0', bill.get('remarks', ''))
        remarks_text.config(state='disabled')

        # Open PDF button if available
        pdf_path = os.path.join(self.data_manager.data_dir, f"bill_{bill_no}.pdf")
        btn_frame = tk.Frame(dialog, pady=10)
        btn_frame.pack()
        if os.path.exists(pdf_path):
            tk.Button(btn_frame, text="�️ Print Bill", font=('Arial', 11, 'bold'),
                     bg='#3498db', fg='white', command=lambda: os.startfile(pdf_path),
                     relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="❌ Close", font=('Arial', 11, 'bold'),
                 bg='#95a5a6', fg='white', command=dialog.destroy,
                 relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
    

        
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
        
        # Build PDF
        doc.build(story)
        return filename


        # Apply patient filter if available
        patient_filter = 'All'
        if hasattr(self, 'patient_filter_var'):
            patient_filter = self.patient_filter_var.get()

        if patient_filter and patient_filter != 'All':
            pid = patient_filter.split(' - ')[0]
            reports = [r for r in reports if r.get('patient_id') == pid]

        for report in reports:
            self.tree.insert('', 'end', values=(
                report['id'],
                report['patient_name'],
                report['test'],
                report.get('result', 'N/A'),
                report['date'],
                report.get('status', 'Completed'),
                report.get('remarks', '')[:50] + '...' if report.get('remarks', '') else ''
            ))
    
    def create_widgets(self):
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="BILLING MANAGEMENT", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        btn_frame = tk.Frame(title_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="➕ New Bill", font=('Arial', 10, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=self.create_bill, padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="↩️ Undo Last", font=('Arial', 10, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                 command=self.undo_last, padx=15, pady=8).pack(side='left', padx=5)
        
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('Bill No', 'Patient', 'Services', 'Total', 'Payment Method', 'Date', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        self.tree.bind('<Double-1>', self.view_bill)
    
    def load_bills(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        bills = self.data_manager.get_bills()
        
        for bill in bills:
            self.tree.insert('', 'end', values=(
                bill['bill_no'],
                bill['patient_name'],
                bill['services'],
                f"₹{bill['total']:.2f}",
                bill['payment_method'],
                bill['date'],
                bill['status']
            ))
    
    def create_bill(self):
        """Create new bill with payment options"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Create New Bill")
        dialog.geometry("600x700")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f'600x700+{x}+{y}')
        
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Bill number
        bills = self.data_manager.get_bills()
        new_bill_no = self.data_manager.generate_id('B', bills)
        
        tk.Label(form_frame, text=f"Bill Number: {new_bill_no}", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Patient selection
        tk.Label(form_frame, text="Select Patient:", font=('Arial', 11)).pack(anchor='w', pady=(10, 5))
        patients = self.data_manager.get_patients()
        patient_names = [f"{p['id']} - {p['name']}" for p in patients]
        patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(form_frame, textvariable=patient_var, values=patient_names, 
                                     state='readonly', font=('Arial', 10), width=40)
        patient_combo.pack(pady=5)
        
        # Services
        tk.Label(form_frame, text="Services/Description:", font=('Arial', 11)).pack(anchor='w', pady=(10, 5))
        services_text = tk.Text(form_frame, height=4, font=('Arial', 10), width=50)
        services_text.pack(pady=5)
        
        # Amount
        tk.Label(form_frame, text="Subtotal Amount (₹):", font=('Arial', 11)).pack(anchor='w', pady=(10, 5))
        subtotal_entry = tk.Entry(form_frame, font=('Arial', 11), width=20)
        subtotal_entry.pack(pady=5)
        
        # Tax (10%)
        tk.Label(form_frame, text="Tax (10%):", font=('Arial', 10)).pack(anchor='w', pady=(5, 0))
        tax_label = tk.Label(form_frame, text="₹0.00", font=('Arial', 11, 'bold'))
        tax_label.pack(anchor='w', pady=2)
        
        # Total
        tk.Label(form_frame, text="Total Amount:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(5, 0))
        total_label = tk.Label(form_frame, text="₹0.00", font=('Arial', 14, 'bold'), fg='#2ecc71')
        total_label.pack(anchor='w', pady=2)
        
        def calculate_total(*args):
            try:
                subtotal = float(subtotal_entry.get())
                tax = subtotal * 0.10
                total = subtotal + tax
                tax_label.config(text=f"₹{tax:.2f}")
                total_label.config(text=f"₹{total:.2f}")
            except:
                tax_label.config(text="₹0.00")
                total_label.config(text="₹0.00")
        
        subtotal_entry.bind('<KeyRelease>', calculate_total)
        
        # Payment method
        tk.Label(form_frame, text="Payment Method:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(15, 5))
        
        payment_var = tk.StringVar(value="Cash")
        payment_methods = ['Cash', 'Credit Card', 'Debit Card', 'Online Payment', 'Insurance']
        
        payment_frame = tk.Frame(form_frame)
        payment_frame.pack(anchor='w', pady=5)
        
        for method in payment_methods:
            rb = tk.Radiobutton(payment_frame, text=method, variable=payment_var, value=method,
                               font=('Arial', 10))
            rb.pack(anchor='w')
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(pady=20)
        
        def save_bill():
            if not patient_var.get():
                messagebox.showerror("Error", "Please select a patient")
                return
            
            services = services_text.get("1.0", "end-1c").strip()
            if not services:
                messagebox.showerror("Error", "Please enter services")
                return
            
            try:
                subtotal = float(subtotal_entry.get())
                tax = subtotal * 0.10
                total = subtotal + tax
            except:
                messagebox.showerror("Error", "Invalid amount")
                return
            
            patient_id = patient_var.get().split(' - ')[0]
            patient_name = patient_var.get().split(' - ')[1]
            
            payment_method = payment_var.get()
            bill_data = {
                'bill_no': new_bill_no,
                'patient_id': patient_id,
                'patient_name': patient_name,
                'services': services,
                'subtotal': subtotal,
                'tax': tax,
                'total': total,
                'payment_method': payment_method,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'status': 'Pending'
            }
            
            # Create receipts folder if it doesn't exist
            receipts_path = os.path.join(os.path.dirname(__file__), 'receipts')
            os.makedirs(receipts_path, exist_ok=True)
            
            def show_bill_and_confirm():
                # First generate the bill
                self.generate_bill_pdf(bill_data)
                
                # Get paths
                if os.name == 'nt':  # Windows
                    downloads_path = os.path.expanduser('~\\Downloads')
                else:  # Unix/Linux/Mac
                    downloads_path = os.path.expanduser('~/Downloads')
                
                bill_path = os.path.join(downloads_path, f"bill_{bill_data['bill_no']}.pdf")
                
                # Show confirmation dialog with paid button
                confirm_dialog = tk.Toplevel(dialog)
                confirm_dialog.title("Confirm Payment")
                confirm_dialog.geometry("300x150")
                confirm_dialog.transient(dialog)
                
                tk.Label(confirm_dialog, 
                        text=f"Bill generated and saved.\nTotal Amount: ₹{total:.2f}",
                        font=('Arial', 12),
                        justify='center').pack(pady=(20,10))
                
                def mark_as_paid():
                    # Update status and save
                    bill_data['status'] = f'PAID via {payment_method}'
                    self.data_manager.add_bill(bill_data)
                    
                    # Copy to receipts folder
                    receipt_file = os.path.join(receipts_path, f"receipt_{new_bill_no}.pdf")
                    import shutil
                    shutil.copy2(bill_path, receipt_file)
                    
                    messagebox.showinfo("Payment Complete", 
                        f"Payment recorded successfully!\nStatus: {bill_data['status']}\nReceipt saved to receipts folder")
                    confirm_dialog.destroy()
                    dialog.destroy()
                    self.load_bills()
                
                tk.Button(confirm_dialog, text="✔️ Mark as Paid",
                         font=('Arial', 11, 'bold'),
                         bg='#2ecc71', fg='white',
                         command=mark_as_paid,
                         padx=20, pady=10).pack(pady=20)
                
                # Center the dialog
                confirm_dialog.update_idletasks()
                x = dialog.winfo_x() + (dialog.winfo_width() // 2) - (confirm_dialog.winfo_width() // 2)
                y = dialog.winfo_y() + (dialog.winfo_height() // 2) - (confirm_dialog.winfo_height() // 2)
                confirm_dialog.geometry(f"+{x}+{y}")
                confirm_dialog.grab_set()
            
            # Handle different payment methods
            if payment_method == 'Cash':
                # For cash, show simple verification
                payment_dialog = tk.Toplevel(dialog)
                payment_dialog.title("Cash Payment")
                payment_dialog.geometry("300x200")
                payment_dialog.transient(dialog)
                
                tk.Label(payment_dialog, text="Cash Payment",
                        font=('Arial', 16, 'bold')).pack(pady=(20,10))
                tk.Label(payment_dialog, text=f"Amount to Collect: ₹{total:.2f}",
                        font=('Arial', 12)).pack(pady=5)
                
                tk.Button(payment_dialog, text="✔️ Cash Received",
                         font=('Arial', 11, 'bold'),
                         bg='#2ecc71', fg='white',
                         command=lambda: [payment_dialog.destroy(), show_bill_and_confirm()],
                         padx=20, pady=10).pack(pady=20)
                
                # Center dialog
                payment_dialog.update_idletasks()
                x = dialog.winfo_x() + (dialog.winfo_width() // 2) - (payment_dialog.winfo_width() // 2)
                y = dialog.winfo_y() + (dialog.winfo_height() // 2) - (payment_dialog.winfo_height() // 2)
                payment_dialog.geometry(f"+{x}+{y}")
                payment_dialog.grab_set()
            else:
                # For card/other payments, show QR and payment confirmation dialog
                payment_dialog = tk.Toplevel(dialog)
                payment_dialog.title(f"{payment_method} Payment")
                payment_dialog.geometry("400x600")
                payment_dialog.transient(dialog)
                
                # Payment info
                tk.Label(payment_dialog, text=f"{payment_method} Payment", 
                        font=('Arial', 16, 'bold')).pack(pady=(20,10))
                tk.Label(payment_dialog, text=f"Amount: ₹{total:.2f}", 
                        font=('Arial', 14)).pack(pady=5)
                tk.Label(payment_dialog, text=f"Bill No: {new_bill_no}", 
                        font=('Arial', 12)).pack(pady=5)
                
                # Generate QR code for payment
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr_data = f"BILL:{new_bill_no}|AMOUNT:{total}|METHOD:{payment_method}"
                qr.add_data(qr_data)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert QR to PhotoImage
                from PIL import ImageTk
                qr_photo = ImageTk.PhotoImage(qr_img)
                
                # Display QR
                qr_label = tk.Label(payment_dialog, image=qr_photo)
                qr_label.image = qr_photo  # Keep reference
                qr_label.pack(pady=20)
                
                # Payment Instructions
                instructions = {
                    'Credit Card': "1. Scan QR with bank app\n2. Enter card details\n3. Complete payment\n4. Click Done below",
                    'Debit Card': "1. Scan QR with bank app\n2. Enter card details\n3. Complete payment\n4. Click Done below",
                    'Insurance': "1. Scan QR for policy details\n2. Submit to insurance portal\n3. Wait for approval\n4. Click Done after approval",
                    'Online Payment': "1. Scan QR with payment app\n2. Complete the transfer\n3. Save transaction ID\n4. Click Done below"
                }
                
                tk.Label(payment_dialog, text=instructions.get(payment_method, "Scan QR to complete payment"),
                        font=('Arial', 11), justify='left').pack(pady=20)
                
                # Done button
                tk.Button(payment_dialog, text="✔️ Payment Complete", font=('Arial', 12, 'bold'),
                         bg='#2ecc71', fg='white', command=lambda: [payment_dialog.destroy(), show_bill_and_confirm()],
                         padx=20, pady=10).pack(pady=20)
                
                # Center the payment dialog
                payment_dialog.update_idletasks()
                x = dialog.winfo_x() + (dialog.winfo_width() // 2) - (payment_dialog.winfo_width() // 2)
                y = dialog.winfo_y() + (dialog.winfo_height() // 2) - (payment_dialog.winfo_height() // 2)
                payment_dialog.geometry(f"+{x}+{y}")
                payment_dialog.grab_set()
        
        tk.Button(btn_frame, text="💾 Save & Generate PDF", font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', cursor='hand2',
                 command=save_bill, padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                 command=dialog.destroy, padx=20, pady=10).pack(side='left', padx=10)
    
    def generate_bill_pdf(self, bill_data):
        """Generate PDF bill with QR code"""
        # Get downloads folder path based on OS
        if os.name == 'nt':  # Windows
            downloads_path = os.path.expanduser('~\\Downloads')
        else:  # Unix/Linux/Mac
            downloads_path = os.path.expanduser('~/Downloads')
            
        filename = os.path.join(downloads_path, f"bill_{bill_data['bill_no']}.pdf")
        
        # Use SimpleDocTemplate for better formatting
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Prepare story elements
        story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
        
        # Create header
        header_text = "SMART HOSPITAL"
        story.append(Paragraph(header_text, styles['Center']))
        story.append(Spacer(1, 12))
        
        # Hospital address
        address = """123 Medical Center Drive<br/>
                    Healthcare City, State 12345<br/>
                    Phone: (555) 123-4567<br/>
                    Email: info@smarthospital.com"""
        story.append(Paragraph(address, styles['Center']))
        story.append(Spacer(1, 20))
        
        # Bill header
        story.append(Paragraph("BILL STATEMENT", styles['Center']))
        story.append(Spacer(1, 20))
        
        # Bill and patient information
        info_data = [
            ['Bill No:', bill_data['bill_no']],
            ['Date:', bill_data['date']],
            ['Patient ID:', bill_data['patient_id']],
            ['Patient Name:', bill_data['patient_name']],
            ['Payment Method:', bill_data['payment_method']],
            ['Status:', bill_data['status']]
        ]
        
        info_table = Table(info_data, colWidths=[120, 380])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Services
        services = bill_data['services'].split(', ')
        service_data = [['Service', 'Amount']] + [[s, ''] for s in services]
        for service in services:
            service_data.append([service, ''])

        t = Table(service_data, colWidths=[300, 200])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # Payment details
        payment_info = [
            ['Payment Information'],
            ['Method:', bill_data['payment_method']],
        ]
        
        # Add payment-specific details
        if bill_data['payment_method'] == 'Credit Card' or bill_data['payment_method'] == 'Debit Card':
            if 'card_details' in bill_data:
                payment_info.extend([
                    ['Card Number:', f"XXXX-XXXX-XXXX-{bill_data['card_details']['number'][-4:]}"],
                    ['Card Holder:', bill_data['card_details']['holder']],
                ])
        elif bill_data['payment_method'] == 'Insurance':
            if 'insurance_details' in bill_data:
                payment_info.extend([
                    ['Provider:', bill_data['insurance_details']['provider']],
                    ['Policy Number:', bill_data['insurance_details']['policy']],
                    ['Claim Status:', bill_data['insurance_details']['status']],
                ])
        elif bill_data['payment_method'] == 'Online Payment':
            payment_info.extend([
                ['Transaction ID:', bill_data.get('transaction_id', 'Pending')],
                ['Payment Status:', bill_data.get('payment_status', 'Pending')],
            ])
        
        t = Table(payment_info, colWidths=[100, 300])
        t.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # Amounts
        amounts_data = [
            ['', 'Amount'],
            ['Subtotal:', f"₹{bill_data['subtotal']:.2f}"],
            ['Tax (10%):', f"₹{bill_data['tax']:.2f}"],
            ['Total:', f"₹{bill_data['total']:.2f}"],
        ]
        t = Table(amounts_data, colWidths=[200, 100])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, -2), (1, -2), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 30))
        
        # Prefer using a user-provided QR image (data/user_qr.png). If not present,
        # fall back to generating a verification QR code dynamically.
        base_dir = os.path.dirname(__file__)
        possible_qr = [
            os.path.join(base_dir, 'data', 'user_qr.png'),
            os.path.join(base_dir, 'data', 'user_qr.jpg'),
            os.path.join(base_dir, 'data', 'user_qr.jpeg')
        ]

        qr_path = None
        for p in possible_qr:
            if os.path.exists(p):
                qr_path = p
                break

        if not qr_path:
            # Generate QR code for verification
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"BILL:{bill_data['bill_no']}|AMOUNT:{bill_data['total']}|DATE:{bill_data['date']}|STATUS:{bill_data['status']}")
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")
            # Get system temp directory for QR code
            qr_path = os.path.join(os.path.expanduser('~'), '.cache', 'hospital_qr_temp.png')
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            qr_image.save(qr_path)
        
        # Add QR code with caption
        img = Image(qr_path)
        img.drawHeight = 1.2*inch
        img.drawWidth = 1.2*inch
        
        qr_table = Table([[img], ['Scan for verification']], colWidths=[1.5*inch])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (0, 1), 8),
        ]))
        story.append(qr_table)
        
        # Build PDF
        doc.build(story)
        
        # Clean up QR temp file
        if os.path.exists(qr_path):
            os.remove(qr_path)
    
    def view_bill(self, event):
        """View bill details"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        bill_no = item['values'][0]
        
        bills = self.data_manager.get_bills()
        bill = next((b for b in bills if b['bill_no'] == bill_no), None)
        
        if not bill:
            return
        
        messagebox.showinfo("Bill Details", 
                           f"Bill No: {bill['bill_no']}\n"
                           f"Patient: {bill['patient_name']}\n"
                           f"Services: {bill['services']}\n"
                           f"Subtotal: ₹{bill['subtotal']:.2f}\n"
                           f"Tax: ₹{bill['tax']:.2f}\n"
                           f"Total: ₹{bill['total']:.2f}\n"
                           f"Payment: {bill['payment_method']}\n"
                           f"Date: {bill['date']}\n"
                           f"Status: {bill['status']}")
    
    def undo_last(self):
        """Undo last billing operation using Stack"""
        if self.data_manager.undo_last_bill():
            messagebox.showinfo("Success", "Last bill deleted successfully!")
            self.load_bills()
        else:
            messagebox.showwarning("Warning", "No operation to undo")

class AnalyticsModule:
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        self.create_widgets()
    
    def create_widgets(self):
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="📈 Analytics & Reports", font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        # Charts container
        charts_container = tk.Frame(self.parent, bg='white')
        charts_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Revenue chart
        revenue_frame = tk.Frame(charts_container, bg='white', relief='raised', bd=1)
        revenue_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(revenue_frame, text="💰 Revenue by Payment Method", 
                font=('Arial', 12, 'bold'), bg='white').pack(pady=10)
        
        self.create_revenue_chart(revenue_frame)
        
        # Appointment status chart
        status_frame = tk.Frame(charts_container, bg='white', relief='raised', bd=1)
        status_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        tk.Label(status_frame, text="📊 Appointment Status", 
                font=('Arial', 12, 'bold'), bg='white').pack(pady=10)
        
        self.create_status_chart(status_frame)
    
    def create_revenue_chart(self, parent):
        """Bar chart for revenue by payment method"""
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        bills = self.data_manager.get_bills()
        revenue_by_method = {}
        
        for bill in bills:
            method = bill.get('payment_method', 'Unknown')
            revenue_by_method[method] = revenue_by_method.get(method, 0) + bill.get('total', 0)
        
        if revenue_by_method:
            methods = list(revenue_by_method.keys())
            amounts = list(revenue_by_method.values())
            
            ax.bar(methods, amounts, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'])
            ax.set_ylabel('Revenue (₹)')
            ax.set_title('Revenue Distribution')
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_status_chart(self, parent):
        """Pie chart for appointment status"""
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        appointments = self.data_manager.get_appointments()
        status_count = {}
        
        for appt in appointments:
            status = appt.get('status', 'Unknown')
            status_count[status] = status_count.get(status, 0) + 1
        
        if status_count:
            labels = list(status_count.keys())
            sizes = list(status_count.values())
            colors = ['#2ecc71', '#f39c12', '#e74c3c']
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

class EmergencyModule:
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        self.create_widgets()
    
    def create_widgets(self):
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="🚑 Emergency Patient Registration", font=('Arial', 20, 'bold'),
                bg='white', fg='#e74c3c').pack()
        
        # Quick form
        form_frame = tk.Frame(self.parent, bg='white', relief='raised', bd=2)
        form_frame.pack(fill='both', expand=True, padx=50, pady=30)
        
        inner_frame = tk.Frame(form_frame, bg='white', padx=40, pady=30)
        inner_frame.pack()
        
        tk.Label(inner_frame, text="⚡ QUICK REGISTRATION", font=('Arial', 16, 'bold'),
                bg='white', fg='#e74c3c').grid(row=0, column=0, columnspan=2, pady=20)
        
        fields = {}
        field_list = [
            ('Patient Name', 'name'),
            ('Age', 'age'),
            ('Gender', 'gender'),
            ('Emergency Type', 'disease'),
            ('Contact', 'contact')
        ]
        
        for i, (label, key) in enumerate(field_list, start=1):
            tk.Label(inner_frame, text=f"{label}:", font=('Arial', 12, 'bold'),
                    bg='white').grid(row=i, column=0, sticky='w', pady=10, padx=(0, 20))
            
            if key == 'gender':
                fields[key] = ttk.Combobox(inner_frame, values=['Male', 'Female', 'Other'],
                                          state='readonly', font=('Arial', 11), width=30)
            else:
                fields[key] = tk.Entry(inner_frame, font=('Arial', 11), width=32)
            
            fields[key].grid(row=i, column=1, pady=10)
        
        # Doctor assignment
        tk.Label(inner_frame, text="Assign Doctor:", font=('Arial', 12, 'bold'),
                bg='white').grid(row=len(field_list)+1, column=0, sticky='w', pady=10, padx=(0, 20))
        
        doctors = self.data_manager.get_doctors()
        doctor_names = [d['name'] for d in doctors]
        fields['doctor'] = ttk.Combobox(inner_frame, values=doctor_names,
                                       state='readonly', font=('Arial', 11), width=30)
        fields['doctor'].grid(row=len(field_list)+1, column=1, pady=10)
        
        def register_emergency():
            patient_data = {}
            for key, widget in fields.items():
                value = widget.get().strip()
                if not value:
                    messagebox.showerror("Error", f"{key.title()} is required!")
                    return
                patient_data[key] = value
            
            patients = self.data_manager.get_patients()
            patient_data['id'] = self.data_manager.generate_id('P', patients)
            patient_data['admit_date'] = datetime.now().strftime("%Y-%m-%d")
            patient_data['address'] = 'Emergency'
            patient_data['blood_group'] = 'Unknown'
            
            self.data_manager.add_patient(patient_data)
            
            messagebox.showinfo("Success", 
                              f"Emergency patient registered!\n"
                              f"Patient ID: {patient_data['id']}\n"
                              f"Assigned to: {patient_data['doctor']}")
            
            # Clear fields
            for widget in fields.values():
                if isinstance(widget, tk.Entry):
                    widget.delete(0, 'end')
                else:
                    widget.set('')
        
        tk.Button(inner_frame, text="🚑 REGISTER EMERGENCY PATIENT", 
                 font=('Arial', 13, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                 command=register_emergency, padx=30, pady=15).grid(
                     row=len(field_list)+2, column=0, columnspan=2, pady=30)

# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    # Initialize data manager
    data_manager = DataManager()
    
    # Create login window
    root = tk.Tk()
    LoginWindow(root, data_manager)
    root.mainloop()

if __name__ == "__main__":
    main()