# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models, _


class ImportOrderWorkflow(models.Model):
    _name = "import.order.workflow"
    

    name = fields.Char(string="Name")
    validate_order = fields.Boolean(string="Validate Order")
    create_invoice = fields.Boolean(string="Create Invoice")
    validate_invoice = fields.Boolean(string="Validate Invoice")
    register_payment = fields.Boolean(string="Register Payment")
    complete_shipment = fields.Boolean(string="Complete Shipment")
    invoice_policy = fields.Selection(
        [('order', 'Ordered quantities'),
         ('delivery', 'Delivered quantities'),
         ('cost', 'Invoice based on time and material')],
        string='Invoicing Policy', default='order')
    picking_policy = fields.Selection([
        ('direct', 'Deliver each product when available'),
        ('one', 'Deliver all products at once')],
        string='Shipping Policy', required=True, readonly=True, default='direct')
