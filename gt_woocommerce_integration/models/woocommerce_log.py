# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import models, fields, api

class WoocommerceLog(models.Model):
    _name = 'woocommerce.log'
    # _rec_name = 'name'
    
    @api.model
    def create(self,vals):
        if not vals.get('log_name'):
            name = self.env['ir.sequence'].next_by_code('log.error')
            vals.update({
                'log_name': name
            })
        return super(WoocommerceLog, self).create(vals)
            
    
        

    log_name = fields.Char(string="Log Name", required=False, )
    log_date = fields.Datetime(string="Log Date",index=True,default=fields.Datetime.now)
    error_lines = fields.One2many("log.error", "log_id", string="Error lines", required=False, )
  

    all_operations = fields.Selection(string="Operations",
                                         selection=[('import_attributes', 'Import Woocommerce product attributes'),
                                                    ('import_categories', 'Import Woocommerce product category'),
                                                    ('import_customer', 'Import Woocommerce customers'),
                                                    ('import_products', 'Import Woocommerce product'),
                                                    ], )





class log_error(models.Model):
    _name = 'log.error'
    _rec_name = 'log_description'
    # _description = 'New Description'

    log_description = fields.Text(string="Log description")
    log_id = fields.Many2one("woocommerce.log", string="Log description", required=False, )

