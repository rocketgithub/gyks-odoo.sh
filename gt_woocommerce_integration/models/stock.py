# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models, _

class stockPicking(models.Model):
    _inherit = "stock.picking"
                                   
    woocom_id = fields.Char(string="Woocom ID")
    is_woocom = fields.Boolean(string="Woocom", default=False)

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        product = []
        for rec in self:
            if rec.product_id.product_tmpl_id.id not in product:
                product.append(rec.product_id.product_tmpl_id.id)
        if product:
            shop_ids = self.env['sale.shop'].search([('woocommerce_shop', '=', True)])
            if shop_ids:
                if shop_ids[0].on_fly_update_stock:
                    shop_ids.with_context(product_ids=product).updateWoocomInventory()
        return res