# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models, _

class delivery_carrier(models.Model):
    
    _inherit = 'delivery.carrier'

    woocom_id = fields.Char(string="Woocom ID")
    delivery_type = fields.Selection([('fixed', 'Fixed Price'), ('base_on_rule', 'Based on Rules')], string='Provider', default='fixed', required=True)
    fixed_price = fields.Float(compute='_compute_fixed_price', inverse='_set_product_fixed_price', store=True, string='Fixed Price',help="Keep empty if the pricing depends on the advanced pricing per destination")
