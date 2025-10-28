# Hospital Management System

## Overview
A comprehensive hospital management system built with Python, featuring advanced appointment scheduling with duration management and conflict prevention.

## Key Features

### 1. Appointment Duration Management
- **Flexible Duration Options**
  - 15 minutes to 2 hours
  - Common presets: 15min, 30min, 45min, 1hr, 1.5hrs, 2hrs
  - Default duration: 30 minutes
  - Easy selection via dropdown interface

### 2. Conflict Prevention System
- **Automatic Conflict Detection**
  - Real-time schedule checking
  - Doctor-specific availability tracking
  - Smart conflict validation algorithm
- **User-Friendly Error Handling**
  - Clear conflict notifications
  - Alternative slot suggestions
  - Visual timeline indicators

### 3. Schedule Management
- **Efficient Time Slot System**
  - Visual calendar interface
  - Time slot validation
  - Past date prevention
  - Buffer time management

## Technical Implementation

### 1. Duration Management
```python
# Duration options
durations = [
    '15 min',
    '30 min',
    '45 min',
    '1 hour',
    '1.5 hours',
    '2 hours'
]

def _convert_duration_to_minutes(duration_str):
    """Convert duration string to minutes"""
    if 'min' in duration_str:
        return int(duration_str.split()[0])
    elif 'hour' in duration_str:
        hours = float(duration_str.split()[0])
        return int(hours * 60)
    return 30  # default
```

### 2. Conflict Detection
```python
def _check_appointment_conflict(appointments, start_time, end_time, doctor_id):
    """Check for overlapping appointments"""
    for appt in appointments:
        if appt['doctor_id'] == doctor_id:
            appt_date = datetime.strptime(f"{appt['date']} {appt['time']}", "%Y-%m-%d %H:%M")
            duration = _convert_duration_to_minutes(appt.get('duration', '30 min'))
            appt_end = appt_date + timedelta(minutes=duration)
            
            if not (end_time <= appt_date or start_time >= appt_end):
                return True
    return False
```

### 3. Appointment Data Structure
```python
appointment = {
    'id': 'A001',
    'patient_id': 'P001',
    'doctor_id': 'D001',
    'date': '2025-10-27',
    'time': '09:00',
    'duration': '30 min',
    'purpose': 'Regular checkup',
    'status': 'Scheduled'
}
```

## Usage Guide

### 1. Scheduling an Appointment
1. Open the appointment form
2. Select patient and doctor
3. Choose appointment date
4. Select time slot
5. Choose duration from dropdown
6. System validates for conflicts
7. Confirm booking if no conflicts

### 2. Managing Time Slots
- Default slot duration: 30 minutes
- Minimum duration: 15 minutes
- Maximum duration: 2 hours
- Buffer between appointments: 5 minutes

### 3. Handling Conflicts
1. System checks for overlapping appointments
2. Shows error message if conflict detected
3. Suggests alternative time slots
4. Prevents double-booking

## Best Practices

### 1. Time Management
- Always validate time slots
- Include buffer time
- Check for past dates
- Validate working hours

### 2. Conflict Prevention
- Check overlapping appointments
- Validate doctor availability
- Consider emergency slots
- Maintain scheduling rules

### 3. User Interface
- Clear duration selection
- Visual conflict indicators
- Intuitive calendar display
- Easy slot navigation

## Contributing
See CONTRIBUTING.md for guidelines.

## License
MIT License - see LICENSE.md for details.

### Patient Management 🏥
- Complete patient records management
- Patient history tracking
- Appointment scheduling
- Medical record documentation

### Doctor Management 👨‍⚕️
- Doctor profiles and specializations
- Appointment scheduling
- Patient assignment
- Work schedule management

### Pharmacy Module 💊
- Medicine inventory management
- Stock tracking and alerts
- Prescription management
- Billing integration

### Laboratory Module 🔬
- Lab test management
- Report generation
- Result tracking
- Sample management

### Billing System 💰
- Automated bill generation
- Service-based billing
- Payment tracking
- PDF bill generation
- Multiple payment methods
- Tax calculation

### Analytics and Reporting 📊
- Patient statistics
- Revenue analysis
- Department workload visualization
- Appointment trends
- Medicine stock analysis
- Lab test distribution
- Patient demographics

### Emergency Services 🚑
- Quick patient registration
- Priority appointment scheduling
- Emergency contact management

