# -*- coding: utf-8 -*-
{
    'name': "Odoo Magento2 Connector",

    'summary': """
       Odoo Magento2 Connector""",

    'description': """
       Odoo Magento2 Connector
    """,

    'author': "Magenest",
    'website': "https://store.magenest.com",
    'category': 'Accounting/Accounting',
    'version': '1.0',
    'depends': ['base', 'account', 'sale', 'sale_management', 'product', 'payment', 'stock', 'website_sale'],
    'images': ['static/description/images/Odoo---Magento2-2.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/config/magento_instance.xml',
        'views/dashboard/website.xml',
        'views/test_product/test_product.xml',
        'views/dashboard/store.xml',
        'views/dashboard/storeview.xml',
        'views/dashboard/dashboard_view.xml',
        'views/stock_location/stock_location_view.xml',
        'views/product/product_template_sync.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
