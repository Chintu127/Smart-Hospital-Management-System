import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json
import os

class DashboardBase:
    def __init__(self, root, user, data_manager):
        self.root = root
        self.user = user
        self.data_manager = data_manager
        self.create_base_dashboard()
    
    def create_base_dashboard(self):
        self.root.title(f"Hospital Management System - {self.user['role'].title()} Dashboard")
        
        # Create main container
        self.main_container = tk.Frame(self.root, bg='#f5f6fa')
        self.main_container.pack(fill='both', expand=True)
        
        # Create sidebar
        self.sidebar = tk.Frame(self.main_container, bg='#2c3e50', width=200)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        
        # User info in sidebar
        user_frame = tk.Frame(self.sidebar, bg='#2c3e50', pady=20)
        user_frame.pack(fill='x')
        
        tk.Label(user_frame, text="👤", font=('Arial', 20),
                bg='#2c3e50', fg='white').pack()
        
        tk.Label(user_frame, text=self.user['name'],
                font=('Arial', 12, 'bold'),
                bg='#2c3e50', fg='white').pack()
        
        tk.Label(user_frame, text=f"ID: {self.user['id']}",
                font=('Arial', 10),
                bg='#2c3e50', fg='#bdc3c7').pack()
        
        tk.Frame(self.sidebar, height=2, bg='#34495e').pack(fill='x', padx=20)
        
        # Create content area
        self.content = tk.Frame(self.main_container, bg='#f5f6fa')
        self.content.pack(side='left', fill='both', expand=True)
        
        # Create top bar
        top_bar = tk.Frame(self.content, bg='white', height=60)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)
        
        # Current date time
        def update_datetime():
            datetime_label.config(
                text=datetime.now().strftime("%B %d, %Y %H:%M:%S"))
            self.root.after(1000, update_datetime)
        
        datetime_label = tk.Label(top_bar, font=('Arial', 12),
                                bg='white', fg='#2c3e50')
        datetime_label.pack(side='left', padx=20)
        update_datetime()
        
        # Notifications button
        self.notification_count = tk.StringVar(value="0")
        
        notification_btn = tk.Button(top_bar, text="🔔",
                                   font=('Arial', 14),
                                   bg='white', bd=0,
                                   command=self.show_notifications)
        notification_btn.pack(side='right', padx=20)
        
        tk.Label(top_bar, textvariable=self.notification_count,
                font=('Arial', 8), bg='red', fg='white',
                width=2).place(relx=1, x=-25, y=10)
        
        # Logout button
        tk.Button(top_bar, text="Logout",
                 font=('Arial', 10),
                 bg='#e74c3c', fg='white',
                 command=self.logout).pack(side='right', padx=5)
        
        # Create workspace
        self.workspace = tk.Frame(self.content, bg='#f5f6fa')
        self.workspace.pack(fill='both', expand=True, padx=20, pady=20)
    
    def add_sidebar_button(self, text, command):
        btn = tk.Button(self.sidebar, text=text,
                       font=('Arial', 11),
                       bg='#2c3e50', fg='white',
                       bd=0, relief='flat',
                       activebackground='#34495e',
                       activeforeground='white',
                       cursor='hand2',
                       anchor='w', padx=20,
                       command=command)
        btn.pack(fill='x', pady=1)
        return btn
    
    def clear_workspace(self):
        """Clear all widgets in workspace"""
        for widget in self.workspace.winfo_children():
            widget.destroy()
    
    def show_notifications(self):
        """Show notifications popup"""
        notifications = self.data_manager.get_notifications(
            user_id=self.user['id'],
            status='unread'
        )
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Notifications")
        dialog.geometry("400x600")
        dialog.transient(self.root)
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        tk.Label(main_frame, text="📬 Notifications",
                font=('Arial', 16, 'bold')).pack(pady=(0,20))
        
        if not notifications:
            tk.Label(main_frame, text="No new notifications",
                    font=('Arial', 12)).pack()
            return
        
        # Create scrollable frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical",
                                command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add notifications
        for notification in notifications:
            note_frame = tk.Frame(scrollable_frame, relief='solid',
                                bd=1, padx=10, pady=10)
            note_frame.pack(fill='x', pady=5)
            
            tk.Label(note_frame, text=notification['title'],
                    font=('Arial', 11, 'bold'),
                    wraplength=300).pack(anchor='w')
            
            tk.Label(note_frame, text=notification['message'],
                    font=('Arial', 10),
                    wraplength=300).pack(anchor='w')
            
            tk.Label(note_frame, text=notification['date'],
                    font=('Arial', 8),
                    fg='gray').pack(anchor='w')
            
            def mark_read(note_id=notification.get('id')):
                self.data_manager.update_notification_status(
                    note_id, 'read')
                dialog.destroy()
                self.update_notification_count()
            
            tk.Button(note_frame, text="Mark as Read",
                     command=mark_read,
                     relief='flat', cursor='hand2').pack(anchor='e')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_notification_count(self):
        """Update notification count in top bar"""
        count = len(self.data_manager.get_notifications(
            user_id=self.user['id'],
            status='unread'
        ))
        self.notification_count.set(str(count))
    
    def logout(self):
        """Logout user and return to login screen"""
        if tk.messagebox.askyesno("Logout",
            "Are you sure you want to logout?"):
            self.root.destroy()
            root = tk.Tk()
            from login_system import LoginSystem
            LoginSystem(root, self.data_manager)
            root.mainloop()

