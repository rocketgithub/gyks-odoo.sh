# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
from odoo import api, fields, models, _
 
class payment_gatway(models.Model):
     
    _name = 'payment.gatway'
    _rec_name = 'title'
    woocom_id = fields.Char(string="Woocom ID")
    title = fields.Char(string="Name")
    descrp = fields.Text(string="Description")
