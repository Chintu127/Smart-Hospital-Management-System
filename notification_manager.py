import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
import os

class NotificationManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.config_path = os.path.join(os.path.dirname(__file__), 'data', 'config.json')
        self.load_config()
        
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    'email': {
                        'smtp_server': 'smtp.gmail.com',
                        'smtp_port': 587,
                        'username': '',
                        'password': '',
                        'from_email': ''
                    }
                }
                self.save_config()
        except Exception as e:
            print(f"Error loading notification config: {e}")
            self.config = {}
    
    def save_config(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def send_email_notification(self, to_email, subject, message):
        if not self.config.get('email', {}).get('username'):
            print("Email configuration not set up")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], 
                                self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'],
                        self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            return True
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            return False
    
    def notify_appointment_scheduled(self, appointment_data):
        """Send notifications when a new appointment is scheduled"""
        try:
            # Get patient and doctor details
            patient = next((p for p in self.data_manager.get_patients() 
                          if p['id'] == appointment_data['patient_id']), None)
            doctor = next((d for d in self.data_manager.get_users() 
                         if d['id'] == appointment_data['doctor_id']), None)
            
            if patient and 'email' in patient:
                # Patient notification
                subject = "Appointment Scheduled"
                message = f"""
                Dear {patient['name']},
                
                Your appointment has been scheduled:
                Date: {appointment_data['date']}
                Time: {appointment_data['time']}
                Doctor: Dr. {doctor['name'] if doctor else 'Unknown'}
                
                Please arrive 15 minutes before your appointment time.
                
                Best regards,
                Hospital Management System
                """
                self.send_email_notification(patient['email'], subject, message)
            
            if doctor and 'email' in doctor:
                # Doctor notification
                subject = "New Appointment Scheduled"
                message = f"""
                Dear Dr. {doctor['name']},
                
                A new appointment has been scheduled:
                Date: {appointment_data['date']}
                Time: {appointment_data['time']}
                Patient: {patient['name'] if patient else 'Unknown'}
                Purpose: {appointment_data.get('purpose', 'Not specified')}
                
                Best regards,
                Hospital Management System
                """
                self.send_email_notification(doctor['email'], subject, message)
                
        except Exception as e:
            print(f"Failed to send appointment notifications: {e}")
    
    def notify_appointment_reminder(self):
        """Send reminders for upcoming appointments"""
        try:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            appointments = self.data_manager.get_appointments()
            
            for appt in appointments:
                if appt['date'] == tomorrow:
                    patient = next((p for p in self.data_manager.get_patients() 
                                  if p['id'] == appt['patient_id']), None)
                    doctor = next((d for d in self.data_manager.get_users() 
                                 if d['id'] == appt['doctor_id']), None)
                    
                    if patient and 'email' in patient:
                        subject = "Appointment Reminder"
                        message = f"""
                        Dear {patient['name']},
                        
                        This is a reminder for your appointment tomorrow:
                        Date: {appt['date']}
                        Time: {appt['time']}
                        Doctor: Dr. {doctor['name'] if doctor else 'Unknown'}
                        
                        Please arrive 15 minutes before your appointment time.
                        
                        Best regards,
                        Hospital Management System
                        """
                        self.send_email_notification(patient['email'], subject, message)
                        
        except Exception as e:
            print(f"Failed to send appointment reminders: {e}")