## Technical Features ⚙️

### Security
- Password hashing using SHA-256
- Role-based access control
- Audit logging
- Session management

### Data Management
- JSON-based data storage
- Automatic backup
- Data validation
- CRUD operations for all entities

### User Interface
- Modern, intuitive design
- Responsive layouts
- Interactive charts and graphs
- Context menus
- Search and filter capabilities

### Documentation
- PDF report generation
- Printable bills and reports
- Data export capabilities

## Installation 📥

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hospital-management.git
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

Required packages:
- tkinter
- matplotlib
- pillow
- qrcode
- reportlab
- seaborn

3. Run the application:
```bash
python main.py
```

## Default Credentials 🔑

| Role      | Username  | Password      |
|-----------|-----------|---------------|
| Admin     | admin     | admin123      |
| Reception | reception | reception123  |
| Doctor    | doctor1   | doctor123     |
| Pharmacy  | pharmacy  | pharmacy123   |
| Lab       | lab       | lab123        |

## File Structure 📁

```
hospital_management/
│
├── main.py                 # Main application entry point
├── data_manager.py         # Data management and storage
├── analytics_manager.py    # Analytics and visualization
├── billing_module.py       # Billing system
│
├── data/                   # Data storage
│   ├── patients.json
│   ├── doctors.json
│   ├── appointments.json
│   ├── medicines.json
│   ├── lab_reports.json
│   ├── bills.json
│   └── users.json
│
└── exports/               # Exported reports and bills
```

## Usage Guide 📖

### Admin Dashboard
- Manage users and roles
- View system analytics
- Configure system settings
- Monitor all departments

### Reception Dashboard
- Register new patients
- Schedule appointments
- Manage billing
- Handle emergency cases

### Doctor Dashboard
- View assigned patients
- Manage appointments
- Write prescriptions
- Order lab tests

### Pharmacy Dashboard
- Manage medicine inventory
- Process prescriptions
- Update stock levels
- Generate reports

### Laboratory Dashboard
- Manage lab tests
- Record test results
- Generate lab reports
- Track samples

## Data Backup 💾

The system automatically maintains data in JSON format in the `data` directory. It's recommended to:
1. Regularly backup the `data` directory
2. Keep backup copies in a secure location
3. Implement scheduled backups

## Security Features 🔒

1. Password Protection
   - All passwords are hashed using SHA-256
   - Secure login system
   - Session management

2. Access Control
   - Role-based access control
   - Feature restriction based on user role
   - Action logging

3. Audit Trail
   - All actions are logged
   - User activity tracking
   - Change history maintenance

## Troubleshooting 🔧

Common issues and solutions:

1. Database Access
   - Ensure write permissions in the data directory
   - Check file permissions
   - Verify JSON file integrity

2. Display Issues
   - Update Python and Tkinter
   - Check screen resolution
   - Verify required packages

3. PDF Generation
   - Ensure ReportLab is properly installed
   - Check write permissions
   - Verify printer configuration

## Contributing 🤝

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 📞

For support:
- Create an issue in the repository
- Contact system administrator
- Check documentation

## Future Enhancements 🚀

Planned features:
- Electronic Health Records (EHR)
- Online appointment booking
- SMS/Email notifications
- Insurance integration
- Mobile application
- Cloud backup
- Telemedicine support
- AI-powered diagnostics

---

Made with ❤️ for healthcare professionals

## Using a custom QR code for payments and bills

If you want to use your own QR code (for UPI or other payment receivers) instead of the automatically generated one, place your QR image file in the `data` folder with one of these names:

- `data/user_qr.png`
- `data/user_qr.jpg`
- `data/user_qr.jpeg`

The application will automatically use this image in the payment GUI and in generated PDF bills (if present). If the file is not found or cannot be loaded, the app will fall back to generating a QR code dynamically.

Example: copy your attached QR image to `d:\PUZZLE\HOSPITAL\test1\data\user_qr.png` and then open the payment window or regenerate a bill.

Default UPI configuration
-------------------------
You can set a default UPI ID used when the app needs to generate a payment QR. Create or edit `data/config.json` and set the `upi_id` key. Example:

```
{
   "upi_id": "7013968958@fam"
}
```

If `data/user_qr.png` is present the app will use that image instead of generating a QR from the configured UPI id.