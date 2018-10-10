# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################

{
    "name" : "Odoo Woocommerce Connector",
    "author" : "Globalteckz",
    "category" : "Sales",
    "depends" : ['base','sale_shop','account','delivery','product_images_olbs','stock','sale'],
    "description": """
Odoo Woocommerce Connector to manage all your woocommerce from odoo
odoo 9 woocommerce
odoo 9 woo commerce
odoo 9 woocommerce connector
odoo 9 woo commerce connector
odoo 9 woocommerce integration
odoo 9 woo commerce connector
odoo 10 woocommerce
odoo 10 woo commerce
odoo 10 woocommerce connector
odoo 10 woo commerce connector
odoo 10 woocommerce integration
odoo 10 woo commerce connector
odoo 11 woocommerce
odoo 11 woo commerce
odoo 11 woocommerce connector
odoo 11 woo commerce connector
odoo 11 woocommerce integration
odoo 11 woo commerce connector
other connectors:
Odoo ebay connector 
odoo ebay integration
odoo amazon connector
odoo amazon integration
odoo prestashop connector
odoo prestashop integration
odoo shipstation connector
odoo shipstation integration
odoo woocommerce connector
odoo woo commerce connector
odoo woocommerce integration 
odoo woo commerce integration
""",
    'summary': 'Odoo woocommerce which you can manage all your operations in Odoo',
    "price": "239.00",
    "currency": "EUR",
    'website': 'http://www.globalteckz.com',
    "license" : "Other proprietary",
    'images': ['static/description/woocommerce_banner.png'],
    "data": [
      'security/woocommerce_security.xml',
      'security/ir.model.access.csv',
      'data/product_data.xml',
      'data/woocom_sequence_data.xml',
      
      'views/sale_analysis_view.xml',
      'views/wocommerce_integration_view.xml',
      'views/sale_shop_view.xml',
      'views/woocom_account_view.xml',
      'wizard/woocom_connector_wizard_view.xml',
      'wizard/woocom_export_categ_view.xml',
      'wizard/woocom_export_product_view.xml',
      'wizard/woocom_export_order_view.xml',
      'wizard/woocom_export_customer_view.xml',
      'views/woocommerce_dashboard_view.xml',
      'views/order_workflow_view.xml',
      'views/product_attribute_view.xml',
      'views/woocom_product_view.xml',
      'views/res_partner_view.xml',
      'views/carrier_woocom_view.xml',
      'views/payment_gatway_view.xml',
      'views/woocom_order_view.xml',
      'views/stock_view.xml',
      'views/woocommerce_log_view.xml',
      'views/wocommerce_menus.xml',
      
    ],
    "installable": True,
    "active": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
