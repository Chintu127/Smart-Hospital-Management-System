import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
import seaborn as sns

class AnalyticsManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        # Set style for all plots
        plt.style.use('seaborn')
        sns.set_palette("husl")
    
    def create_chart_frame(self, parent, figsize=(6, 4)):
        """Create a frame with matplotlib figure"""
        fig = plt.Figure(figsize=figsize, dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        widget = canvas.get_tk_widget()
        return fig, widget
    
    def get_appointment_stats(self, doctor_id=None, days=30):
        """Get appointment statistics"""
        appointments = self.data_manager.get_appointments()
        if doctor_id:
            appointments = [a for a in appointments if a['doctor_id'] == doctor_id]
        
        # Filter for last n days
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        recent_appointments = [a for a in appointments 
                             if a['date'] >= cutoff_date]
        
        # Group by date and status
        daily_stats = {}
        for appointment in recent_appointments:
            date = appointment['date']
            status = appointment['status']
            if date not in daily_stats:
                daily_stats[date] = {'scheduled': 0, 'completed': 0, 'cancelled': 0}
            daily_stats[date][status] += 1
        
        return daily_stats
    
    def plot_appointment_trends(self, frame, doctor_id=None):
        """Plot appointment trends over time"""
        stats = self.get_appointment_stats(doctor_id)
        dates = sorted(stats.keys())
        
        scheduled = [stats[d]['scheduled'] for d in dates]
        completed = [stats[d]['completed'] for d in dates]
        cancelled = [stats[d]['cancelled'] for d in dates]
        
        fig, widget = self.create_chart_frame(frame)
        ax = fig.add_subplot(111)
        
        ax.plot(dates, scheduled, label='Scheduled', marker='o')
        ax.plot(dates, completed, label='Completed', marker='s')
        ax.plot(dates, cancelled, label='Cancelled', marker='^')
        
        ax.set_title('Appointment Trends')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Appointments')
        ax.tick_params(axis='x', rotation=45)
        ax.legend()
        
        fig.tight_layout()
        return widget
    
    def plot_department_workload(self, frame):
        """Plot workload distribution across departments"""
        users = self.data_manager.get_users()
        doctors = [u for u in users if u['role'] == 'doctor']
        
        dept_appointments = {}
        for doctor in doctors:
            dept = doctor.get('department', 'Other')
            appointments = [a for a in self.data_manager.get_appointments()
                          if a['doctor_id'] == doctor['id']]
            dept_appointments[dept] = dept_appointments.get(dept, 0) + len(appointments)
        
        fig, widget = self.create_chart_frame(frame)
        ax = fig.add_subplot(111)
        
        departments = list(dept_appointments.keys())
        counts = list(dept_appointments.values())
        
        bars = ax.bar(departments, counts)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom')
        
        ax.set_title('Department Workload')
        ax.set_xlabel('Department')
        ax.set_ylabel('Number of Appointments')
        ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        return widget
    
    def plot_medicine_stock(self, frame):
        """Plot current medicine stock levels"""
        medicines = self.data_manager.get_medicines()
        
        # Sort by quantity
        medicines = sorted(medicines, key=lambda x: x['quantity'])[:10]
        
        fig, widget = self.create_chart_frame(frame)
        ax = fig.add_subplot(111)
        
        names = [m['name'] for m in medicines]
        quantities = [m['quantity'] for m in medicines]
        reorder_levels = [m.get('reorder_level', 10) for m in medicines]
        
        # Create horizontal bar chart
        bars = ax.barh(names, quantities)
        
        # Add reorder level lines
        for i, level in enumerate(reorder_levels):
            ax.axvline(x=level, ymin=i/len(names), 
                      ymax=(i+1)/len(names), 
                      color='red', linestyle='--', alpha=0.5)
        
        ax.set_title('Medicine Stock Levels')
        ax.set_xlabel('Quantity')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)}',
                   ha='left', va='center')
        
        fig.tight_layout()
        return widget
    
    def plot_lab_test_distribution(self, frame):
        """Plot distribution of lab tests"""
        reports = self.data_manager.get_lab_reports()
        
        test_counts = {}
        for report in reports:
            test_type = report['test']
            test_counts[test_type] = test_counts.get(test_type, 0) + 1
        
        # Sort by count
        test_counts = dict(sorted(test_counts.items(), 
                                key=lambda x: x[1], 
                                reverse=True)[:8])
        
        fig, widget = self.create_chart_frame(frame)
        ax = fig.add_subplot(111)
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(test_counts.values(),
                                         labels=test_counts.keys(),
                                         autopct='%1.1f%%',
                                         textprops={'fontsize': 8})
        
        ax.set_title('Lab Test Distribution')
        
        fig.tight_layout()
        return widget
    
    def plot_revenue_trends(self, frame):
        """Plot revenue trends"""
        bills = self.data_manager.get_bills()
        
        # Group by date
        daily_revenue = {}
        for bill in bills:
            date = bill.get('date', bill.get('created_at', '').split()[0])
            if date:
                amount = float(bill.get('amount', 0))
                daily_revenue[date] = daily_revenue.get(date, 0) + amount
        
        dates = sorted(daily_revenue.keys())
        revenue = [daily_revenue[d] for d in dates]
        
        fig, widget = self.create_chart_frame(frame)
        ax = fig.add_subplot(111)
        
        # Create line plot with area
        ax.fill_between(dates, revenue, alpha=0.3)
        ax.plot(dates, revenue, marker='o')
        
        ax.set_title('Revenue Trends')
        ax.set_xlabel('Date')
        ax.set_ylabel('Revenue')
        ax.tick_params(axis='x', rotation=45)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f'${x:,.2f}'))
        
        fig.tight_layout()
        return widget
    
    def plot_patient_demographics(self, frame):
        """Plot patient age and gender distribution"""
        patients = self.data_manager.get_patients()
        
        # Calculate age from DOB
        ages = []
        genders = []
        for patient in patients:
            try:
                dob = datetime.strptime(patient['dob'], "%Y-%m-%d")
                age = (datetime.now() - dob).days // 365
                ages.append(age)
                genders.append(patient.get('gender', 'Other'))
            except:
                continue
        
        fig, widget = self.create_chart_frame(frame)
        
        # Create two subplots
        ax1 = fig.add_subplot(121)  # Age distribution
        ax2 = fig.add_subplot(122)  # Gender distribution
        
        # Age distribution
        ax1.hist(ages, bins=20, edgecolor='black')
        ax1.set_title('Age Distribution')
        ax1.set_xlabel('Age')
        ax1.set_ylabel('Number of Patients')
        
        # Gender distribution
        gender_counts = {}
        for gender in genders:
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        ax2.pie(gender_counts.values(),
                labels=gender_counts.keys(),
                autopct='%1.1f%%')
        ax2.set_title('Gender Distribution')
        
        fig.tight_layout()
        return widget
    
    def plot_prescription_analysis(self, frame):
        """Plot prescription patterns"""
        prescriptions = self.data_manager.get_prescriptions()
        
        # Analyze medicine frequency
        medicine_freq = {}
        for prescription in prescriptions:
            for medicine in prescription.get('medicines', []):
                name = medicine.get('name', '')
                medicine_freq[name] = medicine_freq.get(name, 0) + 1
        
        # Sort and get top medicines
        top_medicines = dict(sorted(medicine_freq.items(),
                                  key=lambda x: x[1],
                                  reverse=True)[:10])
        
        fig, widget = self.create_chart_frame(frame)
        ax = fig.add_subplot(111)
        
        names = list(top_medicines.keys())
        frequencies = list(top_medicines.values())
        
        # Create horizontal bar chart
        bars = ax.barh(names, frequencies)
        
        ax.set_title('Most Prescribed Medicines')
        ax.set_xlabel('Number of Prescriptions')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)}',
                   ha='left', va='center')
        
        fig.tight_layout()
        return widget