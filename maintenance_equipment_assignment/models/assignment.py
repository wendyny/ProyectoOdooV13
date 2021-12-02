# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT


class MaintenanceAssignment(models.Model):
    _name = 'maintenance.equipment.assignment'
    _description = 'Maintenance Equipment Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'date_order desc'

    def button_done(self):
        for order in self:
            order.state = 'done'
            order.equipment_id.assign_date = order.date_order
            order.equipment_id.equipment_assign_to = 'employee'
            order.equipment_id.employee_id = order.employee_id
            order.equipment_id.department_id = order.department_employee_id
            order.equipment_id.authorization_exit = order.authorization_exit

    READONLY_STATES = {
        'done': [('readonly', True)],
    }

    company_id = fields.Many2one('res.company',
                                 related='equipment_id.company_id',
                                 string='Company',
                                 store=True, readonly=True,
                                 help="Name of company")

    name = fields.Char('Name', required=True, index=True, copy=False,
                       default='New',
                       help="Name of equipment can be brand and model")

    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment',
                                   required=True,
                                   states=READONLY_STATES,
                                   help="ID of equipment ")

    user_id = fields.Many2one('res.users', string='IT Representative',
                              index=True, tracking=True, readonly=True,
                              default=lambda self: self.env.user,
                              check_company=True,
                              help="User logged in")

    employee_id = fields.Many2one('hr.employee', string='Employee', index=True,
                                  tracking=True, check_company=True,
                                  states=READONLY_STATES, required=True,
                                  help="Employee of company")

    assignment_type = fields.Selection([
        ('assignment', 'Assignment'),
        ('reassignment', 'Reassignment'),
        ('temp', 'Temporal')],
        string='Assignment Type',  index=True, copy=True,
        default='assignment', required=True,
        tracking=True, states=READONLY_STATES,
        help="Assignment for new equipment."
             "Re-assignment for existing equipment."
             "Temporal for defined time assignments. ")

    date_order = fields.Datetime('Order Date', required=True,
                                 index=True,
                                 copy=False, default=fields.Datetime.now,
                                 states=READONLY_STATES,
                                 help="Depicts the date where the assignment"
                                      " should be validated and converted into"
                                      " an assignment equipment.")

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
                                         store=True,
                                         help="Employee Manager")

    reason_assignment = fields.Text('Reasons of Assignment', required=True,
                                    states=READONLY_STATES,
                                    help="Describes the cause of the equipment"
                                         " request")

    origin_assignment = fields.Char('Origin of Assignment',
                                    states=READONLY_STATES,
                                    help="Describe the origin of the "
                                         "equipment")

    notes_assignment = fields.Text('Notes of Assignment',
                                   states=READONLY_STATES,
                                   help="Description of the state in which the"
                                        " equipment is delivered")

    authorization_exit = fields.Boolean('Authorization Exit', copy=False,
                                        default=False, states=READONLY_STATES,
                                        help="If the computer has permission "
                                             "to leave the company")

    date_retirement = fields.Date('Date of Retirement',
                                  states=READONLY_STATES,
                                  help="Date that expires the loan of the "
                                       "equipment")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status', readonly=True, index=True, copy=False,
        default='draft', tracking=True,
        help="Status of the assignment. "
             "If it is in draft you can still modify the assignment."
             "But if it is in done you can not change.")

    def _compute_employee_inv(self):
        pass

    @api.depends('employee_id')
    def _compute_employee_data(self):
        for order in self:
            order.department_employee_id = order.employee_id.department_id
            order.parent_employee_id = order.employee_id.parent_id

            if order.department_employee_id and not order.parent_employee_id:
                order.parent_employee_id = \
                    order.department_employee_id.manager_id

    @api.model
    def create(self, val):
        if self.env['maintenance.equipment'].browse(val['equipment_id']).state_equipment == 'bad':
            raise UserError("This equipment can't assigned")

        if val.get('name', 'New') == 'New':
            company_id = val.get("company_id", self.env.company.id)
            val['name'] = self.env['ir.sequence'].with_context(
                force_company=company_id).next_by_code(
                'maintenance.equipment.assignment') or '/'

        return super(MaintenanceAssignment, self).create(val)


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _inherit = 'maintenance.equipment'
    _description = 'Maintenance Equipment'

    assignment_count = fields.Integer(compute="_compute_assignment",
                                      string='Assignment Count', copy=False,
                                      default=0, store=True,
                                      help="counting of assignments")

    assignment_ids = fields.One2many(comodel_name='maintenance.equipment.assignment',
                                     inverse_name='equipment_id',
                                     string='Assignment', copy=False,
                                     help="Assignments")

    @api.depends('assignment_ids')
    def _compute_assignment(self):
        for order in self:
            assignment = order.mapped('assignment_ids')
            order.assignment_count = len(assignment)

    def get_assignment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignment',
            'view_mode': 'tree,form',
            'res_model': 'maintenance.equipment.assignment',
            'domain': [('equipment_id', 'in', self.ids)],
            'context': {'default_equipment_id': self.ids[0],
                        'search_default_equipment_id': self.ids[0]
                        }
        }

    @api.model
    def create(self, val):
        record = super(MaintenanceEquipment, self).create(val)

        line = {}
        if record.employee_id or \
                (record.department_id and record.department_id.manager_id):
            line = {
                    'equipment_id': record.id,
                    'assignment_type': 'assignment',
                    'date_order': record.assign_date or fields.Datetime.now(),
                    'employee_id': record.employee_id.id or
                                   record.department_id.manager_id.id,
                    'reason_assignment': 'Asignación inicial',
                    'state': 'done'
                }
        else:
            line = {
                    'equipment_id': record.id,
                    'assignment_type': 'assignment',
                    'date_order': record.assign_date or fields.Datetime.now(),
                    'employee_id': self.env.user.employee_ids[0].id,
                    'reason_assignment': 'Asignación inicial a IT',
                    'state': 'done'
                }

        record.assignment_ids.create(line)

        return record





