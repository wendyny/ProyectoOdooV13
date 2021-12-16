# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT


class MaintenanceDiagnostic(models.Model):
    _name = 'maintenance.equipment.diagnostic'
    _description = 'Maintenance Equipment Diagnostic'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'date_order desc'

    def button_done(self):
        self.write({'state': 'done'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def button_draft(self):
        self.write({'state': 'draft'})

    READONLY_STATES = {
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    company_id = fields.Many2one('res.company',
                                 related='equipment_id.company_id',
                                 string='Company',
                                 store=True, readonly=True,
                                 help="Name of company")

    name = fields.Char('Name', required=True, index=True, copy=False,
                       default='New',
                       help="New diagnostic")

    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment',
                                   states=READONLY_STATES,
                                   required=True, help="ID of equipment ")

    user_id = fields.Many2one('res.users', string='IT Representative',
                              index=True, tracking=True, readonly=True,
                              default=lambda self: self.env.user,
                              check_company=True,
                              help="User logged in")

    employee_id = fields.Many2one('hr.employee', string='Employee', index=True,
                                  compute='_compute_employee_data',
                                  check_company=True,
                                  required=True,
                                  store=True,
                                  copy=True,
                                  help="Employee of company")

    date_order = fields.Datetime('Order Date', required=True,
                                 index=True,
                                 copy=False, default=fields.Datetime.now,
                                 states=READONLY_STATES,
                                 help="Depicts the date where the diagnostic"
                                      " should be validated and converted into"
                                      " an diagnosed equipment.")

    department_employee_id = fields.Many2one('hr.department',
                                             string='Department',
                                             compute='_compute_employee_data',
                                             inverse="_compute_employee_inv",
                                             states=READONLY_STATES,
                                             store=True,
                                             help="Department according to"
                                                  " the employee")

    parent_employee_id = fields.Many2one('hr.employee', string='Parent',
                                         compute='_compute_employee_data',
                                         inverse="_compute_employee_inv",
                                         states=READONLY_STATES,
                                         store=True, help="Employee Manager")

    reason_diagnostic = fields.Text('Reasons of diagnostic', required=True,
                                    states=READONLY_STATES,
                                    help="Describes the cause of the service "
                                         "request")

    description_diagnostic = fields.Text('Description of diagnostic',
                                         states=READONLY_STATES,
                                         required=True,
                                         help="Describe the service "
                                              "intervention")

    suggestion_diagnostic = fields.Text('Suggestions of diagnostic',
                                        states=READONLY_STATES,
                                        required=True,
                                        help="Describe the suggested solution"
                                             " to the equipment")

    accessories_equipment = fields.Char('Accessories_equipment',
                                        states=READONLY_STATES,
                                        default='N/A',
                                        help="Describe the additional"
                                             "components")

    state = fields.Selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
            ], string='Status', readonly=True, index=True, copy=False,
            default='draft', tracking=True,
            help="Status of the assignment."
                 "If it is in draft you can still modify the assignment."
                 "But if it is in done you can not change.")


    def _compute_employee_inv(self):
        pass

    @api.depends('equipment_id')
    def _compute_employee_data(self):
        for order in self:
            order.employee_id = order.equipment_id.employee_id
            order.parent_employee_id = order.employee_id.parent_id

            if order.employee_id:
                order.department_employee_id = order.employee_id.department_id

            if order.department_employee_id and not order.parent_employee_id:
                order.parent_employee_id = \
                    order.department_employee_id.manager_id

    @api.model
    def create(self, val):
        if val.get('name', 'New') == 'New':
            company_id = val.get("company_id", self.env.company.id)
            val['name'] = self.env['ir.sequence'].with_context(
                force_company=company_id).next_by_code(
                'maintenance.equipment.diagnostic') or '/'

        return super(MaintenanceDiagnostic, self).create(val)


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = 'maintenance.equipment'
    _description = 'Maintenance Equipment'

    diagnostic_count = fields.Integer(compute="_compute_diagnostic",
                                      string='Diagnostic Count', copy=False,
                                      default=0, store=True,
                                      help="counting of diagnostics")

    diagnostic_ids = fields.One2many(comodel_name=
                                     'maintenance.equipment.diagnostic',
                                     inverse_name='equipment_id',
                                     string='Assignment', copy=False,
                                     help="Diagnostics")

    @api.depends('diagnostic_ids')
    def _compute_diagnostic(self):
        for order in self:
            diagnostic = order.mapped('diagnostic_ids')
            order.diagnostic_count = len(diagnostic)

    def get_diagnostic(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Diagnostic',
            'view_mode': 'tree,form',
            'res_model': 'maintenance.equipment.diagnostic',
            'domain': [('equipment_id', 'in', self.ids)],
            'context': {'default_equipment_id': self.ids[0],
                        'search_default_equipment_id': self.ids[0]
                        }
        }