class AdminDashboard(DashboardBase):
    def __init__(self, root, user, data_manager):
        super().__init__(root, user, data_manager)
        self.setup_admin_dashboard()
    
    def setup_admin_dashboard(self):
        # Add sidebar buttons
        self.add_sidebar_button("📊 Dashboard Overview", self.show_overview)
        self.add_sidebar_button("👥 User Management", self.show_user_management)
        self.add_sidebar_button("🏥 Department Management", self.show_department_management)
        self.add_sidebar_button("📈 Analytics", self.show_analytics)
        self.add_sidebar_button("⚙️ System Settings", self.show_settings)
        
        # Show overview by default
        self.show_overview()
    
    def show_overview(self):
        self.clear_workspace()
        
        # Add overview widgets here
        tk.Label(self.workspace, text="System Overview",
                font=('Arial', 20, 'bold')).pack()
        
        # Statistics cards
        stats_frame = tk.Frame(self.workspace, bg='#f5f6fa')
        stats_frame.pack(fill='x', pady=20)
        
        # Get statistics
        users = self.data_manager.get_users()
        doctors = len([u for u in users if u['role'] == 'doctor'])
        patients = len(self.data_manager.get_patients())
        appointments = len(self.data_manager.get_appointments())
        
        stats = [
            ("👨‍⚕️ Doctors", doctors, "#3498db"),
            ("👥 Patients", patients, "#2ecc71"),
            ("📅 Appointments", appointments, "#e67e22"),
            ("💊 Medicines", len(self.data_manager.get_medicines()), "#9b59b6")
        ]
        
        for title, value, color in stats:
            card = tk.Frame(stats_frame, bg='white',
                          relief='solid', bd=1)
            card.pack(side='left', expand=True,
                     fill='both', padx=10)
            
            tk.Label(card, text=title,
                    font=('Arial', 12),
                    bg='white').pack(pady=5)
            
            tk.Label(card, text=str(value),
                    font=('Arial', 24, 'bold'),
                    fg=color, bg='white').pack(pady=5)
    
    def show_user_management(self):
        self.clear_workspace()
        
        # Title
        title_frame = tk.Frame(self.workspace, bg='#f5f6fa')
        title_frame.pack(fill='x', pady=(0,20))
        
        tk.Label(title_frame, text="User Management",
                font=('Arial', 20, 'bold'),
                bg='#f5f6fa').pack(side='left')
        
        tk.Button(title_frame, text="➕ Add User",
                 command=self.add_user,
                 bg='#2ecc71', fg='white',
                 font=('Arial', 10, 'bold'),
                 relief='flat').pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(self.workspace, bg='#f5f6fa')
        filter_frame.pack(fill='x', pady=(0,20))
        
        tk.Label(filter_frame, text="Role:",
                bg='#f5f6fa').pack(side='left')
        
        role_var = tk.StringVar(value="All")
        ttk.Combobox(filter_frame,
                    textvariable=role_var,
                    values=["All", "Admin", "Doctor",
                           "Pharmacist", "Lab Technician",
                           "Receptionist"],
                    state='readonly').pack(side='left', padx=5)
        
        tk.Label(filter_frame, text="Status:",
                bg='#f5f6fa').pack(side='left', padx=(20,0))
        
        status_var = tk.StringVar(value="All")
        ttk.Combobox(filter_frame,
                    textvariable=status_var,
                    values=["All", "Active", "Inactive"],
                    state='readonly').pack(side='left', padx=5)
        
        # Search
        search_var = tk.StringVar()
        tk.Entry(filter_frame,
                textvariable=search_var,
                width=30).pack(side='right')
        
        tk.Label(filter_frame, text="🔍",
                bg='#f5f6fa').pack(side='right', padx=5)
        
        # Users table
        table_frame = tk.Frame(self.workspace)
        table_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Name', 'Role', 'Email', 'Phone', 'Status')
        tree = ttk.Treeview(table_frame, columns=columns,
                           show='headings')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical',
                                command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(fill='both', expand=True)
        
        def load_users():
            for item in tree.get_children():
                tree.delete(item)
            
            users = self.data_manager.get_users()
            role_filter = role_var.get()
            status_filter = status_var.get()
            search = search_var.get().lower()
            
            for user in users:
                if role_filter != "All" and \
                   user['role'].title() != role_filter:
                    continue
                
                if status_filter != "All" and \
                   user['status'].title() != status_filter:
                    continue
                
                if search and search not in \
                   f"{user['name']} {user['email']} {user['id']}".lower():
                    continue
                
                tree.insert('', 'end', values=(
                    user['id'],
                    user['name'],
                    user['role'].title(),
                    user['email'],
                    user['phone'],
                    user['status'].title()
                ))
        
        # Bind events
        role_var.trace('w', lambda *args: load_users())
        status_var.trace('w', lambda *args: load_users())
        search_var.trace('w', lambda *args: load_users())
        
        # Load initial data
        load_users()
        
        def show_user_details(event):
            item = tree.selection()[0]
            user_id = tree.item(item)['values'][0]
            self.show_user_details(user_id)
        
        tree.bind('<Double-1>', show_user_details)
    
    def show_user_details(self, user_id):
        users = self.data_manager.get_users()
        user = next((u for u in users if u['id'] == user_id), None)
        
        if not user:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"User Details - {user_id}")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # User details
        tk.Label(main_frame, text="User Details",
                font=('Arial', 16, 'bold')).pack(pady=(0,20))
        
        details_frame = tk.Frame(main_frame)
        details_frame.pack(fill='x')
        
        fields = [
            ("ID", user['id']),
            ("Name", user['name']),
            ("Role", user['role'].title()),
            ("Email", user['email']),
            ("Phone", user['phone']),
            ("Status", user['status'].title()),
            ("Registered", user.get('registered_date', 'N/A')),
            ("Last Login", user.get('last_login', 'Never'))
        ]
        
        if user['role'] == 'doctor':
            fields.append(("Department", user.get('department', 'N/A')))
        
        for label, value in fields:
            row = tk.Frame(details_frame)
            row.pack(fill='x', pady=5)
            
            tk.Label(row, text=f"{label}:",
                    font=('Arial', 11, 'bold'),
                    width=15, anchor='e').pack(side='left')
            
            tk.Label(row, text=str(value),
                    font=('Arial', 11)).pack(side='left', padx=10)
        
        # Action buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        def toggle_status():
            new_status = 'inactive' if user['status'] == 'active' else 'active'
            user['status'] = new_status
            self.data_manager.update_user(user['id'], user)
            dialog.destroy()
            self.show_user_management()
        
        tk.Button(btn_frame,
                 text="Deactivate" if user['status'] == 'active' else "Activate",
                 command=toggle_status,
                 bg='#e74c3c' if user['status'] == 'active' else '#2ecc71',
                 fg='white',
                 font=('Arial', 11)).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Reset Password",
                 command=lambda: self.reset_password(user),
                 font=('Arial', 11)).pack(side='left', padx=5)
    
    def reset_password(self, user):
        # Simple password reset dialog for admins
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Reset Password - {user['name']}")
        dialog.geometry("400x200")
        dialog.transient(self.root)

        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="New Password:", font=('Arial', 11)).pack(anchor='w')
        pwd_entry = tk.Entry(frame, show='•', width=30)
        pwd_entry.pack(pady=(0,10))

        tk.Label(frame, text="Confirm Password:", font=('Arial', 11)).pack(anchor='w')
        pwd_confirm = tk.Entry(frame, show='•', width=30)
        pwd_confirm.pack(pady=(0,10))

        def do_reset():
            p1 = pwd_entry.get().strip()
            p2 = pwd_confirm.get().strip()
            if not p1 or not p2:
                tk.messagebox.showerror("Error", "Please enter the new password twice.")
                return
            if p1 != p2:
                tk.messagebox.showerror("Error", "Passwords do not match.")
                return
            if len(p1) < 8:
                tk.messagebox.showerror("Error", "Password must be at least 8 characters.")
                return

            try:
                # update_user will hash password internally if provided
                self.data_manager.update_user(user['id'], {'password': p1})
                tk.messagebox.showinfo("Success", "Password has been reset.")
                dialog.destroy()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Unable to reset password: {str(e)}")

        tk.Button(frame, text="Reset Password", bg='#e67e22', fg='white', command=do_reset).pack(pady=10)
    
    def add_user(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New User")
        dialog.geometry("500x420")
        dialog.transient(self.root)

        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill='both', expand=True)

        # Fields
        tk.Label(frame, text="Full Name:", font=('Arial', 11)).pack(anchor='w')
        name_entry = tk.Entry(frame, width=40)
        name_entry.pack(pady=(0,8))

        tk.Label(frame, text="Username:", font=('Arial', 11)).pack(anchor='w')
        username_entry = tk.Entry(frame, width=40)
        username_entry.pack(pady=(0,8))

        tk.Label(frame, text="Password:", font=('Arial', 11)).pack(anchor='w')
        pwd_entry = tk.Entry(frame, show='•', width=40)
        pwd_entry.pack(pady=(0,8))

        tk.Label(frame, text="Confirm Password:", font=('Arial', 11)).pack(anchor='w')
        pwd_confirm = tk.Entry(frame, show='•', width=40)
        pwd_confirm.pack(pady=(0,8))

        tk.Label(frame, text="Email:", font=('Arial', 11)).pack(anchor='w')
        email_entry = tk.Entry(frame, width=40)
        email_entry.pack(pady=(0,8))

        tk.Label(frame, text="Phone:", font=('Arial', 11)).pack(anchor='w')
        phone_entry = tk.Entry(frame, width=40)
        phone_entry.pack(pady=(0,8))

        tk.Label(frame, text="Role:", font=('Arial', 11)).pack(anchor='w')
        role_var = tk.StringVar()
        roles = ["admin", "doctor", "pharmacist", "lab_technician", "receptionist"]
        role_combo = ttk.Combobox(frame, textvariable=role_var, values=roles, state='readonly', width=37)
        role_combo.pack(pady=(0,8))
        role_combo.set(roles[0])

        dept_frame = tk.Frame(frame)
        tk.Label(dept_frame, text="Department:", font=('Arial', 11)).pack(side='left')
        dept_var = tk.StringVar()
        dept_combo = ttk.Combobox(dept_frame, textvariable=dept_var, values=[
            "General Medicine","Pediatrics","Cardiology","Orthopedics","Neurology",
            "Gynecology","Dermatology","ENT","Ophthalmology","Psychiatry"
        ], state='readonly', width=28)
        dept_combo.pack(side='left', padx=8)

        def on_role_change(*args):
            if role_var.get() == 'doctor':
                dept_frame.pack(fill='x', pady=(0,8))
            else:
                dept_frame.pack_forget()

        role_var.trace('w', on_role_change)

        def do_add():
            name = name_entry.get().strip()
            username = username_entry.get().strip()
            pwd = pwd_entry.get().strip()
            pwd2 = pwd_confirm.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            role = role_var.get()

            if not all([name, username, pwd, pwd2, email, phone, role]):
                tk.messagebox.showerror("Error", "All fields are required.")
                return
            if pwd != pwd2:
                tk.messagebox.showerror("Error", "Passwords do not match.")
                return
            if len(pwd) < 8:
                tk.messagebox.showerror("Error", "Password must be at least 8 characters.")
                return

            kwargs = {
                'name': name,
                'email': email,
                'phone': phone,
                'status': 'active'
            }
            if role == 'doctor':
                kwargs['department'] = dept_var.get()

            try:
                created = self.data_manager.create_user(username=username, password=pwd, role=role, **kwargs)
                tk.messagebox.showinfo("Success", f"User created: {created['id']}")
                dialog.destroy()
                self.show_user_management()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Unable to create user: {str(e)}")

        tk.Button(frame, text="Create User", bg='#2ecc71', fg='white', command=do_add).pack(pady=10)
    
    def show_department_management(self):
        # Implementation for department management
        pass
    
    def show_analytics(self):
        # Implementation for analytics
        pass
    
    def show_settings(self):
        # Implementation for settings
        pass

