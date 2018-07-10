# -*- coding: utf-8 -*-
#############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
from odoo.addons.gt_woocommerce_integration.api import API
import logging
from datetime import timedelta, datetime, date, time
import time
logger = logging.getLogger('__name__')
import urllib
import base64
import sys, json
from odoo.exceptions import UserError
class SaleShop(models.Model):
    _inherit = "sale.shop"

    code = fields.Char(srting='Code')
    name = fields.Char('Name')

    woocommerce_shop = fields.Boolean(srting='Woocommerce Shop')
    woocommerce_instance_id = fields.Many2one('woocommerce.instance', srting='Woocommerce Instance', readonly=True)
#     woocommerce_id = fields.Char(string='shop Id')

    # ## Product Configuration
    product_import_condition = fields.Boolean(string="Create New Product if Product not in System while import order", default=True)
#     route_ids = fields.Many2many('stock.location.route', 'shop_route_rel', 'shop_id', 'route_id', string='Routes')

    # Order Information
    company_id = fields.Many2one('res.company', srting='Company', required=False,
                                 default=lambda s: s.env['res.company']._company_default_get('stock.warehouse'))
    prefix = fields.Char(string='Prefix')
    suffix = fields.Char(string='Suffix')
    shipment_fee_product_id = fields.Many2one('product.product', string="Shipment Fee", domain="[('type', '=', 'service')]")
    gift_wrapper_fee_product_id = fields.Many2one('product.product', string="Gift Wrapper Fee", domain="[('type', '=', 'service')]")
    sale_journal = fields.Many2one('account.journal')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')
    partner_id = fields.Many2one('res.partner', string='Customer')
    workflow_id = fields.Many2one('import.order.workflow', string="Order Workflow")
    on_fly_update_order_status = fields.Boolean(string="Update on Shop at time of Odoo Order Status Change", default=True)
    # stock Configuration
    on_fly_update_stock = fields.Boolean(string="Update on Shop at time of Odoo Inventory Change", default=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

    # Schedular Configuration
    auto_import_order = fields.Boolean(string="Auto Import Order", default=True)
    auto_import_products = fields.Boolean(string="Auto Import Products", default=True)
    auto_update_inventory = fields.Boolean(string="Auto Update Inventory", default=True)
    auto_update_order_status = fields.Boolean(string="Auto Update Order Status", default=True)
    auto_update_product_data = fields.Boolean(string="Auto Update Product data", default=True)
    auto_update_price = fields.Boolean(string="Auto Update Price", default=True)

    # Import last date
    last_woocommerce_inventory_import_date = fields.Datetime(srting='Last Inventory Import Time')
    last_woocommerce_product_import_date = fields.Datetime(srting='Last Product Import Time')
    last_woocommerce_product_attrs_import_date = fields.Datetime(srting='Last Product Attributes Import Time')
    last_woocommerce_order_import_date = fields.Date(srting='Last Order Import Time')
    last_woocommerce_msg_import_date = fields.Datetime(srting='Last Message Import Time')


    # Update last date
    woocommerce_last_update_category_date = fields.Datetime(srting='Woocom last update category date')
    woocommerce_last_update_inventory_date = fields.Datetime(srting='Woocom last update inventory date')
    woocommerce_last_update_catalog_rule_date = fields.Datetime(srting='Woocom last update catalog rule date')
    woocommerce_last_update_product_data_date = fields.Datetime(srting='Woocom last update product data rule date')
    woocommerce_last_update_order_status_date = fields.Datetime(srting='Woocom last update order status date')

    # Export last date
    prestashop_last_export_product_data_date = fields.Datetime(string='Last Product Export Time')
    
    @api.one
    def create_woo_attr(self, attr_val, wcapi):
        prod_att_obj = self.env['product.attribute']
        prod_attr_vals_obj = self.env['product.attribute.value']
        attribute_val = {
                'name':attr_val.get('name'),
                'woocom_id' : attr_val.get('id'),
        }
        attrs_ids = prod_att_obj.search([('woocom_id', '=', attr_val.get('id'))])
        if not attrs_ids:
           
            att_id = prod_att_obj.create(attribute_val)
        else:
            attrs_ids[0].write(attribute_val)
            att_id = attrs_ids[0]
        logger.info('Value ===> %s', att_id.name)
        attribute_value_rul = "products/attributes/" + str(attr_val.get('id')) + "/terms"
        attr_value_list = wcapi.get(attribute_value_rul)
        attr_value_list = attr_value_list.json()
        if attr_value_list.get('product_attribute_terms'):
            for attr_val in attr_value_list.get('product_attribute_terms'):
                attrs_op_val = {
                    'attribute_id': att_id.id,
                    'woocom_id': attr_val.get('id'),
                    'name': attr_val.get('slug'),
                }
                attrs_ids = prod_attr_vals_obj.search([('woocom_id', '=', attr_val.get('id')), ('attribute_id', '=', att_id.id)])
                if attrs_ids:
                    attrs_ids[0].write(attrs_op_val)
                else:
                    v_id = prod_attr_vals_obj.create(attrs_op_val)
           
    
    @api.multi
    def importWoocomAttribute(self):
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=False, version='v3')
#             try:
            r = wcapi.get("products/attributes")
            logger.error('rrrrrrrrrr ===> %s', r.text)
            if not r.status_code:
                raise UserError(_("Enter Valid url"))
            attribute_list = r.json()
            if attribute_list.get('product_attributes'):
#                     try:
                for attribute in attribute_list.get('product_attributes'):
                    shop.create_woo_attr(attribute, wcapi)
