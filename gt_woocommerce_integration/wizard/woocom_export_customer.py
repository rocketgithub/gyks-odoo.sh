from openerp import fields,models,api

class export_customer_wizard(models.TransientModel):
    
    _name = 'export.customer.wiz'
    
    select_instance = fields.Many2one('woocommerce.instance',string='Woocommerce Instance')
    shop_ids = fields.Many2one('sale.shop',string='Shop Id')
     
    @api.multi
    def export_to_woocom(self):
        cust_obj = self.env['res.partner']
        export_cust = self._context.get('active_ids')
        for export in cust_obj.browse(export_cust):
            export.write({'to_be_exported':True})
#             
            self.shop_ids.exportWoocomCustomers()