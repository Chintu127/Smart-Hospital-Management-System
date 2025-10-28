import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
import re
from datetime import datetime

class LoginSystem:
    def __init__(self, root, data_manager):
        self.root = root
        self.data_manager = data_manager
        self.create_login_window()
        
    def create_login_window(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title("Hospital Management System - Login")
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        # Login frame
        login_frame = tk.Frame(main_frame, bg='white', padx=40, pady=40)
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Hospital Logo/Name
        tk.Label(login_frame, text="🏥", font=('Arial', 40),
                bg='white').pack(pady=(0,10))
        
        tk.Label(login_frame, text="Hospital Management System",
                font=('Arial', 20, 'bold'), bg='white',
                fg='#2c3e50').pack(pady=(0,30))
        
        # Username
        tk.Label(login_frame, text="Username:", font=('Arial', 12),
                bg='white').pack(anchor='w')
        
        username_entry = tk.Entry(login_frame, font=('Arial', 12),
                                width=30)
        username_entry.pack(pady=(0,15), ipady=5)
        
        # Password
        tk.Label(login_frame, text="Password:", font=('Arial', 12),
                bg='white').pack(anchor='w')
        
        password_entry = tk.Entry(login_frame, font=('Arial', 12),
                                width=30, show='•')
        password_entry.pack(pady=(0,20), ipady=5)
        
        # Show/Hide password
        def toggle_password():
            if password_entry['show'] == '•':
                password_entry['show'] = ''
                show_pass_btn.configure(text='Hide Password')
            else:
                password_entry['show'] = '•'
                show_pass_btn.configure(text='Show Password')
        
        show_pass_btn = tk.Button(login_frame, text="Show Password",
                                command=toggle_password,
                                relief='flat', cursor='hand2',
                                bg='white', bd=0, fg='#3498db')
        show_pass_btn.pack(pady=(0,15))
        
        # Login button
        tk.Button(login_frame, text="Login", font=('Arial', 12, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat',
                 cursor='hand2', command=lambda: self.login(
                     username_entry.get(), password_entry.get()),
                 width=25, pady=8).pack(pady=(0,15))
        
        # Register link
        register_frame = tk.Frame(login_frame, bg='white')
        register_frame.pack()
        
        tk.Label(register_frame, text="Don't have an account?",
                font=('Arial', 10), bg='white').pack(side='left')
        
        register_btn = tk.Button(register_frame, text="Register",
                               font=('Arial', 10), fg='#3498db',
                               relief='flat', cursor='hand2',
                               bg='white', bd=0,
                               command=self.show_registration)
        register_btn.pack(side='left', padx=5)
        
        # Admin registration link (temporary)
        tk.Button(login_frame, text="Register as Admin",
                 font=('Arial', 8), fg='gray',
                 relief='flat', cursor='hand2',
                 bg='white', bd=0,
                 command=lambda: self.show_registration(is_admin=True)).pack(pady=20)
    
    def show_registration(self, is_admin=False):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.title("Hospital Management System - Registration")
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        # Registration frame
        reg_frame = tk.Frame(main_frame, bg='white', padx=40, pady=20)
        reg_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        tk.Label(reg_frame, text="🏥", font=('Arial', 40),
                bg='white').pack(pady=(0,10))
        
        tk.Label(reg_frame, text="New User Registration",
                font=('Arial', 20, 'bold'), bg='white',
                fg='#2c3e50').pack(pady=(0,30))
        
        # Form fields
        fields = [
            ("Full Name:", "name"),
            ("Username:", "username"),
            ("Password:", "password"),
            ("Confirm Password:", "confirm_password"),
            ("Email:", "email"),
            ("Phone:", "phone")
        ]
        
        entries = {}
        for label, key in fields:
            field_frame = tk.Frame(reg_frame, bg='white')
            field_frame.pack(fill='x', pady=5)
            
            tk.Label(field_frame, text=label, font=('Arial', 11),
                    bg='white', width=15, anchor='w').pack(side='left')
            
            if key in ['password', 'confirm_password']:
                entry = tk.Entry(field_frame, font=('Arial', 11),
                               width=25, show='•')
            else:
                entry = tk.Entry(field_frame, font=('Arial', 11), width=25)
            entry.pack(side='left', padx=5)
            entries[key] = entry
        
        # Role selection
        role_frame = tk.Frame(reg_frame, bg='white')
        role_frame.pack(fill='x', pady=5)
        
        tk.Label(role_frame, text="Role:", font=('Arial', 11),
                bg='white', width=15, anchor='w').pack(side='left')
        
        roles = ["doctor", "pharmacist", "lab_technician", "receptionist"]
        if is_admin:
            roles.insert(0, "admin")
        
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(role_frame, textvariable=role_var,
                                values=roles, state='readonly', width=22)
        role_combo.pack(side='left', padx=5)
        if roles:
            role_combo.set(roles[0])
        
        # Department (for doctors)
        dept_frame = tk.Frame(reg_frame, bg='white')
        dept_var = tk.StringVar()
        
        def toggle_department(*args):
            if role_var.get() == "doctor":
                dept_frame.pack(fill='x', pady=5)
            else:
                dept_frame.pack_forget()
        
        role_var.trace('w', toggle_department)
        
        tk.Label(dept_frame, text="Department:", font=('Arial', 11),
                bg='white', width=15, anchor='w').pack(side='left')
        
        departments = [
            "General Medicine",
            "Pediatrics",
            "Cardiology",
            "Orthopedics",
            "Neurology",
            "Gynecology",
            "Dermatology",
            "ENT",
            "Ophthalmology",
            "Psychiatry"
        ]
        
        dept_combo = ttk.Combobox(dept_frame, textvariable=dept_var,
                                values=departments, state='readonly', width=22)
        dept_combo.pack(side='left', padx=5)
        if departments:
            dept_combo.set(departments[0])
        
        def validate_and_register():
            # Get values
            data = {key: entries[key].get().strip() 
                   for key in entries.keys()}
            data['role'] = role_var.get()
            if data['role'] == "doctor":
                data['department'] = dept_var.get()
            
            # Validation
            if any(not v for v in data.values()):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            if data['password'] != data['confirm_password']:
                messagebox.showerror("Error", "Passwords do not match!")
                return
            
            if len(data['password']) < 8:
                messagebox.showerror("Error", 
                    "Password must be at least 8 characters long!")
                return
            
            # Validate email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                messagebox.showerror("Error", "Invalid email address!")
                return
            
            # Validate phone
            phone_pattern = r'^\+?1?\d{9,15}$'
            if not re.match(phone_pattern, data['phone']):
                messagebox.showerror("Error", 
                    "Invalid phone number! Use format: +1234567890")
                return
            
            # Prepare kwargs for DataManager.create_user
            kwargs = {
                'name': data.get('name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'registered_date': datetime.now().strftime("%Y-%m-%d"),
                'status': 'active'
            }
            if data['role'] == 'doctor':
                kwargs['department'] = data.get('department')

            try:
                created = self.data_manager.create_user(
                    username=data['username'],
                    password=data['password'],
                    role=data['role'],
                    **kwargs
                )

                messagebox.showinfo("Success",
                    f"Registration successful!\nYour ID: {created['id']}")
                self.create_login_window()
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {str(e)}")
        
        # Register button
        tk.Button(reg_frame, text="Register", font=('Arial', 12, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat',
                 cursor='hand2', command=validate_and_register,
                 width=25, pady=8).pack(pady=20)
        
        # Back to login button
        tk.Button(reg_frame, text="← Back to Login",
                 font=('Arial', 10), fg='#3498db',
                 relief='flat', cursor='hand2',
                 bg='white', bd=0,
                 command=self.create_login_window).pack()
    
    def login(self, username, password):
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Use DataManager authenticate_user which handles hashing
        user = self.data_manager.authenticate_user(username, password)

        if not user:
            messagebox.showerror("Error", "Invalid username or password!")
            return

        if user.get('status') not in (None, 'active', True):
            messagebox.showerror("Error", "Your account is not active!")
            return

        # Update last login
        try:
            self.data_manager.update_user(user['id'], {'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        except Exception:
            # Non-fatal if update fails
            pass

        messagebox.showinfo("Success", f"Welcome, {user.get('name', user.get('username'))}!")

        # Launch appropriate dashboard based on role
        self.launch_dashboard(user)