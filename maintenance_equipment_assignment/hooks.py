# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, fields, api, _
from odoo.exceptions import UserError


def post_init_hook(cr, registry):
    # logging.getLogger("odoo.addons.maintenance_equipment_assignment").info(
    #     "Migrating existing equipment"
    # )

    env = api.Environment(cr, SUPERUSER_ID, {})
    equipments = env["maintenance.equipment"].search([])

    for equipment in equipments:
        employee_id = None
        if equipment.employee_id:
            employee_id = equipment.employee_id.id
        elif equipment.department_id and equipment.department_id.manager_id:
            employee_id = equipment.department_id.manager_id.id
        elif env.user.employee_ids:
            employee_id = env["users"].employee_ids[0].id

        if employee_id:
            equipment.write({'equipment_assign_to': 'employee',
                             'employee_id': employee_id})
            env["maintenance.equipment.assignment"].create(
                {
                    'equipment_id': equipment.id,
                    'assignment_type': 'assignment',
                    'date_order': equipment.assign_date or fields.Datetime.now(),
                    'employee_id': employee_id,
                    'reason_assignment': 'Asignación inicial',
                    'origin_assignment': 'IT',
                    'authorization_exit': equipment.authorization_exit,
                    'state': 'done'
                }
            )
