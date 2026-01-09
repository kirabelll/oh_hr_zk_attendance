# -*- coding: utf-8 -*-
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################
import pytz
from datetime import datetime
import logging

from .zkconst import *
from struct import unpack
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
try:
    from pyzk import ZK, const
except ImportError:
    _logger.error("Please Install pyzk library.")

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Char(string='Biometric Device ID')


class ZkMachine(models.Model):
    _name = 'zk.machine'
    _description = 'Biometric Device Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Machine IP', required=True, help="IP address of the biometric device")
    port_no = fields.Integer(string='Port No', required=True, default=4370, help="Port number of the biometric device")
    address_id = fields.Many2one('res.partner', string='Working Address', help="Address where the device is located")
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company,
                                help="Company that owns this device")
    device_model = fields.Selection([
        ('uface202', 'uFace 202'),
        ('iface990', 'iFace 990'),
        ('u280', 'U280'),
        ('other', 'Other ZKTeco Model')
    ], string='Device Model', default='u280', help="Select the ZKTeco device model")
    
    timeout = fields.Integer(string='Connection Timeout', default=30, 
                           help="Connection timeout in seconds for device communication")
    
    last_sync_time = fields.Datetime(string='Last Sync Time', readonly=True,
                                   help="Last time attendance data was synchronized")
    
    device_status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Connection Error')
    ], string='Device Status', default='disconnected', readonly=True)

    def device_connect(self, zk):
        """Connect to the biometric device with enhanced error handling for U280"""
        try:
            conn = zk.connect()
            if conn:
                self.device_status = 'connected'
                _logger.info(f"Successfully connected to {self.device_model} device at {self.name}:{self.port_no}")
                return conn
            else:
                self.device_status = 'disconnected'
                return False
        except Exception as e:
            self.device_status = 'error'
            _logger.error(f"Failed to connect to {self.device_model} device at {self.name}:{self.port_no}. Error: {str(e)}")
            return False

    def test_connection(self):
        """Test connection to the biometric device"""
        try:
            zk = ZK(self.name, port=self.port_no, timeout=self.timeout, 
                   password=0, force_udp=False, ommit_ping=False)
            conn = self.device_connect(zk)
            if conn:
                # Get device info for U280
                try:
                    device_name = conn.get_device_name()
                    firmware_version = conn.get_firmware_version()
                    conn.disconnect()
                    
                    message = f"Connection successful!\n"
                    message += f"Device: {device_name}\n"
                    message += f"Firmware: {firmware_version}\n"
                    message += f"Model: {self.device_model}"
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Connection Test',
                            'message': message,
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                except:
                    conn.disconnect()
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Connection Test',
                            'message': 'Connection successful but could not retrieve device info.',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
            else:
                raise UserError(_('Unable to connect to the device. Please check IP address, port, and network connectivity.'))
        except Exception as error:
            raise UserError(f'Connection failed: {str(error)}')

    def clear_attendance(self):
        """Methode to clear record from the zk.machine.attendance model and
        from the device"""
        for info in self:
            try:
                machine_ip = info.name
                zk_port = info.port_no
                try:
                    # Connecting with the device
                    zk = ZK(machine_ip, port=zk_port, timeout=30,
                            password=0, force_udp=False, ommit_ping=False)
                except NameError:
                    raise UserError(_(
                        "Please install it with 'pip3 install pyzk'."))
                conn = self.device_connect(zk)
                if conn:
                    conn.enable_device()
                    clear_data = zk.get_attendance()
                    if clear_data:
                        # Clearing data in the device
                        conn.clear_attendance()
                        # Clearing data from attendance log
                        self._cr.execute(
                            """delete from zk_machine_attendance""")
                        conn.disconnect()
                    else:
                        raise UserError(
                            _('Unable to clear Attendance log.Are you sure '
                              'attendance log is not empty.'))
                else:
                    raise UserError(
                        _('Unable to connect to Attendance Device. Please use '
                          'Test Connection button to verify.'))
            except Exception as error:
                raise ValidationError(f'{error}')

    def restart_device(self):
        """Method to restart the device."""
        zk = ZK(self.name, port=self.port_no, timeout=15, password=0,
                force_udp=False, ommit_ping=False)
        if self.device_connect(zk):
            self.device_connect(zk).restart()
        else:
            raise UserError(
                _('Unable to restart, please check the device is connected.'))

    def getSizeUser(self, zk):
        """Checks a returned packet to see if it returned CMD_PREPARE_DATA,
        indicating that data packets are to be sent

        Returns the amount of bytes that are going to be sent"""
        command = unpack('HHHH', zk.data_recv[:8])[0]
        if command == CMD_PREPARE_DATA:
            size = unpack('I', zk.data_recv[8:12])[0]
            return size
        else:
            return False

    def zkgetuser(self, zk):
        """Start a connection with the time clock"""
        try:
            users = zk.get_users()
            return users
        except:
            return False

    @api.model
    def cron_download(self):
        """cron_download method: Perform a cron job to download attendance data for all machines.

          This method iterates through all the machines in the 'zk.machine' model and
          triggers the download_attendance method for each machine."""
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()

    def download_attendance(self):
        """
         download_attendance method: Download attendance data from a ZKTeco machine including U280.

         This method connects to a ZKTeco machine specified by the 'name', 'port_no', and other parameters,
         retrieves attendance data, and creates corresponding records in 'zk.machine.attendance' and 'hr.attendance'.

         Args:
             None

         Returns:
             bool: True if the download is successful, raises exceptions otherwise.
         """
        _logger.info(f"++++++++++++Cron Executed for {self.device_model} device++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        att_obj = self.env['hr.attendance']
        for info in self:
            machine_ip = info.name
            zk_port = info.port_no
            timeout = info.timeout or 30
            try:
                zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0,
                        force_udp=False, ommit_ping=False)
            except NameError:
                raise UserError(
                    _("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))
            conn = self.device_connect(zk)
            if conn:
                # conn.disable_device() #Device Cannot be used during this time.
                try:
                    user = conn.get_users()
                    _logger.info(f"Retrieved {len(user) if user else 0} users from {info.device_model}")
                except Exception as e:
                    _logger.warning(f"Could not retrieve users from {info.device_model}: {str(e)}")
                    user = False
                try:
                    attendance = conn.get_attendance()
                    _logger.info(f"Retrieved {len(attendance) if attendance else 0} attendance records from {info.device_model}")
                except Exception as e:
                    _logger.warning(f"Could not retrieve attendance from {info.device_model}: {str(e)}")
                    attendance = False
                if attendance:
                    for each in attendance:
                        atten_time = each.timestamp
                        atten_time = datetime.strptime(
                            atten_time.strftime('%Y-%m-%d %H:%M:%S'),
                            '%Y-%m-%d %H:%M:%S')
                        local_tz = pytz.timezone(
                            self.env.user.partner_id.tz or 'GMT')
                        local_dt = local_tz.localize(atten_time, is_dst=None)
                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                        atten_time = datetime.strptime(
                            utc_dt, "%Y-%m-%d %H:%M:%S")
                        atten_time = fields.Datetime.to_string(atten_time)
                        if user:
                            for uid in user:
                                if uid.user_id == each.user_id:
                                    get_user_id = self.env[
                                        'hr.employee'].search(
                                        [('device_id', '=', each.user_id)])
                                    if get_user_id:
                                        duplicate_atten_ids = zk_attendance.search(
                                            [('device_id', '=', each.user_id), (
                                                'punching_time', '=',
                                                atten_time)])
                                        if duplicate_atten_ids:
                                            continue
                                        else:
                                            zk_attendance.create(
                                                {'employee_id': get_user_id.id,
                                                 'device_id': each.user_id,
                                                 'attendance_type': str(
                                                     each.status),
                                                 'punch_type': str(each.punch),
                                                 'punching_time': atten_time,
                                                 'address_id': info.address_id.id})
                                            att_var = att_obj.search([(
                                                'employee_id',
                                                '=',
                                                get_user_id.id),
                                                (
                                                    'check_out',
                                                    '=',
                                                    False)])
                                            if each.punch == 0:  # check-in
                                                if not att_var:
                                                    att_obj.create({
                                                        'employee_id': get_user_id.id,
                                                        'check_in': atten_time})
                                            if each.punch == 1:  # check-out
                                                if len(att_var) == 1:
                                                    att_var.write({
                                                        'check_out': atten_time})
                                                else:
                                                    att_var1 = att_obj.search([(
                                                        'employee_id',
                                                        '=',
                                                        get_user_id.id)])
                                                    if att_var1:
                                                        att_var1[-1].write({
                                                            'check_out': atten_time})

                                    else:
                                        employee = self.env[
                                            'hr.employee'].create(
                                            {'device_id': each.user_id,
                                             'name': uid.name})
                                        zk_attendance.create(
                                            {'employee_id': employee.id,
                                             'device_id': each.user_id,
                                             'attendance_type': str(
                                                 each.status),
                                             'punch_type': str(each.punch),
                                             'punching_time': atten_time,
                                             'address_id': info.address_id.id})
                                        att_obj.create(
                                            {'employee_id': employee.id,
                                             'check_in': atten_time})
                                else:
                                    pass
                    # Update last sync time
                    info.last_sync_time = fields.Datetime.now()
                    # zk.enableDevice()
                    conn.disconnect
                    return True
                else:
                    raise UserError(
                        _('Unable to get the attendance log, please try again later.'))
            else:
                raise UserError(
                    _('Unable to connect, please check the parameters and network connections.'))
