import json
import os
from datetime import datetime
import hashlib
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path

class DataManager:
    def __init__(self, data_dir: str = "data"):
        """Initialize DataManager with data directory"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize data files
        self.files = {
            'users': self.data_dir / 'users.json',
            'patients': self.data_dir / 'patients.json',
            'appointments': self.data_dir / 'appointments.json',
            'prescriptions': self.data_dir / 'prescriptions.json',
            'medicines': self.data_dir / 'medicines.json',
            'lab_reports': self.data_dir / 'lab_reports.json',
            'bills': self.data_dir / 'bills.json',
            'audit_log': self.data_dir / 'audit_log.json'
        }
        
        # Create files if they don't exist
        for file_path in self.files.values():
            if not file_path.exists():
                self._save_data(file_path, [])
    
    def _load_data(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from JSON file with error handling"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, file_path: Path, data: List[Dict[str, Any]]) -> None:
        """Save data to JSON file with error handling"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self._log_error(f"Error saving to {file_path}: {str(e)}")
            raise
    
    def _log_action(self, action: str, details: str, user_id: Optional[str] = None) -> None:
        """Log actions for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'user_id': user_id,
            'ip_address': '127.0.0.1'  # In production, get actual IP
        }
        
        logs = self._load_data(self.files['audit_log'])
        logs.append(log_entry)
        self._save_data(self.files['audit_log'], logs)
    
    def _log_error(self, error_msg: str) -> None:
        """Log error messages"""
        self._log_action('ERROR', error_msg)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data if successful"""
        users = self._load_data(self.files['users'])
        hashed_password = self._hash_password(password)
        
        for user in users:
            if user['username'] == username and user['password'] == hashed_password:
                self._log_action('LOGIN', f'User {username} logged in', user['id'])
                return {k: v for k, v in user.items() if k != 'password'}
        return None
    
    # User Management
    def create_user(self, username: str, password: str, role: str, **kwargs) -> Dict[str, Any]:
        """Create new user with validation"""
        users = self._load_data(self.files['users'])
        
        # Validate username uniqueness
        if any(u['username'] == username for u in users):
            raise ValueError("Username already exists")
        
        user_id = str(uuid.uuid4())
        new_user = {
            'id': user_id,
            'username': username,
            'password': self._hash_password(password),
            'role': role,
            'created_at': datetime.now().isoformat(),
            'active': True,
            **kwargs
        }
        
        users.append(new_user)
        self._save_data(self.files['users'], users)
        self._log_action('CREATE_USER', f'Created user {username}', user_id)
        
        return {k: v for k, v in new_user.items() if k != 'password'}
    
    def update_user(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user data with validation"""
        users = self._load_data(self.files['users'])
        
        for i, user in enumerate(users):
            if user['id'] == user_id:
                if 'password' in data:
                    data['password'] = self._hash_password(data['password'])
                users[i].update(data)
                self._save_data(self.files['users'], users)
                self._log_action('UPDATE_USER', 
                               f'Updated user {user["username"]}', 
                               user_id)
                return {k: v for k, v in users[i].items() if k != 'password'}
        
        raise ValueError("User not found")
    
    # Patient Management
    def add_patient(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Add new patient record"""
        patients = self._load_data(self.files['patients'])
        
        patient_id = str(uuid.uuid4())
        new_patient = {
            'id': patient_id,
            'created_at': datetime.now().isoformat(),
            **data
        }
        
        patients.append(new_patient)
        self._save_data(self.files['patients'], patients)
        self._log_action('ADD_PATIENT', 
                        f'Added patient {data.get("name")}', 
                        user_id)
        
        return new_patient
    
    def update_patient(self, patient_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update patient record"""
        patients = self._load_data(self.files['patients'])
        
        for i, patient in enumerate(patients):
            if patient['id'] == patient_id:
                patients[i].update(data)
                self._save_data(self.files['patients'], patients)
                self._log_action('UPDATE_PATIENT', 
                               f'Updated patient {patient["name"]}', 
                               user_id)
                return patients[i]
        
        raise ValueError("Patient not found")
    
    # Appointment Management
    def create_appointment(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create new appointment"""
        appointments = self._load_data(self.files['appointments'])
        
        appointment_id = str(uuid.uuid4())
        new_appointment = {
            'id': appointment_id,
            'created_at': datetime.now().isoformat(),
            'status': 'scheduled',
            **data
        }
        
        appointments.append(new_appointment)
        self._save_data(self.files['appointments'], appointments)
        self._log_action('CREATE_APPOINTMENT', 
                        f'Created appointment for patient {data.get("patient_id")}',
                        user_id)
        
        return new_appointment
    
    # Medicine Management
    def add_medicine(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Add new medicine to inventory"""
        medicines = self._load_data(self.files['medicines'])
        
        medicine_id = str(uuid.uuid4())
        new_medicine = {
            'id': medicine_id,
            'created_at': datetime.now().isoformat(),
            **data
        }
        
        medicines.append(new_medicine)
        self._save_data(self.files['medicines'], medicines)
        self._log_action('ADD_MEDICINE', 
                        f'Added medicine {data.get("name")}',
                        user_id)
        
        return new_medicine
    
    def update_medicine_stock(self, medicine_id: str, quantity_change: int, user_id: str) -> Dict[str, Any]:
        """Update medicine stock levels"""
        medicines = self._load_data(self.files['medicines'])
        
        for i, medicine in enumerate(medicines):
            if medicine['id'] == medicine_id:
                new_quantity = medicine['quantity'] + quantity_change
                if new_quantity < 0:
                    raise ValueError("Insufficient stock")
                
                medicines[i]['quantity'] = new_quantity
                medicines[i]['last_updated'] = datetime.now().isoformat()
                
                self._save_data(self.files['medicines'], medicines)
                self._log_action('UPDATE_STOCK',
                               f'Updated {medicine["name"]} stock by {quantity_change}',
                               user_id)
                return medicines[i]
        
        raise ValueError("Medicine not found")
    
    # Lab Report Management
    def create_lab_report(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create new lab report"""
        reports = self._load_data(self.files['lab_reports'])
        
        report_id = str(uuid.uuid4())
        new_report = {
            'id': report_id,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            **data
        }
        
        reports.append(new_report)
        self._save_data(self.files['lab_reports'], reports)
        self._log_action('CREATE_LAB_REPORT',
                        f'Created lab report for patient {data.get("patient_id")}',
                        user_id)
        
        return new_report
    
    # Billing Management
    def create_bill(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create new bill"""
        bills = self._load_data(self.files['bills'])
        
        bill_id = str(uuid.uuid4())
        new_bill = {
            'id': bill_id,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            **data
        }
        
        bills.append(new_bill)
        self._save_data(self.files['bills'], bills)
        self._log_action('CREATE_BILL',
                        f'Created bill for patient {data.get("patient_id")}',
                        user_id)
        
        return new_bill
    
    # Prescription Management
    def create_prescription(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create new prescription"""
        prescriptions = self._load_data(self.files['prescriptions'])
        
        prescription_id = str(uuid.uuid4())
        new_prescription = {
            'id': prescription_id,
            'created_at': datetime.now().isoformat(),
            **data
        }
        
        prescriptions.append(new_prescription)
        self._save_data(self.files['prescriptions'], prescriptions)
        self._log_action('CREATE_PRESCRIPTION',
                        f'Created prescription for patient {data.get("patient_id")}',
                        user_id)
        
        return new_prescription
    
    # Getters for analytics
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        users = self._load_data(self.files['users'])
        return [{k: v for k, v in u.items() if k != 'password'} for u in users]
    
    def get_patients(self) -> List[Dict[str, Any]]:
        """Get all patients"""
        return self._load_data(self.files['patients'])
    
    def get_appointments(self) -> List[Dict[str, Any]]:
        """Get all appointments"""
        return self._load_data(self.files['appointments'])
    
    def get_medicines(self) -> List[Dict[str, Any]]:
        """Get all medicines"""
        return self._load_data(self.files['medicines'])
    
    def get_lab_reports(self) -> List[Dict[str, Any]]:
        """Get all lab reports"""
        return self._load_data(self.files['lab_reports'])
    
    def get_bills(self) -> List[Dict[str, Any]]:
        """Get all bills"""
        return self._load_data(self.files['bills'])
    
    def get_prescriptions(self) -> List[Dict[str, Any]]:
        """Get all prescriptions"""
        return self._load_data(self.files['prescriptions'])
    
    def get_audit_logs(self) -> List[Dict[str, Any]]:
        """Get all audit logs"""
        return self._load_data(self.files['audit_log'])
    
    # Search functionality
    def search_records(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search records in a collection based on query parameters"""
        data = self._load_data(self.files[collection])
        results = []
        
        for record in data:
            matches = True
            for key, value in query.items():
                if key not in record or record[key] != value:
                    matches = False
                    break
            if matches:
                results.append(record)
        
        return results