#                     except Exception as e:
#                         if self.env.context.get('log_id'):
#                             log_id = self.env.context.get('log_id')
#                             self.env['log.error'].create({'log_description': str(e) + " While Getting Atribute info of %s" % (attribute_list.get('product_attributes')), 'log_id': log_id})
#                         else:
#                             log_id = self.env['woocommerce.log'].create({'all_operations':'import_attribute', 'error_lines': [(0, 0, {'log_description': str(e) + " While Getting Atribute info of %s" % (attribute_list.get('product_attributes'))})]})
#                             self = self.with_context(log_id=log_id.id)
#             except Exception as e:
#                 if self.env.context.get('log_id'):
#                     log_id = self.env.context.get('log_id')
#                     self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
#                 else:
#                     log_id = self.env['woocommerce.log'].create({'all_operations':'import_attributes', 'error_lines': [(0, 0, {'log_description': str(e)})]})
#                     self = self.with_context(log_id=log_id.id)
        return True
    
    @api.one
    def get_categ_parent(self, category, wcapi):
        prod_category_obj = self.env['woocom.category']
        vals = {
            'woocom_id': str(category.get('id')),
            'name': category.get('name'),
        }
        category_check = prod_category_obj.search([('woocom_id', '=', category.get('parent'))])
        if not category_check:
            if int(category.get('parent')) == 0:
                vals.update({'parent_id': False})
            else:
                cat_url = 'products/categories/' + str(category.get('parent'))
                valsss = wcapi.get(cat_url)
                valsss = valsss.json()
                parent_id = self.get_categ_parent(valsss, wcapi)[0]
                vals.update({'parent_id': parent_id[0].id})
            parent_id = prod_category_obj.create(vals)
            logger.info('Created Category ===> %s' % (parent_id.id))
            if parent_id:
                self.env.cr.execute("select categ_id from woocom_category_shop_rel where categ_id = %s and shop_id = %s" % (
                    parent_id.id, self.id))
                categ_data = self.env.cr.fetchone()
                if categ_data == None:
                    self.env.cr.execute("insert into woocom_category_shop_rel values(%s,%s)" % (parent_id.id, self.id))
            return parent_id
        else:
            parent_id = prod_category_obj.create(vals)
            if parent_id:
                self.env.cr.execute("select categ_id from woocom_category_shop_rel where categ_id = %s and shop_id = %s" % (
                    parent_id.id, self.id))
                categ_data = self.env.cr.fetchone()
                if categ_data == None:
                    self.env.cr.execute("insert into woocom_category_shop_rel values(%s,%s)" % (parent_id.id, self.id))
            return parent_id
    
    @api.one
    def create_woo_category(self, category, wcapi):
        
        prod_category_obj = self.env['woocom.category']
        category_check = prod_category_obj.search([('woocom_id', '=', category.get('id'))])
        if not category_check:
            vals = {
                'woocom_id': str(category.get('id')),
                'name': category.get('name'),
                }
            print("vals==category=====",vals)
            parent_category_check = prod_category_obj.search([('woocom_id', '=', category.get('parent'))])
            if not parent_category_check:
                if int(category.get('parent')) != 0:
                    cat_url = 'products/categories/' + str(category.get('parent'))
                    valsss = wcapi.get(cat_url)
                    valsss = valsss.json()
               
                    parent_id = self.get_categ_parent(valsss.get("product_category"), wcapi)[0].id
                else:
                    parent_id = False
                vals.update({'parent_id': parent_id})
            else:
                vals.update({'parent_id': parent_category_check[0].id})
            logger.info('Created vals ===> %s' % vals)
            cat_id = prod_category_obj.create(vals)
            logger.info('Created Category ===> %s' % (cat_id.id))
            return cat_id
        else:
            vals = {
                'woocom_id': str(category.get('id')),
                'name': category.get('name'),
            }
            parent_category_check = prod_category_obj.search([('woocom_id', '=', category.get('parent'))])
            if not parent_category_check:
                if int(category.get('parent')) != int('0'):
                    cat_url = 'products/categories/' + str(category.get('parent'))
                    valsss = wcapi.get(cat_url)
                    valsss = valsss.json()
                    parent_id = self.get_categ_parent(valsss, wcapi)[0].id
                else:
                    parent_id = False
                vals.update({'parent_id': parent_id})
            else:
                vals.update({'parent_id': parent_category_check[0].id})
            category_check[0].write(vals)
            return category_check[0]
    
    @api.multi
    def importWooCategory(self):
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            try:
                count = 1
                categ = wcapi.get("products/categories?page="+ str(count))
                if not categ.status_code:
                    raise UserError(_("Enter Valid url"))
                category_list = categ.json()
#                 try:
                for category in category_list:
                    shop.create_woo_category(category, wcapi)
                while len(category_list) > 0:
                    count += 1
                    categ = wcapi.get("products/categories?page="+ str(count))
                    category_list = categ.json()
                    for category in category_list:
                        shop.create_woo_category(category, wcapi)
#                 except Exception as e:
#                     if self.env.context.get('log_id'):
#                         log_id = self.env.context.get('log_id')
#                         self.env['log.error'].create({'log_description': str(e) + " While Getting product categories info of %s" % (category_list.get('product_categories')), 'log_id': log_id})
#                     else:
#                         log_id = self.env['woocommerce.log'].create({'all_operations':'import_categories', 'error_lines': [(0, 0, {'log_description': str(e) + " While Getting product categories info of %s" % (category_list.get('product_categories'))})]})
#                         self = self.with_context(log_id=log_id.id)
            except Exception as e:
                if self.env.context.get('log_id'):
                    log_id = self.env.context.get('log_id')
                    self.env['log.error'].create({'log_description': str(e), 'log_id': log_id})
                else:
                    log_id = self.env['woocommerce.log'].create({'all_operations':'import_categories', 'error_lines': [(0, 0, {'log_description': str(e)})]})
                    self = self.with_context(log_id=log_id.id)
        return True
    
    
    @api.one
    def create_woocom_product(self, product, wcapi):
        prod_temp_obj = self.env['product.template']
        product_obj = self.env['product.product']
        att_val_obj = self.env['product.attribute.value']
        att_obj = self.env['product.attribute']
        category_obj = self.env['woocom.category']
        product_att_line_obj = self.env['product.attribute.line']
        prd_tmp_vals = {
            'name': product.get('name'),
            'type': 'product',
            'list_price': product.get('sale_price') and float(product.get('sale_price')) or 0.00,
            'default_code': product.get('sku'),
            'description': product.get('short_description'),
            'woocom_regular_price': product.get('regular_price') and float(product.get('regular_price')) or 0.00,
            'woocom_id': product.get('id'),
            'woocom_price' : product.get('price') and float(product.get('price')) or 0.00,
            'product_lngth': product.get('dimensions').get('length'),
            'product_width': product.get('dimensions').get('width'),
            'product_hght': product.get('dimensions').get('height'),
            'product_wght': product.get('dimensions').get('weight'),
        }
        if product.get('categories'):
            categ = product.get('categories')
            if isinstance(product.get('categories'), dict):
                categ = [categ]
            cat = product.get('categories')[len(product.get('categories'))- 1]
            cat_ids = category_obj.search([('woocom_id', '=', cat.get('id'))])
            if cat_ids:
                categ_id = cat_ids[0]
                logger.info('product categ id ===> %s', categ_id.name)
                prd_tmp_vals.update({'woo_categ': categ_id.id})
            else:
                self.importWooCategory()
                cat_ids = category_obj.search([('woocom_id', '=', cat.get('id'))])
                if cat_ids:
                    prd_tmp_vals.update({'woo_categ': cat_ids[0].id})
        img_ids = []
        images_list = product.get('images')
        count = 1
#        if images_list:
 #           for imgs in images_list:
  #              loc = imgs.get('src').split('/')
   #             image_name = loc[len(loc) - 1]
    #            img_vals = {
     #                 'name': image_name,
      #                'link': True ,
       #               'url':imgs.get('src'),
        #              'woocom_img_id' : imgs.get('id')
         #       } 
          #      if count == 1:
           #         file_contain = urllib.urlopen(imgs.get('src')).read()
            #        image_data = base64.encodestring(file_contain)
             #       prd_tmp_vals.update({'image_medium': image_data})
              #  img_ids.append((0, 0, img_vals))
         #   prd_tmp_vals.update({'woocom_product_img_ids':img_ids})


#    attributes line
        at_lines = []  
        
        for attrdict in product.get('attributes'):
            attrs_ids = att_obj.search([('name','=',attrdict.get('name'))])
            att_id = False
            if attrs_ids:
                att_id = attrs_ids[0]
                logger.info('product attribute id ===> %s', att_id.name)
            else:
                self.importWoocomAttribute()   
                attrs_ids = att_obj.search([('name','=',attrdict.get('name'))])
                if attrs_ids:
                    att_id = attrs_ids[0]
            if att_id:
                value_ids=[]
                option = []
                if 'options' in attrdict:
                    option = attrdict.get('options')
                elif attrdict.get('option'):
                    option = attrdict.get('option')
                if isinstance(option, dict):
                    option = [option]
                for value in option:
                    v_ids = att_val_obj.search([('name','=',value.lower())])
                    if v_ids:
                        value_ids.append(v_ids[0].id)
                if value_ids:
                    at_lines.append((0, 0, {
                        'attribute_id': att_id.id,
                        'value_ids': [(6, 0, value_ids)],
                    }))
        if at_lines:
            prd_tmp_vals.update({'attribute_line_ids':at_lines})
        temp_ids = prod_temp_obj.search([('woocom_id', '=', product.get('id'))])
        if temp_ids:
            temp_id = temp_ids[0]
            logger.info('product template id ===> %s', temp_id.name)
            new_lines = []
            if at_lines:
                for variant_data in at_lines:
                    p_at_ids = product_att_line_obj.search([('attribute_id', '=', variant_data[2].get('attribute_id')), ('product_tmpl_id','=', temp_id.id)])
                    if p_at_ids:
                        v_data = [v.id for v in p_at_ids[0].value_ids]
                        new_vals = []
                        for vd in variant_data[2].get('value_ids')[0][2]:
                            if vd not in v_data:
                                new_vals.append(vd)
                        if new_vals:
                            new_lines.append((1, p_at_ids[0].id, {'attribute_id': variant_data[2].get('attribute_id'), 'value_ids': [(4,new_vals)]}))
                    else:
                        variant_data[2].update({'product_tmpl_id': temp_id.id})
                        product_att_line_obj.create(variant_data[2])
                        new_lines.append((0, 0, {'attribute_id': variant_data[2].get('attribute_id'), 'value_ids': variant_data[2].get('value_ids')[0][2]}))
