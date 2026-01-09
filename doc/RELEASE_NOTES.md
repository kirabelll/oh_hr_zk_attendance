# Open HRMS Biometric Device Integration - Release Notes

## Version 18.0.1.0.0 - January 2026

### New Features
- ✅ **Odoo 18 Compatibility**: Full compatibility with Odoo 18.0
- ✅ **U280 Device Support**: Added support for ZKTeco U280 fingerprint and RFID device
- ✅ **Enhanced Device Management**: Added device model selection and status tracking
- ✅ **Connection Testing**: New test connection feature for troubleshooting
- ✅ **Improved Logging**: Better error handling and logging for device operations
- ✅ **Timeout Configuration**: Configurable connection timeout for different network conditions

### Device Compatibility
- ✅ ZKTeco uFace 202
- ✅ ZKTeco iFace 990  
- ✅ ZKTeco U280 (NEW)
- ✅ Other ZKTeco models using standard protocol

### Technical Improvements
- 🔧 **Library Update**: Migrated from zklib to pyzk for better stability
- 🔧 **Model Enhancements**: Added proper model descriptions and field constraints
- 🔧 **XML Compatibility**: Updated XML views for Odoo 18 compatibility
- 🔧 **Error Handling**: Improved error messages and connection diagnostics
- 🔧 **Performance**: Enhanced attendance sync performance with better duplicate detection

### Installation Requirements
- Python 3.8+
- Odoo 18.0
- pyzk library (`pip install pyzk`)

### Configuration
1. Install the pyzk library
2. Configure device IP and port in HR > Configuration > Biometric Devices
3. Select appropriate device model (U280, uFace 202, iFace 990, or Other)
4. Test connection using the new "Test Connection" button
5. Set employee biometric device IDs to match device enrollment

### Bug Fixes
- 🐛 Fixed datetime handling for different timezones
- 🐛 Resolved XML parsing issues in Odoo 18
- 🐛 Improved duplicate attendance record prevention
- 🐛 Fixed cron job model references

### Migration Notes
- Existing installations will need to install pyzk library
- Device configurations will be preserved during upgrade
- Attendance data remains intact during migration

---

## Previous Versions

### Version 17.0.1.0.0 - December 2023
#### ADD
- Initial commit for Open HRMS Biometric Device Integration
- Support for ZKTeco uFace 202 and iFace 990
- Basic attendance synchronization
- Device management features
