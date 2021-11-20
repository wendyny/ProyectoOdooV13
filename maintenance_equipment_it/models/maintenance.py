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
        default='good', tracking=True)

    architecture = fields.Selection([
        ('32', '32 bits'),
        ('64', '64 bits')],
        string='Architecture Equipment',  index=True, copy=True,
        default='32')

    ip_address = fields.Char('IP Address', copy=True)
    storage_hdd = fields.Char('Storage HDD', copy=True)
    description_processor = fields.Char('Description Processor', copy=True)
    system_operative = fields.Char('System Operative', copy=True)
    ram_memory = fields.Char('RAM Memory', copy=True)
    active_backup = fields.Boolean('Active Backup', copy=True)
    active_vnc = fields.Boolean('Active VNC', copy=True)
    access_network = fields.Boolean('Access Network', copy=True)
    cod_inventory = fields.Char('Code Inventory', copy=True)
    image_equipment = fields.Image('Image', max_width=1920, max_heigth=1920,
                                   store=True)
    authorization_exit = fields.Boolean('Authorization Exit', copy=False,
                                        default=False)

    depreciation_time = fields.Float('Depreciation Time', store=True,
                                     compute='_compute_depreciation_time',
                                     inverse='_compute_depreciation_date')
    state_warranty = fields.Selection([
        ('none', 'NONE'),
        ('valid', 'VALID'),
        ('obsolete', 'OBSOLETE')],
        string='State Warranty', readonly=True, index=True, store=True,
        default='none', compute='_compute_warranty_equipment')

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




