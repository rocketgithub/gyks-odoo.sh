# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models
from odoo.addons.gt_woocommerce_integration.api import woocom_api
class WoocommerceInstance(models.Model):
    _name = 'woocommerce.instance'

    name = fields.Char(string='Name')
    location = fields.Char(string='Location')
    consumer_key = fields.Char(string='Consumer key')
    secret_key=fields.Char(string='Secret Key')
    state = fields.Selection([('draft', 'Draft'), ('connected', 'Connected')],string='State', default='draft') 

# this code is suitable for v2 version.
    @api.multi
    def check_connection(self):
        for rec in self:
#             wcapi = API(
#     url="http://192.168.1.21/wordpress",
#     consumer_key="ck_0e1d2054359b5220edf935c6485d73a860291560",
#     consumer_secret="cs_c2ff80eb7d948dba50a86e4523e0a49043b856af",
#     wp_api=True,
#     version="wc/v2"
# )
#             wcapi = API(
#                 url=rec.location,
#                 consumer_key=rec.consumer_key,
#                 consumer_secret=rec.secret_key,
#                 wp_api=True,
#                 version="wc/v2"
#             )
            wcapi = woocom_api.API(url=rec.location, consumer_key=rec.consumer_key, consumer_secret=rec.secret_key, wp_api=True, version='wc/v2')
            r = wcapi.get("products")
            if not r.status_code == 200:
                raise Warning(("Enter Valid url"))
            rec.write({'state':'connected'})
        return True
    
    @api.multi
    def create_shop(self):
        sale_shop_obj = self.env['sale.shop']
        price_list_obj = self.env['product.pricelist']
        journal_obj = self.env['account.journal']
        company_obj = self.env['res.company']
        warehouse_obj = self.env['stock.warehouse']
        product_prod_obj = self.env['product.product']
#         location_route_obj = self.env['stock.location.route']
        workflow_obj = self.env['import.order.workflow']
        res_partner_obj = self.env['res.partner']
        
        def_journal_ids = journal_obj.search([('type', '=', 'bank')])
        def_pricelist_ids = price_list_obj.search([])
        def_workflow_ids = workflow_obj.search([('name','=','Basic Workflow')])
        def_partner_ids = res_partner_obj.search([('name','=','Guest'),('company_type','=','person')])
        company_ids = company_obj.search([])
        def_ship_ids = product_prod_obj.search([('type', '=', 'service'),('name','like','%Shipping%')])
        def_gift_ids = product_prod_obj.search([('type', '=', 'service'),('name', 'like', '%Gift%')])
        def_warehouse_ids = warehouse_obj.search([])

        for instance in self:
            shop_name = instance.name + '_shop'
            shop_vals = {
                'name' : shop_name,
                'woocommerce_instance_id' : instance.id,
                'woocommerce_shop' : True,
                'pricelist_id': def_pricelist_ids and def_pricelist_ids[0].id,
                'sale_journal': def_journal_ids and def_journal_ids[0].id,
                'company_id': company_ids and company_ids[0].id,
                'shipment_fee_product_id': def_ship_ids and def_ship_ids[0].id,
                'gift_wrapper_fee_product_id': def_gift_ids and def_gift_ids[0].id,
                'warehouse_id' : def_warehouse_ids and def_warehouse_ids[0].id,
                'prefix': instance.name[:2] + '_',
                'partner_id' : def_partner_ids and def_partner_ids[0].id,
                'workflow_id': def_workflow_ids and def_workflow_ids[0].id,
            }
            # print"shop_vals newwwwwww===============>",shop_vals
            shop_ids = sale_shop_obj.search([('woocommerce_instance_id', '=', self[0].id), ('name', '=',shop_name)])
    
            if not shop_ids:
                sale_shop_id = sale_shop_obj.create(shop_vals)
        return True
    
