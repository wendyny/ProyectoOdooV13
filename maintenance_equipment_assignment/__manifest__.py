# -*- coding: utf-8 -*-

{
    'name': 'Maintenance Equipment Assignment',
    'version': '1.0',
    'sequence': 125,
    'category': 'Operations/Maintenance',
    'description': """
        Track equipments and maintenance requests""",
    'depends': ['mail', 'maintenance', 'maintenance_equipment_it'],
    'summary': 'Track equipment and manage maintenance requests',
    'website': '',
    'data': [
        'security/ir.model.access.csv',
        'data/assignment_data.xml',
        'views/maintenance_it_view.xml',
        'report/maintenance_equipment_assignment.xml',
        'report/maintenance_equipment_template.xml',
    ],
    'installable': True,
    'application': True,
    'post_init_hook': 'post_init_hook',
}
