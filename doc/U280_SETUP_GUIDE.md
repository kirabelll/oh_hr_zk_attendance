# ZKTeco U280 Setup Guide

## Overview
The ZKTeco U280 is a fingerprint and RFID card time attendance terminal that is compatible with this Odoo biometric integration module.

## Device Specifications
- **Model**: ZKTeco U280
- **Connectivity**: TCP/IP, USB
- **Capacity**: 3,000 fingerprints, 30,000 cards, 100,000 records
- **Authentication**: Fingerprint, RFID card, Password
- **Communication Protocol**: Standard ZKTeco protocol

## Network Configuration

### 1. Device Network Setup
1. Connect the U280 to your network via Ethernet cable
2. Access the device menu by pressing the Menu key
3. Navigate to: **Comm. → Network → IP Address**
4. Set a static IP address (e.g., 192.168.1.100)
5. Set subnet mask (e.g., 255.255.255.0)
6. Set gateway (your router IP)
7. Save the configuration

### 2. Test Network Connection
1. From a computer on the same network, ping the device IP
2. Ensure the device responds to ping requests

## Odoo Configuration

### 1. Install Required Library
```bash
pip install pyzk
```

### 2. Configure Device in Odoo
1. Go to **HR → Configuration → Biometric Devices**
2. Click **Create**
3. Fill in the details:
   - **Machine IP**: Enter the U280 IP address (e.g., 192.168.1.100)
   - **Port No**: Default is 4370
   - **Working Address**: Select the location where device is installed
   - **Company**: Select your company

### 3. Employee Setup
1. Go to **HR → Employees**
2. Open each employee record
3. In the **HR Settings** tab, enter the **Biometric Device ID**
4. This ID should match the user ID enrolled in the U280 device

## Device Operations

### 1. Download Attendance Data
- Click the **Download Data** button in the device configuration
- This will sync attendance records from U280 to Odoo

### 2. Clear Device Data
- Use **Clear Data** button to remove attendance logs from both device and Odoo
- **Warning**: This action cannot be undone

### 3. Restart Device
- Use **Restart Device** button to remotely restart the U280
- Useful for troubleshooting connection issues

## Troubleshooting

### Connection Issues
1. **Cannot connect to device**:
   - Verify IP address and port number
   - Check network connectivity (ping test)
   - Ensure device is powered on
   - Check firewall settings

2. **No attendance data**:
   - Verify employees have correct Biometric Device ID
   - Check if users are enrolled in the U280 device
   - Ensure attendance records exist on the device

3. **Duplicate records**:
   - The system automatically prevents duplicate entries
   - Check employee device ID mapping

### U280 Specific Settings
1. **Communication Settings**:
   - Protocol: TCP/IP
   - Port: 4370 (default)
   - Timeout: 30 seconds

2. **User Enrollment**:
   - Enroll users directly on the U280 device
   - Note the User ID assigned by the device
   - Use this User ID as the Biometric Device ID in Odoo

## Supported Features
- ✅ Fingerprint authentication
- ✅ RFID card authentication
- ✅ Password authentication
- ✅ Real-time attendance sync
- ✅ Multiple punch types (Check In/Out, Break In/Out, Overtime)
- ✅ Remote device management
- ✅ Automatic cron job for data sync

## Limitations
- Device must be on the same network as Odoo server
- Requires stable network connection for real-time sync
- User enrollment must be done on the device itself

## Support
For technical support or device-specific issues, contact:
- **Email**: odoo@cybrosys.com
- **Website**: https://cybrosys.com