class DoctorDashboard(DashboardBase):
    def __init__(self, root, user, data_manager):
        super().__init__(root, user, data_manager)
        self.setup_doctor_dashboard()
    
    def setup_doctor_dashboard(self):
        # Add sidebar buttons
        self.add_sidebar_button("📊 Dashboard", self.show_overview)
        self.add_sidebar_button("👥 My Patients", self.show_patients)
        self.add_sidebar_button("📅 Appointments", self.show_appointments)
        self.add_sidebar_button("📝 Prescriptions", self.show_prescriptions)
        self.add_sidebar_button("📋 Medical Records", self.show_medical_records)
        self.add_sidebar_button("📊 My Analytics", self.show_analytics)
        
        # Show overview by default
        self.show_overview()
    
    def show_overview(self):
        # Implementation for doctor's overview
        pass
    
    def show_patients(self):
        # Implementation for patient management
        pass
    
    def show_appointments(self):
        # Implementation for appointment management
        pass
    
    def show_prescriptions(self):
        # Implementation for prescription management
        pass
    
    def show_medical_records(self):
        # Implementation for medical records
        pass
    
    def show_analytics(self):
        # Implementation for doctor's analytics
        pass

class PharmacistDashboard(DashboardBase):
    def __init__(self, root, user, data_manager):
        super().__init__(root, user, data_manager)
        self.setup_pharmacist_dashboard()
    
    def setup_pharmacist_dashboard(self):
        # Add sidebar buttons
        self.add_sidebar_button("📊 Dashboard", self.show_overview)
        self.add_sidebar_button("💊 Inventory", self.show_inventory)
        self.add_sidebar_button("📝 Prescriptions", self.show_prescriptions)
        self.add_sidebar_button("🛒 Sales", self.show_sales)
        self.add_sidebar_button("📦 Purchase Orders", self.show_purchase_orders)
        self.add_sidebar_button("📈 Analytics", self.show_analytics)
        
        # Show overview by default
        self.show_overview()
    
    def show_overview(self):
        # Implementation for pharmacist's overview
        pass
    
    def show_inventory(self):
        # Implementation for inventory management
        pass
    
    def show_prescriptions(self):
        # Implementation for prescription handling
        pass
    
    def show_sales(self):
        # Implementation for sales management
        pass
    
    def show_purchase_orders(self):
        # Implementation for purchase order management
        pass
    
    def show_analytics(self):
        # Implementation for pharmacy analytics
        pass

