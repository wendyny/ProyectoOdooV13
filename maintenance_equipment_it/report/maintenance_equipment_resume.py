# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EquipmentResume(models.TransientModel):
    _name = 'maintenance_equipment_it.report.resume.wizard'

    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 index=True,
                                 default=lambda self: self.env.company.id)

    maintenance_team_id = fields.Many2one('maintenance.team',
                                          string='Maintenance Team',
                                          check_company=True)

    def get_report(self):
        self.ensure_one()

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'maintenance_team_id': self.maintenance_team_id.id,
            }
        }
        action = self.env.ref(
            'maintenance_equipment_it.action_report_equipment_resume'
        ).report_action(self, data=data)

        return action


class ReportResume(models.AbstractModel):
    _name = 'report.maintenance_equipment_it.report_equipment_resume'

    @api.model
    def _get_report_values(self, docids, data=None):
        maintenance_team_id = data['form']['maintenance_team_id']

        records = self.env['maintenance.equipment'].search([
            ('maintenance_team_id', '=', maintenance_team_id),
        ], order='category_id, name')

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': records
        }


