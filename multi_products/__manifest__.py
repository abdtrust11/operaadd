# -*- coding: utf-8 -*-
{
    'name': "Multi Product Select",
    'summary': """""",
    'description': """""",
    'author': "",
    'website': "",
    'category': '',
    'version': '15.0.0.0',
    'depends': ['base', 'purchase', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/multi_product_wizard_view.xml',
        'views/purchase_order.xml',
        'views/stock_picking.xml',
    ],
}