#                 prd_tmp_vals.pop('attribute_line_ids')
            F = prd_tmp_vals.copy()
#             F.pop('image_medium')
            prd_tmp_vals.update({'attribute_line_ids': new_lines})
            temp_id = temp_id.write(prd_tmp_vals)
        else:
            temp_ids = prod_temp_obj.create(prd_tmp_vals)
        if product.get('variations'):
            for variation in product.get('variations'):
                try:
                    url = "products/" + str(product.get('id')) +"/variations/" + str(variation)
                    vari = wcapi.get(url)
                    if not vari.status_code:
                        raise UserError(_("Enter Valid url"))
                    vari_data = vari.json()
                    op_ids = []
                    for var in vari_data.get('attributes'):
                        v_ids = att_val_obj.search([('name','=',var.get('option').lower())])
                        if v_ids:
                            op_ids.append(v_ids[0].id)
                    if op_ids:
                        product_ids = product_obj.search( 
                            [('product_tmpl_id.woocom_id', '=', product.get('id'))]) 
                        prod_id_var = False 
                        if product_ids: 
                            for product_data in product_ids: 
                                prod_val_ids = product_data.attribute_value_ids.ids 
                                prod_val_ids.sort() 
                                get_val_ids = op_ids 
                                get_val_ids.sort() 
                                if get_val_ids == prod_val_ids: 
                                    prod_id_var = product_data 
                                    break
                        if prod_id_var:
                            vari_vals={
                                'default_code' : vari_data.get('sku'),
                                'product_lngth': vari_data.get('dimensions').get('length'),
                                'product_width': vari_data.get('dimensions').get('width'),
                                'product_hght': vari_data.get('dimensions').get('height'),
                                'product_wght': vari_data.get('dimensions').get('weight'),
                                'woocom_variant_id' : vari_data.get('id'),
                                'list_price': vari_data.get('sale_price') and float(vari_data.get('sale_price')) or 0.00,
                                'woocom_regular_price': vari_data.get('regular_price') and float(vari_data.get('regular_price')) or 0.00,
                                'woocom_price' : vari_data.get('price'),
                                'description': vari_data.get('short_description'),
                            }
                            prod_id_var.write(vari_vals)
                except:
                    pass
#                 return temp_id
#     
    @api.multi
    def importWoocomProduct(self):
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            count = 1
            prod = wcapi.get("products?page="+ str(count))
            if not prod.status_code:
                raise UserError(_("Enter Valid url"))
            product_list = prod.json()
            for product in product_list:
                shop.create_woocom_product(product, wcapi)
            while len(product_list) > 0:
                count += 1
                prod = wcapi.get("products?page="+ str(count))
                product_list = prod.json()
                for product in product_list:
                    shop.create_woocom_product(product, wcapi)
        return True
    
         
    @api.one
    def create_woo_inventory(self, loc_id , qty , product):
        
        inv_wiz = self.env['stock.change.product.qty']
        if qty > 0:
            inv_wizard = inv_wiz.create({
                'location_id' : loc_id,
                'new_quantity' : qty,
                'product_id' : product.id,
                })
            inv_wizard.change_product_qty()
        return True
        
    @api.multi
    def importWoocomInventory(self):
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            products = wcapi.get("products")
            if products.status_code != 200:
                raise UserError(_("Enter Valid url"))
            
            product_list = products.json()
            
            product_vrt = {}
            for prod_dict in product_list:
                product_vrt = prod_dict.get('variations')
                if product_vrt:
                    for variant in product_vrt:
                        prod_url = 'products/' + str(prod_dict.get('id')) + "/variations/" + str(variant)
                        products_data = wcapi.get(prod_url)
                        product_dict = products_data.json()
                        if products_data.status_code != 200:
                            raise UserError(_("Enter Valid url"))
                        
                        prod_ids = self.env['product.product'].search([('woocom_variant_id', '=', variant)])
                        if prod_ids:
                            p_id = prod_ids[0]
                            logger.info('product invent id ===> %s', p_id.name)
                        else:
                            shop.create_woocom_product(product_dict, wcapi)
                            prod_ids = self.env['product.product'].search([('woocom_variant_id', '=', variant.get('id'))])
                            if prod_ids:
                                p_id = prod_ids[0]
                        if p_id:
                            self.create_woo_inventory(shop.warehouse_id.lot_stock_id.id, product_dict.get('stock_quantity'), p_id)
                else:
                    pro_ids = self.env['product.product'].search([('product_tmpl_id.woocom_id', '=', prod_dict.get('id'))])
                    if pro_ids:
                        p_id = pro_ids[0]
                    else:
                        product_url = 'products/' + str(prod_dict.get('id'))
                        products_data = wcapi.get(product_url)
                        if products_data.status_code != 200:
                            raise UserError(_("Enter Valid url"))
    
                        product_dict = products_data.json()
                        shop.create_woocom_product(product_dict.get('product'), wcapi)
                        pro_ids = self.env['product.product'].search([('product_tmpl_id.woocom_id', '=', prod_dict.get('id'))])
                        if pro_ids:
                            p_id = pro_ids[0]
                    if p_id:
                        self.create_woo_inventory(shop.warehouse_id.lot_stock_id.id, prod_dict.get('stock_quantity'), p_id)
        return True
    
    @api.one
    def create_woo_customer(self, customer_detail, wcapi):
        res_partner_obj = self.env['res.partner']
        country_obj = self.env['res.country']
        state_obj = self.env['res.country.state']
        
        country_ids  = False
        bcountry = customer_detail.get('billing').get('country')
        if bcountry != 'False':
            country_ids = country_obj.search([('code', '=', bcountry)])
            if not country_ids:
                country_id = country_obj.create({'name':bcountry, 'code':bcountry}).id
            else:
                country_id = country_ids[0].id
                logger.info('country id ===> %s', country_id)
        else:
            country_id = False
            
        bstate = customer_detail.get('billing').get('state')
        if bstate != 'False':
            state_ids = state_obj.search([('code', '=', bstate)])
            if not state_ids:
                state_id = state_obj.create({'name':bstate, 'code':bstate, 'country_id': country_id}).id
            else:
                state_id = state_ids[0].id
                logger.info('state id ===> %s', state_id)
        else:
            state_id = False
