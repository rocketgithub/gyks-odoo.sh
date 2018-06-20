# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class product_template(models.Model):
    _inherit = 'product.template'

    woocom_categ_ids = fields.Many2many('woocom.category', 'woocomm_product_cat_rel', 'prod_id', 'categ_id', 'Woocommerce Category')
    woocom_product_img_ids = fields.One2many('product.images','product_t_id','Product Images')
    woocom_id = fields.Char('Woocommerce ID')
    product_lngth=fields.Float('Length')
    product_wght=fields.Float('Weight')
    product_hght=fields.Float('Height')
    product_width=fields.Float('Weight')
    woocom_price = fields.Float(string="woocommerce Price")
    woocom_regular_price = fields.Float(string="woo-commerce Regular Price")
    product_to_be_exported = fields.Boolean(string="Product to be exported?")
    woo_categ = fields.Many2one('woocom.category',string = "Woocom Category ID")
    sku =fields.Char('SKU')
    
#     @api.one
#     @api.constrains('woocom_price', 'woocom_regular_price')
#     def _check_woocomm_price(self):
#         if self.woocom_price and self.woocom_regular_price and self.woocom_price >= self.woocom_regular_price:
#             raise ValidationError(_('Please enter in value less then regular price. '))
    
class product_product(models.Model):
    _inherit='product.product'
    
    woocommerce_product=fields.Boolean('Woocommerce Product')
    woocom_variant_id = fields.Char('Woocommerce Variant ID')
    variant_price = fields.Float(string="Variant Price")
    shop_ids = fields.Many2many('sale.shop', 'product_shop_rel', 'product_id', 'shop_id', string="Shop")

class product_images(models.Model):
    _inherit ='product.images'

    product_t_id=fields.Many2one('product.template','Product Images')
    # product_v_id = fields.Many2one('product.product', 'Product Images')
    image_url=fields.Char('Image URL')
    image=fields.Binary('Image')
    woocom_img_id=fields.Integer('Img ID')
    shop_ids = fields.Many2many('sale.shop', 'img_shop_rel', 'img_id', 'shop_id', string="Shop")
    write_date = fields.Datetime(string="Write Date")
 
class woocom_category(models.Model):
    _name ="woocom.category"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'
    
    name = fields.Char('Name', index=True, required=True, translate=True)
    parent_id = fields.Many2one('woocom.category', 'Parent Category', index=True, ondelete='cascade')
    child_id = fields.One2many('woocom.category', 'parent_id', 'Child Categories')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    type = fields.Selection([
        ('view', 'View'),
        ('normal', 'Normal')], 'Category Type', default='normal',
        help="A category of the view type is a virtual category that can be used as the parent of another category to create a hierarchical structure.")
    product_count = fields.Integer(
                    '# Products', compute='_compute_product_count',
                    help="The number of products under this category (Does not consider the children categories)")

    woocom_id = fields.Char("Woocom ID")
    shop_ids = fields.Many2many('sale.shop', 'woocom_category_shop_rel', 'categ_id', 'shop_id', string="Shop")
    to_be_exported = fields.Boolean(string="To be exported?")
    
    def _compute_product_count(self):
        for rec in self:
            product_ids = self.env['product.template'].search([('woocom_categ_ids','=',rec.id)])
            rec.product_count = len(product_ids)

    @api.multi
    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res
            
        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]
        
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            parents = list(category_names)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()
