from odoo import models, fields

class MessengerMessage(models.Model):
    _name = 'messenger_message'
    _description = 'Messenger Message'

    name = fields.Char(string='Message ID', required=True, help='Unique message identifier from Messenger')
    text = fields.Text(string='Message Text')
    sender_id = fields.Char(string='Sender ID')
    received_at = fields.Datetime(string='Received At', default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string='Related Customer')
