# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
import json
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from datetime import datetime
from odoo.exceptions import Warning
import time


class SaleShop(models.Model):
    _inherit = 'sale.shop'
    _description = "The woocommerce determines the woocommerce view"
    # _order = 'sequence'

    woocom_kanban_dashboard = fields.Text(compute='_woocom_kanban_dashboard')

    
    @api.one
    def _woocom_kanban_dashboard(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.invoice']
        stock_obj = self.env['stock.picking']
       
        all_order_ids = order_obj.search([('shop_id','=',self[0].id)]) 
        pending_order_ids = order_obj.search([('shop_id','=',self[0].id),('woocom_id','!=',False),('state','in',('sale','sent'))])
        complete_order_ids = order_obj.search([('shop_id','=',self[0].id),('woocom_id','!=',False),('state','=','done')])
        draft_order_ids = order_obj.search([('shop_id','=',self[0].id),('woocom_id','!=',False),('state','=','draft')])
        cancel_order_ids = order_obj.search([('shop_id','=',self[0].id),('woocom_id','!=',False),('state','=','cancel')])
        
        origin_list = [s.name for s in all_order_ids]
        all_invoice_ids = invoice_obj.search([('is_woocom','=',True),('origin', 'in', origin_list)])
        pending_invoice_ids = invoice_obj.search([('is_woocom','=',True),('origin', 'in', origin_list),('state','!=','paid')])
        complete_invoice_ids = invoice_obj.search([('is_woocom','=',True),('origin', 'in', origin_list),('state','=','paid')])
        draft_invoice_ids = invoice_obj.search([('is_woocom','=',True),('origin', 'in', origin_list),('state','=','draft')])
        cancel_invoice_ids = invoice_obj.search([('is_woocom','=',True),('origin', 'in', origin_list),('state','=','cancel')])
        
        all_stock_ids = stock_obj.search([('is_woocom','=',True), ('origin', 'in', origin_list)])
        pending_stock_ids = stock_obj.search([('is_woocom','=',True),('origin', 'in', origin_list),('state','in', ('confirmed', 'waiting'))])
        complete_stock_ids = stock_obj.search([('is_woocom','=',True),('origin', 'in', origin_list),('state','=','done')])
#         late_delivey_ids = stock_obj.search([('is_presta','=',True),('origin', 'in', origin_list),('min_date','<',datetime.today())])
        back_order_ids = stock_obj.search([('is_woocom','=',True),('origin', 'in', origin_list),('backorder_id','<>', False)])
        
        
        woocommerce_webservices ={
                                 
        'all_order': len(all_order_ids),
        'pending_order': len(pending_order_ids),
        'complete_order': len(complete_order_ids),
        'draft_order': len(draft_order_ids),
        'cancel_order': len(cancel_order_ids),
        
        'all_invoice': len(all_invoice_ids),
        'pending_invoice': len(pending_invoice_ids),
        'complete_invoice': len(complete_invoice_ids),
        'draft_invoice': len(draft_invoice_ids),
        'cancel_invoice': len(cancel_invoice_ids),
        
        'all_stock': len(all_stock_ids),
        'pending_stock': len(pending_stock_ids),
        'complete_stock': len(complete_stock_ids),
#         'late_delivey':late_delivey_ids,
        'back_order': len(back_order_ids),

        }
        self.woocom_kanban_dashboard = json.dumps(woocommerce_webservices)


    @api.multi
    def action_view_all_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id','=',self[0].id)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    @api.multi
    def action_view_draft_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id','=',self[0].id),('woocom_id','!=',False),('state','=','draft')])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    @api.multi
    def action_view_cancel_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id','=',self[0].id),('woocom_id','!=',False),('state','=','cancel')])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result



    @api.multi
    def action_view_pending_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id','=',self[0].id),('woocom_id','!=',False),('state','in',('sale','sent'))])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


    @api.multi
    def action_view_complete_order(self):
        order_obj = self.env['sale.order']
        order_id = order_obj.search([('shop_id','=',self[0].id),('woocom_id','!=',False),('state','=','done')])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders_to_invoice')
        list_view_id = imd.xmlid_to_res_id('sale.view_quotation_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(order_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % order_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


    @api.multi
    def action_view_all_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.invoice']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search([('is_woocom', '=', True), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
 
 
    @api.multi
    def action_view_pending_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.invoice']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search([('is_woocom', '=', True),('state','=','open'),('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    @api.multi
    def action_view_draft_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.invoice']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search(
            [('is_woocom', '=', True), ('state', '=', 'draft'), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    @api.multi
    def action_view_cancel_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.invoice']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search(
            [('is_woocom', '=', True), ('state', '=', 'cancel'), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
 
    @api.multi
    def action_view_complete_invoice(self):
        order_obj = self.env['sale.order']
        invoice_obj = self.env['account.invoice']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        invoice_id = invoice_obj.search(
            [('is_woocom', '=', True), ('state', '=', 'paid'), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % invoice_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result    
    
    
    @api.multi
    def action_view_all_stock(self):
        order_obj = self.env['sale.order']
        stock_obj = self.env['stock.picking']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        stock_id = stock_obj.search([('is_woocom', '=', True), ('origin', 'in', origin_list)])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('stock.action_picking_tree_all')
        list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
        form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(stock_id) > 1:
            result['domain'] = "[('id','in',%s)]" % stock_id.ids
        elif len(stock_id) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = stock_id.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    
    @api.multi
    def action_view_pending_stock(self):
        order_obj = self.env['sale.order']
        stock_obj = self.env['stock.picking']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        stock_id = stock_obj.search([('is_woocom', '=', True), ('origin', 'in', origin_list),('state','in', ('confirmed', 'waiting'))])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('stock.action_picking_tree_all')
        list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
        form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(stock_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % stock_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


    @api.multi
    def action_view_complete_stock(self):
        order_obj = self.env['sale.order']
        stock_obj = self.env['stock.picking']
        all_order_ids = order_obj.search([('shop_id', '=', self[0].id)])
        origin_list = [s.name for s in all_order_ids]
        stock_id = stock_obj.search([('is_woocom', '=', True), ('origin', 'in', origin_list), ('state', '=', 'done')])

        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('stock.action_picking_tree_all')
        list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
        form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(stock_id) >= 1:
            result['domain'] = "[('id','in',%s)]" % stock_id.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    
    @api.multi
    def woocom_action_picking_tree_waiting(self):
        shop_obj = self.env['sale.shop']
        order_obj =self.env['sale.order']
        stock_obj = self.env['stock.picking']
        shop_id  = shop_obj.search([('woocommerce_instance_id','=',self.id)])
        all_order_ids = order_obj.search([('shop_id','=',shop_id.id)])
        origin_list = [s.name for s in all_order_ids] 
        all_stock_ids = stock_obj.search([('is_woocom','=',True), ('origin', 'in', origin_list)])
    
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('stock.action_picking_tree_waiting')
        list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
        form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'kanban'], [False, 'pivot']],
            'target': action.target,
            'context':{'search_default_waiting': 1,},
            'res_model': action.res_model,
        }
        if len(all_stock_ids) >= 1:
            result['domain'] = "[('id','in',%s)]" % all_stock_ids.ids
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


    
