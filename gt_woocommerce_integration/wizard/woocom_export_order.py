from openerp import fields,models,api

class export_order_wizard(models.TransientModel):
    
    _name = 'export.order.wiz'
    
    select_instance = fields.Many2one('woocommerce.instance',string='Woocommerce Instance')
    shop_ids = fields.Many2one('sale.shop',string='Shop Id')
     
    @api.multi
    def export_to_woocom(self):
        order_obj = self.env['sale.order']
        export_order = self._context.get('active_ids')
        for export in order_obj.browse(export_order):
            export.write({'to_be_exported':True})
#             
            self.shop_ids.expotWoocomOrder()