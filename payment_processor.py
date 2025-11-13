import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from PIL import Image, ImageTk
import json
import os
from datetime import datetime
import random

class PaymentProcessor:
    def __init__(self, parent, bill_data, callback):
        self.parent = parent
        self.bill_data = bill_data
        self.callback = callback
        # Load configuration (UPI id etc.) if available
        self.base_dir = os.path.dirname(__file__)
        self.config_path = os.path.join(self.base_dir, 'data', 'config.json')
        self.upi_id = None
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    self.upi_id = cfg.get('upi_id')
        except Exception:
            self.upi_id = None
        self.create_payment_window()
    
    def create_payment_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Payment Processing")
        self.window.geometry("600x700")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f'600x700+{x}+{y}')
        
        # Payment Method Selection
        tk.Label(self.window, text="Select Payment Method", 
                font=('Arial', 16, 'bold')).pack(pady=20)
        
        methods_frame = tk.Frame(self.window)
        methods_frame.pack(fill='x', padx=20)
        
        # Payment Methods
        self.payment_var = tk.StringVar(value="qr")
        
        methods = [
            ("QR Code Payment", "qr"),
            ("Credit Card", "credit"),
            ("Debit Card", "debit")
        ]
        
        for text, value in methods:
            rb = tk.Radiobutton(methods_frame, text=text, 
                              variable=self.payment_var, value=value,
                              command=self.show_payment_method,
                              font=('Arial', 12))
            rb.pack(anchor='w', pady=5)
        
        # Container for payment method specific widgets
        self.payment_container = tk.Frame(self.window)
        self.payment_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Show initial payment method (QR)
        self.show_payment_method()
    
    def show_payment_method(self):
        # Clear container
        for widget in self.payment_container.winfo_children():
            widget.destroy()
        
        method = self.payment_var.get()
        
        if method == "qr":
            self.show_qr_payment()
        elif method in ["credit", "debit"]:
            self.show_card_payment()
    
    def show_qr_payment(self):
    # Prefer loading a user-provided QR image (e.g. data/user_qr.png).
        # If not present, fall back to generating a UPI QR using qrcode.
        amount = self.bill_data['total']
        merchant = "Hospital Management System"
        reference = self.bill_data['bill_no']

        # Look for an external QR image in the repository data folder
        base_dir = os.path.dirname(__file__)
        possible_paths = [
            os.path.join(base_dir, 'data', 'user_qr.png'),
            os.path.join(base_dir, 'data', 'user_qr.jpg'),
            os.path.join(base_dir, 'data', 'user_qr.jpeg'),
            os.path.join(base_dir, 'data', 'user_qr.bmp'),
            os.path.join(base_dir, 'data', 'user_qr.gif')
        ]

        user_qr_path = None
        for p in possible_paths:
            if os.path.exists(p):
                user_qr_path = p
                break

        if user_qr_path:
            try:
                qr_image = Image.open(user_qr_path).convert('RGBA')
                qr_image = qr_image.resize((300, 300))
            except Exception as e:
                # If loading fails, fall back to generated QR
                print(f"Failed to load user QR image {user_qr_path}: {e}")
                user_qr_path = None

        if not user_qr_path:
            # Determine UPI id: prefer configured upi_id, otherwise default
            upi_pa = self.upi_id if self.upi_id else 'hospital@upi'
            # Create UPI payment string
            upi_string = f"upi://pay?pa={upi_pa}&pn={merchant}&am={amount}&tr={reference}&cu=INR"

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(upi_string)
            qr.make(fit=True)

            qr_image = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
            qr_image = qr_image.resize((300, 300))

        # Convert to PhotoImage
        qr_photo = ImageTk.PhotoImage(qr_image)

        # Display QR
        tk.Label(self.payment_container, text="Scan QR Code to Pay",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 6))

        # If a configured UPI id exists, show it as a caption so users know the receiver
        if self.upi_id:
            tk.Label(self.payment_container, text=f"UPI: {self.upi_id}",
                     font=('Arial', 11)).pack(pady=(0, 10))
        else:
            tk.Label(self.payment_container, text="",
                     font=('Arial', 11)).pack(pady=(0, 10))

        qr_label = tk.Label(self.payment_container, image=qr_photo)
        qr_label.image = qr_photo
        qr_label.pack()

        # Payment Details
        details_frame = tk.Frame(self.payment_container)
        details_frame.pack(fill='x', pady=20)

        tk.Label(details_frame, text=f"Amount: ${self.bill_data['total']:.2f}",
                 font=('Arial', 12)).pack()
        tk.Label(details_frame, text=f"Reference: {self.bill_data['bill_no']}",
                 font=('Arial', 12)).pack()

        # Verify Payment Button
        tk.Button(self.payment_container, text="Verify Payment",
                  command=self.verify_qr_payment,
                  font=('Arial', 12)).pack(pady=20)
    
    def show_card_payment(self):
        # Card Type
        card_type = self.payment_var.get().title()
        
        tk.Label(self.payment_container, text=f"{card_type} Card Payment",
                font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Card Details Form
        form_frame = tk.Frame(self.payment_container)
        form_frame.pack(fill='x', padx=20)
        
        # Card Number
        tk.Label(form_frame, text="Card Number:",
                font=('Arial', 11)).pack(anchor='w')
        self.card_number = ttk.Entry(form_frame, font=('Arial', 11))
        self.card_number.pack(fill='x', pady=(0, 10))
        
        # Card Holder
        tk.Label(form_frame, text="Card Holder Name:",
                font=('Arial', 11)).pack(anchor='w')
        self.card_holder = ttk.Entry(form_frame, font=('Arial', 11))
        self.card_holder.pack(fill='x', pady=(0, 10))
        
        # Expiry Date
        expiry_frame = tk.Frame(form_frame)
        expiry_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(expiry_frame, text="Expiry Date:",
                font=('Arial', 11)).pack(side='left')
        
        self.exp_month = ttk.Combobox(expiry_frame, width=3,
                                     values=[str(i).zfill(2) for i in range(1, 13)])
        self.exp_month.pack(side='left', padx=5)
        
        self.exp_year = ttk.Combobox(expiry_frame, width=5,
                                    values=[str(i) for i in range(2025, 2036)])
        self.exp_year.pack(side='left')
        
        # CVV
        tk.Label(form_frame, text="CVV:",
                font=('Arial', 11)).pack(anchor='w')
        self.cvv = ttk.Entry(form_frame, font=('Arial', 11), show='*', width=5)
        self.cvv.pack(anchor='w')
        
        # Amount
        amount_frame = tk.Frame(self.payment_container)
        amount_frame.pack(fill='x', pady=20)
        
        tk.Label(amount_frame, text="Amount to Pay:",
                font=('Arial', 12, 'bold')).pack(side='left')
        tk.Label(amount_frame, text=f"${self.bill_data['total']:.2f}",
                font=('Arial', 12)).pack(side='left', padx=10)
        
        # Process Payment Button
        tk.Button(self.payment_container, text="Process Payment",
                 command=self.process_card_payment,
                 font=('Arial', 12)).pack(pady=20)
    
    def verify_qr_payment(self):
        # Simulate payment verification
        # In real implementation, this would verify with payment gateway
        if messagebox.askyesno("Verify Payment", 
                             "Has the payment been completed successfully?"):
            self.complete_payment("QR Code")
        else:
            messagebox.showwarning("Payment Incomplete", 
                                 "Please complete the payment process")
    
    def process_card_payment(self):
        # Validate card details
        if not self.validate_card_details():
            return
        
        # Simulate card processing
        # In real implementation, this would connect to payment gateway
        messagebox.showinfo("Processing", 
                          "Processing payment... Please wait...")
        
        # Simulate successful payment
        self.complete_payment(f"{self.payment_var.get().title()} Card")
    
    def validate_card_details(self):
        card_number = self.card_number.get().strip()
        card_holder = self.card_holder.get().strip()
        exp_month = self.exp_month.get()
        exp_year = self.exp_year.get()
        cvv = self.cvv.get().strip()
        
        if not card_number or len(card_number) != 16 or not card_number.isdigit():
            messagebox.showerror("Error", "Please enter a valid 16-digit card number")
            return False
        
        if not card_holder:
            messagebox.showerror("Error", "Please enter card holder name")
            return False
        
        if not exp_month or not exp_year:
            messagebox.showerror("Error", "Please select expiry date")
            return False
        
        if not cvv or len(cvv) != 3 or not cvv.isdigit():
            messagebox.showerror("Error", "Please enter a valid 3-digit CVV")
            return False
        
        return True
    
    def complete_payment(self, payment_method):
        # Update bill data with payment details
        self.bill_data.update({
            'payment_method': payment_method,
            'payment_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'transaction_id': f"TXN{random.randint(100000, 999999)}",
            'status': 'Paid'
        })
        
        # Call callback function with updated bill data
        self.callback(self.bill_data)
        
        messagebox.showinfo("Success", "Payment processed successfully!")
        # Close the payment window after showing confirmation
        try:
            self.window.destroy()
        except Exception:
            pass