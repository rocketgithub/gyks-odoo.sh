from openerp import fields,models,api

class export_category_wizard(models.TransientModel):
    
    _name = 'export.categ.wiz'
    
    select_instance = fields.Many2one('woocommerce.instance',string='Woocommerce Instance')
    shop_ids = fields.Many2one('sale.shop',string='Shop Id')
     
    @api.multi
    def export_to_woocom(self):
        prod_obj = self.env['product.category']
        for cat in prod_obj.browse(self.env.context.get('active_ids')):
            self.create_woo_category(cat)
        self.shop_ids.exportWoocomCategories()
        return True
    
#     cates = prod_obj.browse(self.env.context.get('active_ids'))
#     cates.write({'')
#     self.shop_ids.exportWoocomCategories()        
#     

    @api.one
    def get_categ_parent(self, category):
        prod_category_obj = self.env['woocom.category']
        vals = {
            'name': category.name,
            'to_be_exported': True
        }
        category_check = prod_category_obj.search([('name', '=', category.parent_id.name)])
        if not category_check:
            if not category.parent_id:
                vals.update({'parent_id': False})
            else:
                parent_id = self.get_categ_parent(category.parent_id)
                vals.update({'parent_id': parent_id[0].id})
            parent_id = prod_category_obj.create(vals)
            return parent_id
        else:
            parent_id = prod_category_obj.create(vals)
            return parent_id
    
    @api.one
    def create_woo_category(self, category):
        prod_category_obj = self.env['woocom.category']
        category_ids = prod_category_obj.search([('name', '=', category.name)])
        if not category_ids:
            vals = {
                'name': category.name,
                'to_be_exported': True
                }
            parent_category_check = prod_category_obj.search([('name', '=', category.parent_id.name)])
            if not parent_category_check:
                parent_id = self.get_categ_parent(category.parent_id)
                vals.update({'parent_id': parent_id[0].id})
            else:
                vals.update({'parent_id': parent_category_check[0].id})
            cat_id = prod_category_obj.create(vals)
            return cat_id
        else:
            vals = {
                'name': category.name,
                'to_be_exported': True
            }
            parent_category_check = prod_category_obj.search([('name', '=', category.parent_id.name)])
            if not parent_category_check:
                parent_id = self.get_categ_parent(category.parent_id)
                vals.update({'parent_id': parent_id[0].id})
            else:
                vals.update({'parent_id': parent_category_check[0].id})
            category_ids[0].write(vals)
            return category_ids[0]