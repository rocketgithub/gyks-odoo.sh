# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models, _

class account_invoice(models.Model):
    _inherit = "account.invoice"
                
    is_woocom =fields.Boolean('Woocommerce')
    total_discount_tax_excl=fields.Float('Discount(tax excl.)')
    total_discount_tax_incl=fields.Float('Discount(tax incl)')
    total_paid_tax_excl= fields.Float('Paid (tax excl.)')
    total_paid_tax_incl=fields.Float('Paid (tax incl.)')
    total_products_wt=fields.Float('Weight')
    total_shipping_tax_excl=fields.Float('Shipping(tax excl.)')
    total_shipping_tax_incl=fields.Float('Shipping(tax incl.)')
    total_wrapping_tax_excl=fields.Float('Wrapping(tax excl.)')
    total_wrapping_tax_incl=fields.Float('Wrapping(tax incl.)')
    shop_ids = fields.Many2many('sale.shop', 'invoice_shop_rel', 'invoice_id', 'shop_id', string="Shop")

    def invoice_pay_customer_base(self):
        accountinvoice_link = self
        journal_id = self._default_journal()

        if self.type == 'out_invoice':
            self.with_context(type='out_invoice')
        elif self.type == 'out_refund':    
            self.with_context(type='out_refund')
        self.pay_and_reconcile(journal_id,accountinvoice_link.amount_total, False, False)
        return True    
    
account_invoice()

