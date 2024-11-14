# Create a new file named helpdesk_ticket_inherit.py

from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    facebook_conversation_id = fields.Many2one('facebook.user.conversation', string='Facebook Conversation')
    
    
    
    
    @api.model
    def create(self, vals):
        record = super(HelpdeskTicket, self).create(vals)
        if vals.get('user_id'):
            record.message_follower_ids.unlink()
        return record
    
    def write(self, vals):
        result = super(HelpdeskTicket, self).write(vals)
        if vals.get('user_id'):
            self.message_follower_ids.unlink()
        return result
    
    def action_view_facebook_conversation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facebook Conversation',
            'res_model': 'facebook.user.conversation',
            'res_id': self.facebook_conversation_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }