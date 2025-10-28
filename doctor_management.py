import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
from tkcalendar import Calendar
import json
import os

class DoctorModule:
    def __init__(self, parent, data_manager, user):
        self.parent = parent
        self.data_manager = data_manager
        self.user = user
        self.create_widgets()
        self.load_schedules()
    
    def create_widgets(self):
        # Title Frame
        title_frame = tk.Frame(self.parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="👨‍⚕️ Doctor Management", 
                font=('Arial', 20, 'bold'),
                bg='white', fg='#2c3e50').pack(side='left')
        
        # Action Buttons
        btn_frame = tk.Frame(title_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="➕ Set Schedule", 
                 font=('Arial', 10, 'bold'),
                 bg='#2ecc71', fg='white', relief='flat', 
                 command=self.set_schedule,
                 padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="📊 View Analytics", 
                 font=('Arial', 10, 'bold'),
                 bg='#3498db', fg='white', relief='flat',
                 command=self.view_analytics,
                 padx=15, pady=8).pack(side='left', padx=5)
        
        # Calendar & Schedule View
        content_frame = tk.Frame(self.parent, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Calendar
        calendar_frame = tk.Frame(content_frame, bg='white')
        calendar_frame.pack(side='left', fill='y', padx=(0, 20))
        
        self.calendar = Calendar(calendar_frame, selectmode='day',
                               date_pattern='yyyy-mm-dd')
        self.calendar.pack(pady=(0, 20))
        
        self.calendar.bind('<<CalendarSelected>>', self.load_day_schedule)
        
        # Doctor selection if admin
        if self.user['role'] == 'admin':
            doctors = [u for u in self.data_manager.get_users() 
                      if u['role'] == 'doctor']
            doctor_list = [f"{d['id']} - {d['name']}" for d in doctors]
            
            tk.Label(calendar_frame, text="Select Doctor:",
                    font=('Arial', 11, 'bold'),
                    bg='white').pack()
            
            self.doctor_var = tk.StringVar()
            doctor_combo = ttk.Combobox(calendar_frame, 
                                      textvariable=self.doctor_var,
                                      values=doctor_list, width=30)
            doctor_combo.pack(pady=10)
            doctor_combo.bind('<<ComboboxSelected>>', self.load_day_schedule)
        else:
            self.doctor_var = tk.StringVar(value=f"{self.user['id']} - {self.user['name']}")
        
        # Right panel - Schedule
        schedule_frame = tk.Frame(content_frame, bg='white')
        schedule_frame.pack(side='left', fill='both', expand=True)
        
        # Schedule table
        columns = ('Time', 'Status', 'Patient', 'Type')
        self.tree = ttk.Treeview(schedule_frame, columns=columns,
                                show='headings', height=20)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(schedule_frame, orient='vertical',
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Configure columns
        widths = [100, 100, 200, 150]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        # Configure tags for status colors
        self.tree.tag_configure('available', background='#e8f5e9')
        self.tree.tag_configure('booked', background='#fff3e0')
        self.tree.tag_configure('unavailable', background='#ffebee')
    
    def set_schedule(self):
        if not self.doctor_var.get():
            messagebox.showerror("Error", "Please select a doctor first!")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Set Schedule")
        dialog.geometry("500x700")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        tk.Label(main_frame, text="Set Doctor Schedule",
                font=('Arial', 16, 'bold')).pack(pady=(0,20))
        
        # Date Range
        date_frame = tk.Frame(main_frame)
        date_frame.pack(fill='x', pady=10)
        
        tk.Label(date_frame, text="Date Range:",
                font=('Arial', 11, 'bold')).pack(side='left')
        
        start_cal = Calendar(date_frame, selectmode='day',
                           date_pattern='yyyy-mm-dd',
                           mindate=datetime.now())
        start_cal.pack(side='left', padx=5)
        
        end_cal = Calendar(date_frame, selectmode='day',
                          date_pattern='yyyy-mm-dd',
                          mindate=datetime.now())
        end_cal.pack(side='left', padx=5)
        
        # Time Range
        time_frame = tk.Frame(main_frame)
        time_frame.pack(fill='x', pady=20)
        
        tk.Label(time_frame, text="Working Hours:",
                font=('Arial', 11, 'bold')).pack()
        
        hours_frame = tk.Frame(time_frame)
        hours_frame.pack(pady=10)
        
        # Start time
        start_time_frame = tk.Frame(hours_frame)
        start_time_frame.pack(side='left', padx=10)
        
        tk.Label(start_time_frame, text="Start Time").pack()
        
        start_hour = tk.StringVar(value="09")
        start_minute = tk.StringVar(value="00")
        
        ttk.Combobox(start_time_frame, textvariable=start_hour,
                    values=[f"{i:02d}" for i in range(24)],
                    width=5).pack(side='left', padx=2)
        tk.Label(start_time_frame, text=":").pack(side='left')
        ttk.Combobox(start_time_frame, textvariable=start_minute,
                    values=['00', '15', '30', '45'],
                    width=5).pack(side='left', padx=2)
        
        # End time
        end_time_frame = tk.Frame(hours_frame)
        end_time_frame.pack(side='left', padx=10)
        
        tk.Label(end_time_frame, text="End Time").pack()
        
        end_hour = tk.StringVar(value="17")
        end_minute = tk.StringVar(value="00")
        
        ttk.Combobox(end_time_frame, textvariable=end_hour,
                    values=[f"{i:02d}" for i in range(24)],
                    width=5).pack(side='left', padx=2)
        tk.Label(end_time_frame, text=":").pack(side='left')
        ttk.Combobox(end_time_frame, textvariable=end_minute,
                    values=['00', '15', '30', '45'],
                    width=5).pack(side='left', padx=2)
        
        # Slot Duration
        duration_frame = tk.Frame(main_frame)
        duration_frame.pack(fill='x', pady=10)
        
        tk.Label(duration_frame, text="Appointment Duration:",
                font=('Arial', 11, 'bold')).pack(side='left')
        
        duration_var = tk.StringVar(value="30")
        ttk.Combobox(duration_frame, textvariable=duration_var,
                    values=['15', '30', '45', '60'],
                    width=10).pack(side='left', padx=10)
        
        tk.Label(duration_frame, text="minutes").pack(side='left')
        
        # Break Time
        break_frame = tk.Frame(main_frame)
        break_frame.pack(fill='x', pady=10)
        
        tk.Label(break_frame, text="Break Time:",
                font=('Arial', 11, 'bold')).pack()
        
        breaks_frame = tk.Frame(break_frame)
        breaks_frame.pack(pady=10)
        
        self.break_vars = []
        
        def add_break():
            break_row = tk.Frame(breaks_frame)
            break_row.pack(fill='x', pady=2)
            
            start_hour = tk.StringVar(value="12")
            start_minute = tk.StringVar(value="00")
            end_hour = tk.StringVar(value="13")
            end_minute = tk.StringVar(value="00")
            
            ttk.Combobox(break_row, textvariable=start_hour,
                        values=[f"{i:02d}" for i in range(24)],
                        width=5).pack(side='left', padx=2)
            tk.Label(break_row, text=":").pack(side='left')
            ttk.Combobox(break_row, textvariable=start_minute,
                        values=['00', '15', '30', '45'],
                        width=5).pack(side='left', padx=2)
            
            tk.Label(break_row, text="to").pack(side='left', padx=5)
            
            ttk.Combobox(break_row, textvariable=end_hour,
                        values=[f"{i:02d}" for i in range(24)],
                        width=5).pack(side='left', padx=2)
            tk.Label(break_row, text=":").pack(side='left')
            ttk.Combobox(break_row, textvariable=end_minute,
                        values=['00', '15', '30', '45'],
                        width=5).pack(side='left', padx=2)
            
            tk.Button(break_row, text="❌",
                     command=lambda: [break_row.destroy(),
                                    self.break_vars.remove(break_vars)],
                     relief='flat').pack(side='left', padx=5)
            
            break_vars = (start_hour, start_minute, end_hour, end_minute)
            self.break_vars.append(break_vars)
        
        tk.Button(break_frame, text="➕ Add Break",
                 command=add_break).pack()
        
        # Add default lunch break
        add_break()
        
        def save_schedule():
            try:
                doctor_id = self.doctor_var.get().split(' - ')[0]
                start_date = datetime.strptime(start_cal.get_date(), "%Y-%m-%d")
                end_date = datetime.strptime(end_cal.get_date(), "%Y-%m-%d")
                
                if end_date < start_date:
                    raise ValueError("End date must be after start date")
                
                # Get breaks
                breaks = []
                for break_var in self.break_vars:
                    break_start = f"{break_var[0].get()}:{break_var[1].get()}"
                    break_end = f"{break_var[2].get()}:{break_var[3].get()}"
                    breaks.append([break_start, break_end])
                
                # Create schedule for each day
                current_date = start_date
                while current_date <= end_date:
                    # Skip weekends
                    if current_date.weekday() < 5:  # Monday to Friday
                        schedule_data = {
                            'doctor_id': doctor_id,
                            'date': current_date.strftime("%Y-%m-%d"),
                            'start_time': f"{start_hour.get()}:{start_minute.get()}",
                            'end_time': f"{end_hour.get()}:{end_minute.get()}",
                            'slot_duration': int(duration_var.get()),
                            'breaks': breaks,
                            'available': True
                        }
                        
                        self.data_manager.update_doctor_schedule(schedule_data)
                    
                    current_date += timedelta(days=1)
                
                messagebox.showinfo("Success", "Schedule updated successfully!")
                dialog.destroy()
                self.load_day_schedule(None)
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Save button
        tk.Button(main_frame, text="💾 Save Schedule",
                 font=('Arial', 11, 'bold'),
                 bg='#2ecc71', fg='white',
                 command=save_schedule,
                 relief='flat', padx=20, pady=10).pack(pady=20)
    
    def view_analytics(self):
        if not self.doctor_var.get():
            messagebox.showerror("Error", "Please select a doctor first!")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Doctor Analytics")
        dialog.geometry("800x600")
        dialog.transient(self.parent)
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        doctor_id = self.doctor_var.get().split(' - ')[0]
        doctor_name = self.doctor_var.get().split(' - ')[1]
        
        tk.Label(main_frame, text=f"Analytics for Dr. {doctor_name}",
                font=('Arial', 16, 'bold')).pack(pady=(0,20))
        
        # Get statistics
        appointments = [a for a in self.data_manager.get_appointments()
                       if a['doctor_id'] == doctor_id]
        
        total_appointments = len(appointments)
        completed = len([a for a in appointments if a['status'] == 'completed'])
        cancelled = len([a for a in appointments if a['status'] == 'cancelled'])
        scheduled = len([a for a in appointments if a['status'] == 'scheduled'])
        
        # Create statistics frames
        stats_frame = tk.Frame(main_frame)
        stats_frame.pack(fill='x', pady=20)
        
        stats = [
            ("Total Appointments", total_appointments, '#3498db'),
            ("Completed", completed, '#2ecc71'),
            ("Scheduled", scheduled, '#f1c40f'),
            ("Cancelled", cancelled, '#e74c3c')
        ]
        
        for title, value, color in stats:
            stat_box = tk.Frame(stats_frame, relief='solid', bd=1)
            stat_box.pack(side='left', expand=True, padx=10)
            
            tk.Label(stat_box, text=title,
                    font=('Arial', 12)).pack(pady=5)
            tk.Label(stat_box, text=str(value),
                    font=('Arial', 20, 'bold'),
                    fg=color).pack(pady=5)
        
        # Most common appointment types
        types_frame = tk.Frame(main_frame)
        types_frame.pack(fill='x', pady=20)
        
        tk.Label(types_frame, text="Most Common Appointment Types",
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        type_counts = {}
        for appointment in appointments:
            type_counts[appointment['type']] = type_counts.get(appointment['type'], 0) + 1
        
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        for appt_type, count in sorted_types[:5]:
            row = tk.Frame(types_frame)
            row.pack(fill='x', pady=2)
            
            tk.Label(row, text=appt_type,
                    font=('Arial', 11),
                    width=20, anchor='w').pack(side='left')
            
            # Progress bar background
            bar_bg = tk.Frame(row, bg='#eee', width=300, height=20)
            bar_bg.pack(side='left', padx=10)
            bar_bg.pack_propagate(False)
            
            # Progress bar
            bar_width = int((count / total_appointments) * 300)
            bar = tk.Frame(bar_bg, bg='#3498db', width=bar_width, height=20)
            bar.pack(side='left', anchor='w')
            
            tk.Label(row, text=f"{count} ({count/total_appointments*100:.1f}%)",
                    font=('Arial', 11)).pack(side='left')
        
        # Monthly statistics
        monthly_frame = tk.Frame(main_frame)
        monthly_frame.pack(fill='x', pady=20)
        
        tk.Label(monthly_frame, text="Monthly Statistics",
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Group appointments by month
        monthly_stats = {}
        for appointment in appointments:
            date = datetime.strptime(appointment['date'], "%Y-%m-%d")
            month_key = date.strftime("%Y-%m")
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'total': 0, 'completed': 0}
            
            monthly_stats[month_key]['total'] += 1
            if appointment['status'] == 'completed':
                monthly_stats[month_key]['completed'] += 1
        
        # Show last 6 months
        months = sorted(monthly_stats.keys())[-6:]
        for month in months:
            stats = monthly_stats[month]
            
            row = tk.Frame(monthly_frame)
            row.pack(fill='x', pady=2)
            
            month_label = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
            tk.Label(row, text=month_label,
                    font=('Arial', 11),
                    width=20, anchor='w').pack(side='left')
            
            # Progress bar for completion rate
            completion_rate = (stats['completed'] / stats['total']) * 100
            
            bar_bg = tk.Frame(row, bg='#eee', width=300, height=20)
            bar_bg.pack(side='left', padx=10)
            bar_bg.pack_propagate(False)
            
            bar = tk.Frame(bar_bg, bg='#2ecc71', 
                         width=int(completion_rate * 3), height=20)
            bar.pack(side='left', anchor='w')
            
            tk.Label(row, 
                    text=f"{stats['completed']}/{stats['total']} ({completion_rate:.1f}%)",
                    font=('Arial', 11)).pack(side='left')
    
    def load_day_schedule(self, event):
        """Load schedule for selected date"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.doctor_var.get():
            return
        
        doctor_id = self.doctor_var.get().split(' - ')[0]
        selected_date = self.calendar.get_date()
        
        # Get doctor's schedule
        schedule = self.data_manager.get_doctor_schedule(doctor_id, selected_date)
        if not schedule:
            return
        
        schedule = schedule[0]
        if not schedule['available']:
            return
        
        # Get appointments for this day
        appointments = [a for a in self.data_manager.get_appointments()
                      if a['doctor_id'] == doctor_id and 
                      a['date'] == selected_date]
        
        # Generate time slots
        start_time = datetime.strptime(schedule['start_time'], "%H:%M")
        end_time = datetime.strptime(schedule['end_time'], "%H:%M")
        slot_duration = timedelta(minutes=schedule['slot_duration'])
        
        current_slot = start_time
        while current_slot < end_time:
            slot_time = current_slot.strftime("%H:%M")
            
            # Check if slot is during break
            is_break = False
            for break_time in schedule['breaks']:
                break_start = datetime.strptime(break_time[0], "%H:%M")
                break_end = datetime.strptime(break_time[1], "%H:%M")
                if break_start <= current_slot < break_end:
                    is_break = True
                    break
            
            if is_break:
                self.tree.insert('', 'end',
                    values=(slot_time, "Break", "-", "-"),
                    tags=('unavailable',))
            else:
                # Check if slot is booked
                appointment = next((a for a in appointments 
                                 if a['time'] == slot_time), None)
                
                if appointment:
                    self.tree.insert('', 'end',
                        values=(slot_time,
                               "Booked",
                               appointment['patient_name'],
                               appointment['type']),
                        tags=('booked',))
                else:
                    self.tree.insert('', 'end',
                        values=(slot_time, "Available", "-", "-"),
                        tags=('available',))
            
            current_slot += slot_duration
    
    def load_schedules(self):
        """Initial load of schedule data"""
        if self.doctor_var.get():
            self.load_day_schedule(None)