#         if customer_detail.get('first_name') or customer_detail.get('last_name'):
        vals = {
            'woocom_id': customer_detail.get('id'),
            'name': (customer_detail.get('first_name') or '' + customer_detail.get('last_name') or '') or customer_detail.get('username'),
            'customer' : True,
            'supplier' : False,
            'street': customer_detail.get('billing') and customer_detail.get('billing').get('address_1') or '',
            'street2' : customer_detail.get('billing').get('address_2'),
            'city': customer_detail.get('billing').get('city'),
            'zip': customer_detail.get('billing').get('postcode'),
            'phone': customer_detail.get('billing').get('phone'),
            'state_id' :state_id,
            'country_id': country_id,
            'email': customer_detail.get('email'),
            'website': customer_detail.get('website'),
            }
        
        ####
        add_lines = []  
        
        scountry = customer_detail.get('shipping').get('country')
        if scountry != 'False':
            scountry_ids = country_obj.search([('code', '=', scountry)])
            if not scountry_ids:
                scountry_id = country_obj.create({'name':scountry, 'code':scountry}).id
            else:
                scountry_id = scountry_ids[0].id
                logger.info('scountry id ===> %s', scountry_id)
        else:
            scountry_id = False
            
        sstate = customer_detail.get('shipping').get('state')
        if sstate != 'False':
            sstate_ids = state_obj.search([('code', '=', sstate)])
            if not sstate_ids:
                sstate_id = state_obj.create({'name':sstate, 'code':sstate, 'country_id': scountry_id}).id
            else:
                sstate_id = sstate_ids[0].id
                logger.info('sstate id ===> %s', sstate_id)
        else:
            sstate_id = False
        
        if customer_detail.get('shipping').get('city'):
            add_lines.append((0, 0, {
                'woocom_id': customer_detail.get('id'),
                'name': customer_detail.get('shipping').get('first_name') or ' ' + customer_detail.get('shipping').get('last_name') or ' ',
                'street': customer_detail.get('shipping').get('address_1'),
                'street2' : customer_detail.get('shipping').get('address_2'),
                'city': customer_detail.get('shipping').get('city'),
                'zip': customer_detail.get('shipping').get('postcode'),
                'phone': customer_detail.get('shipping').get('phone'),
                'country_id' : scountry_id,
                'state_id' : sstate_id,
                'type': 'delivery',
                }))
        vals.update({'child_ids' : add_lines})
        customer_ids = res_partner_obj.search([('woocom_id', '=', customer_detail.get('id')),('email','=',customer_detail.get('email'))])
        if not customer_ids:
            cust_id = res_partner_obj.create(vals)
        else:
            cust_id = customer_ids[0]
            logger.info('customer id ===> %s', cust_id.name)
            vals.pop('child_ids')
            cust_id.write(vals)
        if cust_id:
            self.env.cr.execute("select cust_id from customer_shop_rel where cust_id = %s and shop_id = %s" % (cust_id.id, self.id))
            cust_data = self.env.cr.fetchone()
        return cust_id


    
    @api.multi
    def importWoocomCustomer(self):
        
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            count = 1
            customers = wcapi.get("customers?page="+ str(count))
            if customers.status_code != 200:
                raise UserError(_("Enter Valid url"))
            customer_list = customers.json()
            for custm in customer_list:
                shop.create_woo_customer(custm, wcapi)
            while len(customer_list) > 0:
                count += 1
                custm = wcapi.get("customers?page="+ str(count))
                customer_list = custm.json()
                for custm in customer_list:
                    shop.create_woo_customer(custm, wcapi)
        return True
    
    @api.one
    def create_woo_carrier(self, carrier, wcapi):
        carrier_obj = self.env['delivery.carrier']
        partner_obj = self.env['res.partner']
        product_obj = self.env['product.product']
        partner_ids = partner_obj.search([('name', '=', carrier.get('title'))])
        if partner_ids:
            partner_id = partner_ids[0]
        else:
            partner_id = partner_obj.create({'name': carrier.get('title')})
        prod_ids = product_obj.search([('name', '=', carrier.get('title'))])
        if prod_ids:
            prod_ids = prod_ids[0]
        else:
            prod_ids = product_obj.create({'name': carrier.get('title')})
        carr_vals = {
            'name': carrier.get('title'),
            'partner_id': partner_id.id,
            'woocom_id': carrier.get('id'),
            'product_id': prod_ids.id
        }
        car_ids = carrier_obj.search([('woocom_id', '=',carrier.get('id'))])
        if not car_ids:
            carrier_id = carrier_obj.create(carr_vals)
        else:
            carrier_id = car_ids[0]
            logger.info('carrier id ===> %s', carrier_id.name)
            carrier_id.write(carr_vals)
        return carrier_id
    
    @api.multi
    def importWoocomCarrier(self):
        
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            carriers = wcapi.get("shipping_methods")
            if carriers.status_code != 200:
                raise UserError(_("Enter Valid url"))
            carriers_list = carriers.json()
            for carrier in carriers_list:
                shop.create_woo_carrier(carrier, wcapi)
        return True
    
    @api.one
    def create_woo_payment_method(self, payment, wcapi):
        payment_obj = self.env['payment.gatway']
        pay_ids = payment_obj.search([('woocom_id', '=',payment.get('id'))])
        pay_vals = {
            'title': payment.get('title'),
            'woocom_id': payment.get('id'),
            'descrp': payment.get('description'),
            }
        pay_ids.write(pay_vals)
        if not pay_ids:
            payment_id = payment_obj.create(pay_vals)
            payment_id.write(pay_vals)
        
        
    
    @api.multi
    def importWooPaymentMethod(self):
        
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            payment_methods = wcapi.get("payment_gateways")
            if payment_methods.status_code != 200:
                raise UserError(_("Enter Valid url"))
            payments_list = payment_methods.json()
            for payment in payments_list:
                shop.create_woo_payment_method(payment, wcapi)
        return True
    
    def woocomManageOrderWorkflow(self, saleorderid, order_detail, status):
        invoice_obj = self.env['account.invoice']
        invoice_refund_obj = self.env['account.invoice.refund']
        return_obj = self.env['stock.return.picking']
        return_line_obj = self.env['stock.return.picking.line']
        
        if order_detail.get('status') == 'cancelled':
            if saleorderid.state in ['draft']:
                saleorderid.action_cancel()

            if saleorderid.state in ['progress', 'done', 'manual']:
                invoice_ids = saleorderid.invoice_ids
                for invoice in invoice_ids:
                    refund_ids = invoice_obj.search([('origin', '=', invoice.number)])
                    # print  "==refund_ids==>",refund_ids
                    if not refund_ids:
                        if invoice.state == 'paid':
                            refund_invoice_id = invoice_refund_obj.create(dict(
                                description='Refund To %s' % (invoice.partner_id.name),
                                date=datetime.date.today(),
                                filter_refund='refund'
                            ))
                            refund_invoice_id.invoice_refund()
                            saleorderid.write({'is_refund': True})
                        else:
                            invoice.action_cancel()

                for picking in saleorderid.picking_ids:
                    if picking.state not in ('done'):
                        picking.action_cancel()
                    else:
                        ctx = self._context.copy()
                        ctx.update({'active_id': picking.id})
                        res = return_obj.with_context(ctx).default_get(['product_return_moves', 'move_dest_exists'])
                        res.update({'invoice_state': '2binvoiced'})
                        return_id = return_obj.with_context(ctx).create({'invoice_state': 'none'})
                        for record in res['product_return_moves']:
                            record.update({'wizard_id': return_id.id})
                            return_line_obj.with_context(ctx).create(record)

                        pick_id_return, type = return_id.with_context(ctx)._create_returns()
                        pick_id_return.force_assign()
                        pick_id_return.action_done()
            saleorderid.action_cancel()
            return True
            
        if order_detail.get('status') == 'refunded':
            if saleorderid.state in ['draft']:
                saleorderid.action_cancel()

                if saleorderid.state in ['progress', 'done', 'manual']:
                    invoice_ids = saleorderid.invoice_ids
                    for invoice in invoice_ids:
                        refund_ids = invoice_obj.search([('origin', '=', invoice.number)])
                    if not refund_ids:
                        if invoice.state == 'paid':
                            refund_invoice_id = invoice_refund_obj.create(dict(
                                description='Refund To %s' % (invoice.partner_id.name),
                                date=datetime.date.today(),
                                filter_refund='refund'
                            ))
                            refund_invoice_id.invoice_refund()
                            saleorderid.write({'is_refund': True})
                        else:
                            invoice.action_cancel()
            return True
        
        if self.workflow_id:
            if self.workflow_id.validate_order:
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()

        # if complete shipment is activated in workflow
            if self.workflow_id.complete_shipment:
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()
                for picking_id in saleorderid.picking_ids:
    
                    # If still in draft => confirm and assign
                    if picking_id.state == 'draft':
                        picking_id.action_confirm()
                        picking_id.action_assign()
    
                    if picking_id.state == 'confirmed':
                        picking_id.force_assign()
                    picking_id.do_transfer()
    
            # if create_invoice is activated in workflow
            if self.workflow_id.create_invoice:
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()
                if not saleorderid.invoice_ids:
                    invoice_ids = saleorderid.action_invoice_create()
                    invoice_ids = invoice_obj.browse(invoice_ids)
                    invoice_ids.write({'is_woocom': True})
    
    
            # if validate_invoice is activated in workflow
            if self.workflow_id.validate_invoice:
                if saleorderid.state == 'draft':
                    saleorderid.action_confirm()
    
                if not saleorderid.invoice_ids:
                    invoice_ids = saleorderid.action_invoice_create()
                    invoice_ids = invoice_obj.browse(invoice_ids)
                    invoice_ids.write({'is_woocom': True})
    
                for invoice_id in saleorderid.invoice_ids:
                    if invoice_id.state == 'draft':
                        invoice_id.action_invoice_open()
    
            # if register_payment is activated in workflow
            if self.workflow_id.register_payment:
                if saleorderid.state == 'draft':
                    saleorderid.action_confirm()
                if not saleorderid.invoice_ids:
                    invoice_ids = saleorderid.action_invoice_create()
                    invoice_ids = invoice_obj.browse(invoice_ids)
                    invoice_ids.write({'is_woocom': True})
    
                for invoice_id in saleorderid.invoice_ids:
                    if invoice_id.state == 'draft':
                        # print "invoice state is draft"
                        invoice_id.action_invoice_open()
                    if invoice_id.state not in ['paid'] and invoice_id.invoice_line_ids:
                        invoice_id.pay_and_reconcile(
                            self.workflow_id and self.sale_journal or self.env['account.journal'].search(
                                [('type', '=', 'bank')], limit=1), invoice_id.amount_total)
            return True
                
        else:
            if order_detail.get('status') == 'on-hold':
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()

                for picking_id in saleorderid.picking_ids:
