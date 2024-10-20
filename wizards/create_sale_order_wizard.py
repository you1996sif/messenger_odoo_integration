from odoo import api, fields, models

class CreateSaleOrderWizard(models.TransientModel):
    _name = 'create.sale.order.wizard'
    _description = 'Create Sale Order Wizard'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    date_order = fields.Datetime(string='Order Date', default=fields.Datetime.now)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    team_id = fields.Many2one('crm.team', string='Sales Team')
    client_order_ref = fields.Char(string='Customer Reference')
    order_line_ids = fields.One2many('create.sale.order.line.wizard', 'wizard_id', string='Order Lines')


    @api.model
    def default_get(self, fields):
        res = super(CreateSaleOrderWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            conversation = self.env['facebook.user.conversation'].browse(active_id)
            res['partner_id'] = conversation.partner_id.id
            res['pricelist_id'] = conversation.partner_id.property_product_pricelist.id
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.pricelist_id = self.partner_id.property_product_pricelist
            self.payment_term_id = self.partner_id.property_payment_term_id
            self.team_id = self.env['crm.team']._get_default_team_id(user_id=self.env.uid)


    def action_create_sale_order(self):
        self.ensure_one()
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'date_order': self.date_order,
            'payment_term_id': self.payment_term_id.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'client_order_ref': self.client_order_ref,
            'order_line': [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.price_unit,
                }) for line in self.order_line_ids
            ],
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

class CreateSaleOrderLineWizard(models.TransientModel):
    _name = 'create.sale.order.line.wizard'
    _description = 'Create Sale Order Line Wizard'

    wizard_id = fields.Many2one('create.sale.order.wizard', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    tax_id = fields.Many2many('account.tax', string='Taxes')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.list_price
            self.tax_id = self.product_id.taxes_id