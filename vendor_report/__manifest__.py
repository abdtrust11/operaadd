# -*- coding: utf-8 -*-
{
    'name': "Vendor Report",

    'summary': """
        report show Target details """,


    'author': "Albraa siraj",
    'category': 'inventory',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','sale','purchase','product_category'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_wizard.xml',
        'report/vendor_template.xml',
    ],



}