# If still in draft => confirm and assign
                    if picking_id.state == 'draft':
                        picking_id.action_confirm()
                        picking_id.action_assign()
    
                    if picking_id.state == 'confirmed':
                        picking_id.force_assign()
                    picking_id.do_transfer()
                if not saleorderid.invoice_ids:
                    invoice_ids = saleorderid.action_invoice_create()
                    
                        
            elif order_detail.get('status') == 'failed':
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()

                for picking_id in saleorderid.picking_ids:
# If still in draft => confirm and assign
                    if picking_id.state == 'draft':
                        picking_id.action_confirm()
                        picking_id.action_assign()
    
                    if picking_id.state == 'confirmed':
                        picking_id.force_assign()
                    picking_id.do_transfer()
                                            
            elif order_detail.get('status') == 'processing': 
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()
               
                if not saleorderid.invoice_ids:
                    invoice_ids = saleorderid.action_invoice_create()
    
                for invoice_id in saleorderid.invoice_ids:
                    if invoice_id.state == 'draft':
                        invoice_id.action_invoice_open()
                    if invoice_id.state not in ['paid'] and invoice_id.invoice_line_ids:
                            invoice_id.pay_and_reconcile(
                                self.sale_journal or self.env['account.journal'].search(
                                    [('type', '=', 'bank')], limit=1), invoice_id.amount_total)
        
            elif order_detail.get('status') == 'pending':
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()
               
                if not saleorderid.invoice_ids:
                    invoice_ids = saleorderid.action_invoice_create()
                
                        
            elif order_detail.get('status') == 'completed':
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()

                for picking_id in saleorderid.picking_ids:
                    if picking_id.state == 'draft':
                        picking_id.action_confirm()
                        picking_id.action_assign()
    
                    if picking_id.state == 'confirmed':
                        picking_id.force_assign()
                    picking_id.do_transfer()
                    
                if not saleorderid.invoice_ids:
                    invoice_ids = saleorderid.action_invoice_create()
    
                for invoice_id in saleorderid.invoice_ids:
                    if invoice_id.state == 'draft':
                        invoice_id.action_invoice_open()
                    if invoice_id.state not in ['paid'] and invoice_id.invoice_line_ids:
                            invoice_id.pay_and_reconcile(
                                self.sale_journal or self.env['account.journal'].search(
                                    [('type', '=', 'bank')], limit=1), invoice_id.amount_total)
                
                saleorderid.action_done()
                
           
    @api.one
    def woocomManageOrderLines(self, orderid, order_detail, wcapi):
        sale_order_line_obj = self.env['sale.order.line']
        prod_attr_val_obj = self.env['product.attribute.value']
        prod_templ_obj = self.env['product.template']
        product_obj = self.env['product.product']
        lines = []
        for child in order_detail:
            p_id = False
            p_ids = product_obj.search([('default_code', '=', child.get('sku'))])
            if p_ids:
                p_id = p_ids[0]
                logger.info('order line product id ===> %s', p_id.name)
            else:
                self.importWoocomProduct()
                p_ids = product_obj.search([('default_code', '=', child.get('sku'))])
                if p_ids:
                    p_id = p_ids[0]
            if not p_id:
                p_id = product_obj.create({'default_code': child.get('sku'), 'name': child.get('name') or child.get('sku')})
#                 'name': child.get('sku'),
#             if child.get('name') or child.get('sku')
            
            line = {
                'product_id' : p_id and p_id.id,
                'price_unit': float(child.get('price')),
                'name': child.get('name') or child.get('sku'),
                'product_uom_qty': float(child.get('quantity')),
                'order_id': orderid.id,
                'tax_id': False,
                'woocom_id': child.get('id'),
                'product_uom': p_id and p_id.uom_id.id 
            }
            line_ids = sale_order_line_obj.search([('order_id', '=', orderid.id), ('woocom_id', '=', child.get('id'))])
            if line_ids:
                line_id = line_ids[0]
                logger.info('order line id ===> %s', line_id.name)
                line_id.write(line)
            else:
                line_id = sale_order_line_obj.create(line)
        return True
          
    @api.one
    def create_woo_order(self, order_detail, wcapi):
        sale_order_obj = self.env['sale.order']
        res_partner_obj = self.env['res.partner']
        carrier_obj = self.env['delivery.carrier']
        status_obj = self.env['woocom.order.status']
        payment_obj = self.env['payment.gatway']
        woocom_conector = self.env['woocommerce.connector.wizard']
        
        if not order_detail.get('line_items'):
            return False
        custm_id = order_detail.get('customer_id')
        if not custm_id:
            partner_id = self[0].partner_id.id
        else:
            part_ids = res_partner_obj.search([('woocom_id', '=', custm_id)])
            if part_ids:
                partner_id = part_ids[0].id
                logger.info('partner id ===> %s', partner_id)
            else:
                url = 'customers/' + str(custm_id)
                customer_data = wcapi.get(url)
                customer_data = customer_data.json()
                partner_id = self.create_woo_customer(customer_data.get('customer'), wcapi)[0].id
            paym_ids = payment_obj.search([('woocom_id','=',order_detail.get('payment_method'))])
            if paym_ids:
                pay_id = paym_ids[0].id
                logger.info('payment id ===> %s', pay_id)
            else:
                pay_id = payment_obj.search([('woocom_id','=',order_detail.get('payment_method'))])
                pay_id = pay_id.id
            car_id = False
            for avalue in order_detail.get('shipping_lines'):
                if avalue.get('method_id') == 'False':
                    car_id = False
                else:
                    car_ids = carrier_obj.search([('woocom_id','=',avalue.get('method_id'))])
                    if car_ids:
                        car_id = car_ids[0].id
                        logger.info('carrier id ===> %s', car_id)
                    else:
                        self.importWoocomCarrier()
    #                     car_url = 'shipping_methods'+str(avalue.get('method_id'))
                        car_id = carrier_obj.search({'woocom_id','=', avalue.get('method_id')})
                        carr_data = wcapi.get(car_url)
                        carrier_data = carr_data.json()
                        carrier_id = self.create_woo_carrier(carrier_data.get('customer'), wcapi)[0].id
