from odoo import tools
from odoo import api, fields, models


class WoocommerceSaleReport(models.Model):
    _name = "woocommerce.sales.report"
    _description = "Woocommerce Sales Orders Statistics"
    _auto = False
    _order = 'date desc'

#     name = fields.Char('Order Reference', readonly=True)
    date = fields.Datetime('Date Order', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
#     product_uom = fields.Many2one('product.uom', 'Unit of Measure', readonly=True)
    product_uom_qty = fields.Float('# of Qty', readonly=True)
    woocommerce_shop = fields.Many2one('sale.shop', string="woocommerce Shop")
    woocommerce_instance_id = fields.Many2one('woocommerce.instance', string="woocommerce Instance")
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    price_total = fields.Float('Total', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    team_id = fields.Many2one('crm.team', 'Sales Team', readonly=True, oldname='section_id')
    country_id = fields.Many2one('res.country', 'Partner Country', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True)
    
    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
             SELECT min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.price_total / COALESCE(cr.rate, 1.0)) as price_total,
                    s.name as name,
                    s.date_order as date,
                    s.state as state,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    ss.woocommerce_instance_id as woocommerce_instance_id,
                    ss.id as woocommerce_shop,
                    t.categ_id as categ_id,
                    s.team_id as team_id,
                    p.product_tmpl_id,
                    partner.country_id as country_id
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _from(self):
        from_str = """
                sale_order_line l
                      join sale_order s on (l.order_id=s.id)
                      join sale_shop ss on (s.shop_id = ss.id and ss.woocommerce_shop = true)
                      join woocommerce_instance woo on (ss.woocommerce_instance_id=woo.id)
                      join res_partner partner on s.partner_id = partner.id
                      left join product_product p on (l.product_id=p.id)
                      left join product_template t on (p.product_tmpl_id=t.id)
                      left join product_uom u on (u.id=l.product_uom)
                      left join product_uom u2 on (u2.id=t.uom_id)
                      left join product_pricelist pp on (s.pricelist_id = pp.id)
                      left join currency_rate cr on (cr.currency_id = pp.currency_id and
                      cr.company_id = s.company_id and
                      cr.date_start <= coalesce(s.date_order, now()) and
                      (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
                
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.name,
                    s.date_order,
                    s.partner_id,
                    s.user_id,
                    s.state,
                    s.company_id,
                    s.team_id,
                    ss.id,
                    p.product_tmpl_id,
                    ss.woocommerce_instance_id,
                    partner.country_id,
                    partner.commercial_partner_id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        q = """CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by())
        self.env.cr.execute(q)
