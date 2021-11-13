# -*- coding: utf-8 -*-

{
    'name': 'Maintenance Equipment Diagnostic',
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
        'data/diagnostic_data.xml',
        'views/maintenance_diagnostic_view.xml',
        'report/maintenance_equipment_diagnostic.xml',
        'report/maintenance_equipment_template.xml',
    ],
    'installable': True,
    'application': True,
}