#                     car_ids = carrier_obj.search([('woocom_id','=',avalue.get('method_id'))])
#                     if car_ids:
#                         car_id = car_ids[0].id
#                         logger.info('carrier id ===> %s', car_id)
#                     else:
#                         car_id = False
            
            order_vals = {'partner_id': partner_id,
                          'woocom_id' : order_detail.get('id'),
                          'warehouse_id': self.warehouse_id.id,
                          'name': (self.prefix and self.prefix or '') + str(order_detail.get('id')) + (self.suffix and self.suffix or ''),
                          'pricelist_id': self.pricelist_id.id,
                          'order_status' : order_detail.get('status'),
                          'shop_id': self.id,
                          'carrier_woocommerce': car_id or False,
                          'woocom_payment_mode':pay_id
            }
            sale_order_ids = sale_order_obj.search([('woocom_id', '=', order_detail.get('id'))])
            if not sale_order_ids:
                s_id = sale_order_obj.create(order_vals)
            else:
                s_id = sale_order_ids[0]
                logger.info('create order ===> %s', s_id.name)
                s_id.write(order_vals)
            self.woocomManageOrderLines(s_id, order_detail.get('line_items'), wcapi)
            self.woocomManageOrderWorkflow(s_id, order_detail, order_detail.get('status'))
        
    @api.multi
    def importWoocomOrder(self):
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            count = 1
            if self.env.context.get('last_woocommerce_order_import_date'):
                method = "orders?filter[created_at_min]="+ self.env.context.get('last_woocommerce_order_import_date')
            elif shop.last_woocommerce_order_import_date:
                today = date.today()- timedelta(days=2)
                method = "orders?filter[created_at_min]="+ str(today)
            else:
                method = 'orders?page='+ str(count)
            orders = wcapi.get(method)
            if orders.status_code != 200:
                raise UserError(_("Enter Valid url"))
            orders_list = orders.json()
            for order in orders_list:
                shop.create_woo_order(order, wcapi)
            while len(orders_list) > 0:
                count += 1
                order = wcapi.get("orders?page="+ str(count))
                orders_list = order.json()
                for order in orders_list:
                    shop.create_woo_order(order, wcapi)
        return True
    
    @api.multi
    def updateWoocomCategory(self):
        categ_obj = self.env['woocom.category']
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            if shop.woocommerce_last_update_category_date:
                categ_ids = categ_obj.search([('write_date','>', shop.woocommerce_last_update_category_date),('woocom_id','!=',False)])
            else:
                categ_ids = categ_obj.search([('woocom_id','!=',False)])
            for each in categ_ids:
                cat_vals= ({
                            'id': each.woocom_id,
                            'name': each.name,
                            'parent': each.parent_id and str(each.parent_id.woocom_id) or '0',
                })
                categ_url = 'products/categories/' + str(each.woocom_id)
                cat_vals = wcapi.post(categ_url, cat_vals)
                
                    
    @api.multi
    def updateWoocomProduct(self):
        #update product details,image and variants
        prod_templ_obj = self.env['product.template']
        prdct_obj = self.env['product.product']
        stock_quant_obj = self.env['stock.quant']
        inventry_line_obj = self.env['stock.inventory.line']
        prod_att_obj = self.env['product.attribute']
        prod_attr_vals_obj = self.env['product.attribute.value']
        inventry_line_obj = self.env['stock.inventory.line']
        inventry_obj = self.env['stock.inventory']
        stock_quanty = self.env['stock.quant']

        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            if shop.woocommerce_last_update_product_data_date:
                product_data_ids = prod_templ_obj.search([('write_date', '>',shop.woocommerce_last_update_product_data_date),('woocom_id', '!=', False)])
            else:
                product_data_ids = prod_templ_obj.search([('woocom_id', '!=', False)])
