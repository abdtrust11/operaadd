# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
{
    "name": "BSTT Account Invoice",
    "summary": "Extends the Account Invoice "
               "amount",
    "version": "14.0.1.0.0",
    "category": "Invoicing",
    "author": "BSTT",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ['base', 'web'],
    "data": [
        'security/account_security.xml',
        #'views/assets.xml',
        'views/company.xml',
        'views/partner.xml',
        'reports/invoice_report.xml',
        #'reports/base_document_layout.xml',
    ],
    'qweb': [

    ],
}
