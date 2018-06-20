from openerp import fields,models,api

class export_product_wizard(models.TransientModel):
    
    _name = 'export.product.wiz'
    
    select_instance = fields.Many2one('woocommerce.instance',string='Woocommerce Instance')
    shop_ids = fields.Many2one('sale.shop',string='Shop Id')
     
    @api.multi
    def export_to_woocom(self):
        prod_tmpl_obj = self.env['product.template']
        export_product = self._context.get('active_ids')
        for export in prod_tmpl_obj.browse(export_product):
            export.write({'product_to_be_exported':True})
#             
            self.shop_ids.exportWoocomProduct()