#             product_data_ids = prod_templ_obj.browse([55])
            for each in product_data_ids:
                categs = [{
                    "id": each.woo_categ.woocom_id,
                }]
                parent_id = each.woo_categ.parent_id
                while parent_id:
                    categs.append({
                         "id": parent_id.woocom_id,
                    })
                    parent_id = parent_id.parent_id
                image_list = []
                count = 1
                for image_data in each.woocom_product_img_ids:
                    if image_data.woocom_img_id:
                        image_list.append({
                            'id':image_data.woocom_img_id,
                            'src':image_data.url,
                            'position': count  
                            })
                    else:
                        image_list.append({
                            'src':image_data.url,
                            'position': count  
                        })
                    count +=1
                prod_vals = {
                'name' : each.name,
                'sku': str(each.default_code),
                "regular_price": each.woocom_regular_price and str(each.woocom_regular_price) or '0.00',
                'sale_price': each.woocom_price and str(each.woocom_price) or '0.00',#str(each.with_context(pricelist=shop.pricelist_id.id).price),
                'dimensions':{
                                'width': str(each.product_width),
                                'height': str(each.product_hght),
                                'length': str(each.product_lngth),
                                'weight': str(each.product_wght),
                                },
                'description' : each.description_sale and str(each.description_sale) or '',
                'short_description': each.description_sale and str(each.description_sale) or '',
#                 'images':image_list,
                'categories':categs,
                'id': int(each.woocom_id),
                }
                
                if each.attribute_line_ids:
                    p_ids = prdct_obj.search([('product_tmpl_id', '=' ,each.id)])
                    qaunt = 0
                    if p_ids:
                        stck_quant_id = stock_quanty.search([('product_id','in',p_ids.ids),('location_id','=',shop.warehouse_id.lot_stock_id.id)])
                        for stock in stck_quant_id:
                            qaunt += stock.quantity
                    prod_vals.update({
                        'type': 'variable',
                        'stock_quantity': int(qaunt),
                    }) 
                else:
                    p_ids = prdct_obj.search([('product_tmpl_id', '=' ,each.id)])
                    qaunt = 0
                    if p_ids:
                        stck_quant_id = stock_quanty.search([('product_id','=',p_ids[0].id),('location_id','=',shop.warehouse_id.lot_stock_id.id)])
                        for stock in stck_quant_id:
                            qaunt += stock.quantity
                    prod_vals.update({
                        'type': 'simple',
                        'stock_quantity': int(qaunt),
                    }) 
                if prod_vals.get('type') == 'simple':
                    prod_url = 'products/' + str(each.woocom_id)
                    prd_response = wcapi.post(prod_url, prod_vals)
                attributes = []
                if each.attribute_line_ids:
                    attributes = []
                    for attr in each.attribute_line_ids:
                        values = []
                        for attr_value in attr.value_ids:
                            values.append(attr_value.name)
                        attributes.append({
                            'id': int(attr.attribute_id.woocom_id),
                            'name': attr.attribute_id.name,
                            'options': values,
                            'variation': 'true',
                            'visible': 'false'
                        })
                    if attributes:
                        prod_vals.update({'attributes': attributes})
                        prod_url = 'products/' + str(each.woocom_id)
                        prod_export_res = wcapi.post(prod_url, prod_vals)
                
                prod_var_id = prdct_obj.search([('product_tmpl_id', '=', each.id)])

                for var in prod_var_id:
                    if not var.attribute_value_ids:
                        continue
                    values = []
                    for att in var.attribute_value_ids:
                        values.append({
                            'id': att.attribute_id.woocom_id,
                            'option': att.name,
                        })
                    var_vals = {
                        'name' : var.name,
    #                     'sale_price': str(var.with_context(pricelist=shop.pricelist_id.id).price),
                        'regular_price': var.woocom_regular_price and str(var.woocom_regular_price) or '0.00',
                        'sale_price': var.woocom_price and str(var.woocom_price) or '0.00',
                        'dimensions':{
                                    'width': str(var.product_width),
                                    'height': str(var.product_hght),
                                    'length': str(var.product_lngth),
                                    'weight': str(var.product_wght),
                                    },
                        'attributes': values,
                        }
                    if var.woocom_variant_id:
                        var_url = 'products/' + str(each.woocom_id) + '/variations/' + str(var.woocom_variant_id)
                    else:
                        var_url = 'products/' + str(each.woocom_id) + '/variations'
                    prd_response = wcapi.post(var_url, var_vals).json()
                    var.write({'woocom_variant_id': prd_response.get('id')  })
        return True           
            
            
    @api.multi
    def updateWoocomInventory(self):
        prod_templ_obj = self.env['product.template']
        prdct_obj = self.env['product.product']
        inv_wiz = self.env['stock.change.product.qty']
        stck_quant = self.env['stock.quant']
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            if self.env.context.get('product_ids'):
                p_ids = prod_templ_obj.browse(self.env.context.get('product_ids'))
            elif shop.woocommerce_last_update_inventory_date:
                p_ids = prod_templ_obj.search([('write_date','>', shop.woocommerce_last_update_inventory_date)])
            else:
                p_ids = prod_templ_obj.search([('woocom_id','!=',False)])
            for temp in p_ids:
                if temp.attribute_line_ids:
                    prod_var_id = prdct_obj.search([('product_tmpl_id', '=', temp.id)])
                    for var_id in prod_var_id:
                        stck_id = stck_quant.search([('product_id','=',var_id.id),('location_id','=',shop.warehouse_id.lot_stock_id.id)])
                        qty = 0
                        for stck in stck_id:
                            qty += stck.quantity
                        pro_vals = {
                            'stock_quantity' : int(qty),
                            'manage_stock' : 'true'
                        }
                        if qty > 0:
                            pro_vals.update({'in_stock': True})
                        else:
                            pro_vals.update({'in_stock': False})
                        url = "products/" + str(temp.woocom_id) +"/variations/" + str(var_id.woocom_variant_id)
                        pro_res = wcapi.post(url, pro_vals).json()
                else:
                    product_ids = prdct_obj.search([('product_tmpl_id', '=', temp.id)])
                    if product_ids:
                        stck_id = stck_quant.search([('product_id','=',product_ids[0].id),('location_id','=',shop.warehouse_id.lot_stock_id.id)])
                        qty = 0
                        for stck in stck_id:
                            qty += stck.quantity
                        pro_vals = {
                            'stock_quantity' : int(qty),
                            'manage_stock' : 'true'
                        }
                        if qty > 0:
                            pro_vals.update({'in_stock': True})
                        else:
                            pro_vals.update({'in_stock': False})
                        pro_url = 'products/' + str(temp.woocom_id)
                        pro_res = wcapi.post(pro_url, pro_vals).json()
            shop.write({'woocommerce_last_update_inventory_date': datetime.now()})
                
    @api.multi
    def updateWoocomOrderStatus(self):
        sale_order_obj = self.env['sale.order']
        status_obj = self.env['woocom.order.status']
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            sale_order_ids = sale_order_obj.search([('woocom_id', '!=', False), ('order_status','in',['pending','processing','on-hold'])])
            for sale_order in sale_order_ids:
                ordr_url = 'orders/' + str(sale_order.woocom_id)
                order_vals = {
                     'status' : 'completed',
                }
                ord_res = wcapi.post(ordr_url, order_vals).json()
                if ord_res:
                    sale_order.write({'order_status': 'completed'})
                    
                
    @api.multi
    def expotWoocomOrder(self):
        sale_order_obj = self.env['sale.order']
        res_partner_obj = self.env['res.partner']
        carrier_obj = self.env['delivery.carrier']
