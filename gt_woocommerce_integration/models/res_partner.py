# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models, _

class res_partner(models.Model):
    _inherit = "res.partner"
                
    woocom_customer=fields.Boolean('Woocommerce customer')
    woocom_paswrd=fields.Char('Password')
    woocom_id = fields.Char('Woocom ID',readonly=True)

    shop_ids = fields.Many2many('sale.shop', 'customer_shop_rel', 'cust_id', 'shop_id', string="Shop")
    manufacturer = fields.Boolean(string="Is Manufacturer?",)
    to_be_exported = fields.Boolean(string="To be exported?")
    address_id = fields.Char('Address ID')
