from odoo import models, fields, api, _
from odoo.exceptions import UserError

from odoo.http import request, Response

from ..controllers.nnewmessenger import FacebookWebhookController  


import logging

_logger = logging.getLogger(__name__)



class FacebookUserConversation(models.Model):
    _name = 'facebook.user.conversation'
    _description = 'Facebook User Conversation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    facebook_id = fields.Char(related='partner_id.facebook_id', string='Facebook ID', store=True)
    last_message_date = fields.Datetime(string='Last Message Date')
    conversation_status = fields.Selection([
        ('active', 'Active'),
        ('archived', 'Archived')
    ], default='active', string='Status')
    message_ids = fields.One2many('facebook_conversation', 'user_conversation_id', string='Messages')


    def name_get(self):
        return [(rec.id, f"{rec.partner_id.name} - Facebook Chat") for rec in self]

    @api.model
    def create_or_update_conversation(self, partner_id):
        conversation = self.search([('partner_id', '=', partner_id)], limit=1)
        if not conversation:
            conversation = self.create({
                'partner_id': partner_id,
                'facebook_id': self.env['res.partner'].browse(partner_id).facebook_id,
            })
        else:
            conversation.write({'last_message_date': fields.Datetime.now()})
        return conversation

    def action_archive(self):
        self.write({'conversation_status': 'archived'})

    def action_unarchive(self):
        self.write({'conversation_status': 'active'})
    


    def message_post(self, **kwargs):
        # Don't create a message in the chatter for Facebook messages
        if self.env.context.get('from_facebook'):
            return True

        message = super(FacebookUserConversation, self).message_post(**kwargs)
        
        # Send the message to Facebook
        controller = FacebookWebhookController()
        clean_body = controller.strip_html(message.body)
        if clean_body:
            sent = controller.send_facebook_message(self.partner_id.id, clean_body, env=self.env)
            
            if not sent:
                raise UserError(_("Failed to send message to Facebook."))
        
        return message
