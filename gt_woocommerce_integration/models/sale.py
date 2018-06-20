# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models, _

class sale_order(models.Model):
    _inherit = "sale.order"
                                   
    shop_id=fields.Many2one('sale.shop','Shop ID')
#     order_status = fields.Many2one('woocom.order.status', string="Status")
    order_status = fields.Selection([('pending','Pending payment'),('processing','Processing'),('on-hold','On hold'),('completed','Completed')
                                     ,('cancelled','Cancelled'),('refunded','Refunded'),('failed','Failed')], string="Status")
    woocom_order_ref=fields.Char('Order Reference')
    woocom_payment_mode=fields.Many2one('payment.gatway',string='Payment mode')
    carrier_woocommerce=fields.Many2one('delivery.carrier',string='Carrier In Woocommerce')
    woocommerce_order=fields.Boolean('Woocommerce Order')
    token=fields.Char('Token')
    woocom_id =  fields.Char('woocom_id')
    woocom_variant_id = fields.Char('Woocommerce Variant ID')
    shop_ids = fields.Many2many('sale.shop', 'saleorder_shop_rel', 'saleorder_id', 'shop_id', string="Shop")
    to_be_exported = fields.Boolean(string="To be exported?")

class sale_order_line(models.Model):
    _inherit='sale.order.line'
    
    gift=fields.Boolean('Gift')
    gift_message=fields.Char('Gift Message')
    wrapping_cost=fields.Float('Wrapping Cost')
    woocom_id = fields.Char(string="Woocom ID")
    
class WoocomOrderStatus(models.Model):
    _name = 'woocom.order.status'

    name = fields.Char(string="Status")
    woocom_id = fields.Char(string="Woocom ID")
