import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime, timedelta

class DatePicker:
    def __init__(self, parent, date_var):
        self.parent = parent
        self.date_var = date_var
        self.top = None
        
    def show_calendar(self):
        self.top = tk.Toplevel(self.parent)
        self.top.title("Select Date")
        self.top.geometry("300x300")
        self.top.transient(self.parent)
        self.top.grab_set()
        
        # Center the dialog
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.top.winfo_screenheight() // 2) - (300 // 2)
        self.top.geometry(f'300x300+{x}+{y}')
        
        # Create calendar
        cal = Calendar(self.top, selectmode='day',
                      date_pattern='yyyy-mm-dd',
                      mindate=datetime.now())
        cal.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Add OK button
        tk.Button(self.top, text="OK", command=lambda: self.on_date_select(cal.get_date())).pack(pady=10)
        
    def on_date_select(self, date):
        self.date_var.set(date)
        self.top.destroy()