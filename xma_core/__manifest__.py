# -*- coding: utf-8 -*-
{
    'name': "Xma Core",

    'summary': """
        Extablece la conexion de Odoo con el servicio de timbrado""",

    'description': """ 
    """,

    'author': "Xmarts Group LLC",
    'website': "https://www.xmarts.com",
    'category': 'Account',
    'version': '16.0.1',
    'license': 'OPL-1',
    'images': ['static/description/banners/banner.gif'],

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