#         status_obj = self.env['presta.order.status']
        sale_order_line_obj = self.env['sale.order.line']
        prod_attr_val_obj = self.env['product.attribute.value']
        prod_templ_obj = self.env['product.template']
        product_obj = self.env['product.product']
        invoice_obj = self.env['account.invoice']
        invoice_refund_obj = self.env['account.invoice.refund']
        return_obj = self.env['stock.return.picking']
        return_line_obj = self.env['stock.return.picking.line']

        prod_templ_obj = self.env['product.template']
        prdct_obj = self.env['product.product']
        categ_obj = self.env['product.category']
         
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            if self.env.context.get('export_product_ids'):
                order_ids = sale_order_obj.browse(self.env.context.get('export_product_ids'))
            else:
                order_ids = sale_order_obj.search([('to_be_exported', '=', True)])
            for order in order_ids:
                order_name = order.partner_id.name
                name_list = order_name.split(' ')
                first_name = name_list[0]
                if len(name_list) > 1:
                    last_name = name_list[1]
                else:
                    last_name = name_list[0]
                data = {
                    'customer_id' : int(order.partner_id.woocom_id),
                    'payment_method' :str(order.woocom_payment_mode),
                    'status' : str(order.order_status),
                    "billing": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "address_1": order.partner_id.street,
                        "address_2":order.partner_id.street2,
                        "city": order.partner_id.city,
                        "state": str(order.partner_id.state_id.code),
                        "postcode": str(order.partner_id.zip),
                        "country":  str(order.partner_id.country_id.code),
                        "email": str(order.partner_id.email),
                        "phone": str(order.partner_id.phone)
                    },
                    
                    "shipping": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "address_1": order.partner_id.street,
                        "address_2":order.partner_id.street2,
                        "city": order.partner_id.city,
                        "state": str(order.partner_id.state_id.code),
                        "postcode":str(order.partner_id.zip),
                        "country":  str(order.partner_id.country_id.code)
                    },
                    "total" : str(order.amount_total),
                    "line_items": [
                    ],
                    "shipping_lines": [
                        {
                            'method_id': str(order.carrier_id.woocom_id),
                            'method_title': str(order.carrier_id.name),
                            }
                    ]
                }
                if order.order_line:
                    line_items = []
                    for line in order.order_line:
                        product = False
                        if line.product_id and line.product_id.attribute_value_ids:
                            product = line.product_id.woocom_variant_id
                        else:
                            product = line.product_id.product_tmpl_id.woocom_id
                        line_items.append({
                            "product_id":  product,
                            "name" : line.name,
                            "quantity": str(line.product_uom_qty),
                            "price" : str(line.price_unit),
                            "shipping_total": str(line.price_unit),
                            
                        })
                    data.update({
                        'line_items': line_items
                    })
                ordr_export_res = wcapi.post("orders",data).json()
                if ordr_export_res:
                    order.write({'woocom_id': ordr_export_res.get('id'), 'to_be_exported': False})
                
                            
    @api.multi
    def exportWoocomCategories(self):
        categ_obj = self.env['woocom.category']
        
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            if self.env.context.get('export_product_ids'):
               
                category_ids = categ_obj.browse(self.env.context.get('export_product_ids'))
            else:
                category_ids = categ_obj.search([('to_be_exported','=',True)])
            for categ in category_ids:
                data = {
                        "name":categ.name,
                        'slug':categ.name.replace(' ','_'),
                        "parent": categ.parent_id.woocom_id and int(categ.parent_id.woocom_id) or 0,
                    }
                res = wcapi.post("products/categories", data)
                res = res.json()
                if res:
                    categ.write({'woocom_id': res.get('id'), 'to_be_exported': False})
            
    @api.multi
    def exportWoocomCustomers(self):
        res_partner_obj = self.env['res.partner']
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            if self.env.context.get('export_product_ids'):
                customer_ids = res_partner_obj.browse(self.env.context.get('export_product_ids'))
            else:
                customer_ids = res_partner_obj.search([('to_be_exported', '=', True)])
            for customer in customer_ids:
                customer_name = customer.name
                name_list = customer_name.split(' ')
                first_name = name_list[0]
                if len(name_list) > 1:
                    last_name = name_list[1]
                else:
                    last_name = name_list[0]
                custom_data = {
                        "email": str(customer.email),
                        "first_name": first_name,
                        "last_name": last_name,
                        "password" : str(customer.email) ,
                        "billing": {
                            "first_name": first_name,
                            "last_name": last_name,
                            "company": str(customer.parent_id.name),
                            "address_1": customer.street  or '',
                            "address_2": customer.street2  or '',
                            "city": customer.city or '',
                            "state": str(customer.state_id.code),
                            "postcode": str(customer.zip) or '',
                            "country": str(customer.country_id.code),
                            "email": str(customer.email),
                            "phone": str(customer.phone),
                        },
                        "shipping": {
                            "first_name":first_name,
                            "last_name": last_name,
                            "company": str(customer.parent_id.name),
                            "address_1": customer.street  or '',
                            "address_2": customer.street2  or '',
                            "city": customer.city or '',
                            "state": str(customer.state_id.code),
                            "postcode": str(customer.zip) or '',
                            "country": str(customer.country_id.code)
                        }
                    }
                cust_export_res = wcapi.post("customers", custom_data).json()
                if cust_export_res:
                    customer.write({'woocom_id': cust_export_res.get('id'), 'to_be_exported': False})
                
    @api.multi
    def exportWoocomProduct(self):
        prod_templ_obj = self.env['product.template']
        prdct_obj = self.env['product.product']
        stock_quanty = self.env['stock.quant']
        for shop in self:
            wcapi = API(url=shop.woocommerce_instance_id.location, consumer_key=shop.woocommerce_instance_id.consumer_key, consumer_secret=shop.woocommerce_instance_id.secret_key,wp_api=True, version='wc/v2')
            if self.env.context.get('export_product_ids'):
                product_ids = prod_templ_obj.browse(self.env.context.get('export_product_ids'))
            else:
                product_ids = prod_templ_obj.search([('product_to_be_exported', '=', True)])
            for product in product_ids:
                categs = [{
                    "id": product.woo_categ.woocom_id,
                }]
                parent_id = product.woo_categ.parent_id
                while parent_id:
                    categs.append({
                         "id": parent_id.woocom_id,
                    })
                    parent_id = parent_id.parent_id
                images = []
                count = 0
                for image_data in product.woocom_product_img_ids:
                    images.append({
                        'src':image_data.url,
                        'position': count  
                        })
                    count +=1
                prod_vals = {
                    "name" :product.name,
                    "slug": product.name.replace(' ','_'),
                    "sku": str(product.default_code),
                    "manage_stock": 'true',
                    "in_stock": 'true',
#                     "stock_quantity": product.qty_available ,
                    "dimensions": {
                                        "length": str(product.product_lngth),
                                        "width": str(product.product_width),
                                        "height": str(product.product_hght),
                                        "weight": str(product.product_wght),
                                      },
                    "regular_price": product.woocom_regular_price and str(product.woocom_regular_price) or '0.00',
                    "sale_price": product.woocom_price and str(product.woocom_price) or '0.00',
                    "images":images,
                    "categories": categs,
                    'description' : str(product.description_sale),
                    'in_stock': 'true',
                    'manage_stock': 'true'
                }
                if product.attribute_line_ids:
                    p_ids = prdct_obj.search([('product_tmpl_id', '=' ,product[0].id)])
                    qaunt = 0
                    if p_ids:
                        stck_quant_id = stock_quanty.search([('product_id','in',p_ids.ids),('location_id','=',shop.warehouse_id.lot_stock_id.id)])
                        for stock in stck_quant_id:
                            qaunt += stock.quantity
                    prod_vals.update({
                        'type': 'variable',
                        'stock_quantity': int(qaunt),
                    }) 
                else:
                    p_ids = prdct_obj.search([('product_tmpl_id', '=' ,product[0].id)])
                    qaunt = 0
                    if p_ids:
                        stck_quant_id = stock_quanty.search([('product_id','=',p_ids[0].id),('location_id','=',shop.warehouse_id.lot_stock_id.id)])
                        for stock in stck_quant_id:
                            qaunt += stock.quantity
                    prod_vals.update({
                        'type': 'simple',
                        'stock_quantity': int(qaunt),
                    }) 
                if prod_vals.get('type') == 'simple':
                    prod_export_res = wcapi.post("products", prod_vals).json()
                    if prod_export_res:    
                        product.write({'woocom_id': prod_export_res.get('id'),'product_to_be_exported': False})
                attributes = []
                if product.attribute_line_ids:
                    attributes = []
                    for attr in product.attribute_line_ids:
                        values = []
                        for attr_value in attr.value_ids:
                            values.append(attr_value.name)
                        attributes.append({
                            'name': attr.attribute_id.name,
                            'options': values,
                            'variation': True,
                            'visible': False
                        })
                    if attributes:
                        prod_vals.update({'attributes': attributes})
                        prod_export_res = wcapi.post("products", prod_vals).json()
                        if prod_export_res:    
                            product.write({'woocom_id': prod_export_res.get('id'),'product_to_be_exported': False})
                     
                        prod_var_id = prdct_obj.search([('product_tmpl_id', '=', product.id)])
                        for variant in prod_var_id:
                            stck_id = stock_quanty.search([('product_id','=',variant.id),('location_id','=',shop.warehouse_id.lot_stock_id.id)])
                            qty = 0
                            for stck in stck_id:
                                qty += stck.quantity
                            variation_vals = {
                                'sku': str(variant.default_code),
                                'stock_quantity': int(qty),
                                'in_stock': 'true',
                                'manage_stock': 'true',
                                "sale_price": variant.woocom_price and str(variant.woocom_price) or '0.00',
                                'regular_price': variant.woocom_regular_price and str(variant.woocom_regular_price) or '0.00',
                                'weight' : str(variant.product_wght),
                                'attributes': [{'option': avalue.name, 'name':avalue.attribute_id.name} for avalue in variant.attribute_value_ids],
                                "dimensions": {
                                    "length": str(variant.product_lngth),
                                    "width": str(variant.product_width),
                                    "height": str(variant.product_hght),
                                  },
                            }
                            url = "products/" +str(prod_export_res.get('id')) + "/variations"
                            prod_var_res = wcapi.post("products/" +str(prod_export_res.get('id')) + "/variations", variation_vals).json()
                            if prod_var_res:    
                                variant.write({'woocom_variant_id': prod_var_res.get('id'),'product_to_be_exported': False})
                    

                
            
                
