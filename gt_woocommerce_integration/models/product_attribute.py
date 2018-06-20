# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models, _

class product_attribute(models.Model):
    _inherit='product.attribute'
    
    woocom_id = fields.Char(string='Woocommerce Id')
    prod_attribute = fields.One2many('product.attribute.value','attribute_id',string = 'attribute value')
    shop_ids = fields.Many2many('sale.shop', 'attr_shop_rel', 'attr_id', 'shop_id', string="Shop")

class product_attribute_value(models.Model):
    _inherit= "product.attribute.value"
    
    woocom_id = fields.Char(string='Woocommerce Id')
    
# class product_category(models.Model):
#     _inherit="product.category"
#     
#     woocom_id = fields.Char(string='Woocommerce Id')
#     shop_id = fields.Many2one('sale.shop', 'Shop ID')
#     shop_ids = fields.Many2many('sale.shop', 'categ_shop_rel', 'categ_id', 'shop_id', string="Shop")
#     to_be_exported = fields.Boolean(string="To be exported?")
#     
#     
#     @api.multi
#     def get_leaf(self):
#         for leaf in self:
#             c_ids = self.search([('parent_id','=',leaf.id)])
#             if not c_ids:
#                 leaf.leaf_cat = True
# 
#     woocom_id = fields.Char(string='Woocommerce Id')
#     write_date = fields.Datetime(string="Write Date")
#     shop_id = fields.Many2one('sale.shop', 'Shop ID')
#     shop_ids = fields.Many2many('sale.shop', 'categ_shop_rel', 'categ_id', 'shop_id', string="Shop")
#     leaf_cat = fields.Boolean(compute="get_leaf",string="Leaf Category", default=False)
# #     to_be_exported = fields.Boolean(string="To be exported?")
        
