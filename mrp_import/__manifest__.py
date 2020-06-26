# -*- coding: utf-8 -*-

{
    'name': "Import BOM",
    'summary': """Import BOM""",
    'description': """Import BOM""",
    'author': "Paul Lu",
    'category': 'utils',
    'version': '1.0',
    'depends': ['mrp'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'data': [
        'views/mrp_bom.xml',
        'views/mrp_bom_views.xml',
    ],
    'qweb': [
        'static/src/xml/tree_upload_views.xml',
    ],
    'license': 'LGPL-3',
    'support': 'luss613@gmail.com',
}
