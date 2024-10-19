from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    facebook_id = fields.Char(string='Facebook ID', help="Facebook ID of the partner")
