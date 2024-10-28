# Create a new file helpdesk_ticket.py in your models directory

from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    facebook_conversation_id = fields.Many2one('facebook.user.conversation', string='Facebook Conversation')