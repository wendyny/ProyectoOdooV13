# -*- coding: utf-8 -*-

{
    'name': 'Maintenance Equipment IT',
    'version': '1.0',
    'sequence': 125,
    'category': 'Operations/Maintenance',
    'description': """
        Track equipments and maintenance requests""",
    'depends': ['mail', 'maintenance'],
    'summary': 'Track equipment and manage maintenance requests',
    'website': '',
    'data': [
        'views/maintenance_it_view.xml',
        'report/maintenance_equipment.xml',
        'report/maintenance_equipment_template.xml',

        'report/maintenance_equipment_resume_template.xml',
        'report/maintenance_equipment_resume_wizard.xml',
    ],
    'installable': True,
    'application': True,
}
