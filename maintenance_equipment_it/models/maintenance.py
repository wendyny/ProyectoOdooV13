# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import api, fields, models, _


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = 'maintenance.equipment'
    _description = 'Maintenance Equipment'

    def button_good(self):
        self.write({'state_equipment': 'good'})

    def button_bad(self):
        self.write({'state_equipment': 'bad'})

    state_equipment = fields.Selection([
        ('good', 'GOOD'),
        ('bad', 'BAD')],
        string='Status Equipment', readonly=True, index=True, copy=False,
        default='good', tracking=True,
        help="Describes the physical condition of the equipment"
             "You can set to: Good when it is working or"
             " Bad when it is damaged")

    architecture = fields.Selection([
        ('32', '32 bits'),
        ('64', '64 bits')],
        string='Architecture Equipment',  index=True, copy=True,
        help="Specifies the architecture of the computer")

    ip_address = fields.Char('IP Address', copy=True,
                             help="Describes the address IP of equipment")

    storage_hdd = fields.Char('Storage HDD', copy=True,
                              help="Specifies storage capacity")

    description_processor = fields.Char('Description Processor', copy=True,
                                        help="Describes the processor of "
                                             "equipment")

    system_operative = fields.Char('System Operative', copy=True,
                                   help="Specifies system operative installed"
                                        "in the computer")

    ram_memory = fields.Char('RAM Memory', copy=True,
                             help="Specifies the capacity of memory ram")

    active_backup = fields.Boolean('Active Backup', copy=True,
                                   help="If the backup system is active")

    active_vnc = fields.Boolean('Active VNC', copy=True,
                                help="If the VNC is installed")

    access_network = fields.Boolean('Access Network', copy=True,
                                    help="If the equipment has access"
                                         "to network")

    cod_inventory = fields.Char('Code Inventory', copy=True,
                                help="Code of inventory give for "
                                     "department accounting")

    image_equipment = fields.Image('Image', max_width=1920, max_heigth=1920,
                                   store=True,
                                   help="Image of equipment")

    authorization_exit = fields.Boolean('Authorization Exit', copy=False,
                                        default=False,
                                        help="If the computer has permission "
                                             "to leave the company")

    depreciation_time = fields.Float('Depreciation Months', store=True,
                                     compute='_compute_depreciation_time',
                                     inverse='_compute_depreciation_date',
                                     help="Time the equipment depreciated")

    state_warranty = fields.Selection([
        ('none', 'NONE'),
        ('valid', 'VALID'),
        ('obsolete', 'OBSOLETE')],
        string='State Warranty', readonly=True, index=True, store=True,
        default='none', compute='_compute_warranty_equipment',
        help="Status of the warranty. "
             "If it is in None means do not has warranty. "
             "But if it is in Valid means is has warranty. "
             "Or Obsolete means your warranty expired")

    brand = fields.Char('Brand',
                        help="Describes the brand of equipment")

    @api.depends('effective_date', 'warranty_date')
    def _compute_depreciation_time(self):
        for equipment in self:
            if equipment.effective_date and equipment.warranty_date:
                seconds = (equipment.warranty_date-equipment.effective_date).\
                    total_seconds()
                equipment.depreciation_time = seconds/(24*60*60)/30

    @api.depends('effective_date', 'depreciation_time')
    def _compute_depreciation_date(self):
        for equipment in self:
            if equipment.effective_date and equipment.depreciation_time:
                equipment.warranty_date = \
                    equipment.effective_date +\
                    timedelta(days=equipment.depreciation_time*30)

    @api.depends('effective_date', 'warranty_date')
    def _compute_warranty_equipment(self):
        for equipment in self:
            if not equipment.effective_date or not equipment.warranty_date:
                equipment.state_warranty = 'none'
            elif equipment.effective_date <= fields.Date.today() <= \
                    equipment.warranty_date:
                equipment.state_warranty = 'valid'
            else:
                equipment.state_warranty = 'obsolete'