class LabTechnicianDashboard(DashboardBase):
    def __init__(self, root, user, data_manager):
        super().__init__(root, user, data_manager)
        self.setup_lab_dashboard()
    
    def setup_lab_dashboard(self):
        # Add sidebar buttons
        self.add_sidebar_button("📊 Dashboard", self.show_overview)
        self.add_sidebar_button("🔬 Lab Tests", self.show_lab_tests)
        self.add_sidebar_button("📋 Test Results", self.show_test_results)
        self.add_sidebar_button("📦 Lab Inventory", self.show_inventory)
        self.add_sidebar_button("📈 Analytics", self.show_analytics)
        
        # Show overview by default
        self.show_overview()
    
    def show_overview(self):
        # Implementation for lab overview
        pass
    
    def show_lab_tests(self):
        # Implementation for lab test management
        pass
    
    def show_test_results(self):
        # Implementation for test results
        pass
    
    def show_inventory(self):
        # Implementation for lab inventory
        pass
    
    def show_analytics(self):
        # Implementation for lab analytics
        pass

class ReceptionistDashboard(DashboardBase):
    def __init__(self, root, user, data_manager):
        super().__init__(root, user, data_manager)
        self.setup_receptionist_dashboard()
    
    def setup_receptionist_dashboard(self):
        # Add sidebar buttons
        self.add_sidebar_button("📊 Dashboard", self.show_overview)
        self.add_sidebar_button("👥 Patients", self.show_patients)
        self.add_sidebar_button("📅 Appointments", self.show_appointments)
        self.add_sidebar_button("💰 Billing", self.show_billing)
        self.add_sidebar_button("🏥 Room Management", self.show_room_management)
        self.add_sidebar_button("📈 Reports", self.show_reports)
        
        # Show overview by default
        self.show_overview()
    
    def show_overview(self):
        # Implementation for receptionist's overview
        pass
    
    def show_patients(self):
        # Implementation for patient registration/management
        pass
    
    def show_appointments(self):
        # Implementation for appointment scheduling
        pass
    
    def show_billing(self):
        # Implementation for billing management
        pass
    
    def show_room_management(self):
        # Implementation for room management
        pass
    
    def show_reports(self):
        # Implementation for reports generation
        pass