

from odoo import models, fields, api, _
from odoo.http import request, Response

from ..controllers.nnewmessenger import FacebookWebhookController  


import logging

_logger = logging.getLogger(__name__)


class FacebookConversation(models.Model):
    _name = 'facebook_conversation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Facebook Messenger Conversation'
    _order = 'create_date desc'


    user_conversation_id = fields.Many2one('facebook.user.conversation', string='User Conversation', ondelete='cascade', required=True)
    create_date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    message = fields.Text(string='Message', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    sender = fields.Selection([('customer', 'Customer'), ('odoo', 'Odoo User')], string='Sender', required=True)
    odoo_user_id = fields.Many2one('res.users', string='Odoo User')
    reply_message = fields.Text(string='Reply')
    message_type = fields.Selection([
        ('email', 'Email'),
        ('comment', 'Comment'),
        ('notification', 'System notification'),
        ('user_notification', 'User notification'),
    ], string='Message Type', default='comment')
    subtype_id = fields.Many2one('mail.message.subtype', string='Subtype')
    
    
    @api.model
    def create(self, vals):
        if 'user_conversation_id' in vals and 'partner_id' not in vals:
            conversation = self.env['facebook.user.conversation'].browse(vals['user_conversation_id'])
            vals['partner_id'] = conversation.partner_id.id
        return super(FacebookConversation, self).create(vals)
    
    @api.model
    def create_from_facebook(self, partner, message):
        conversation = self.env['facebook.user.conversation'].sudo().create_or_update_conversation(partner.id)
        return self.create({
            'user_conversation_id': conversation.id,
            'message': message,
            'sender': 'customer',
        })

    def send_reply(self):
        _logger.info('Attempting to send reply')
        if self.reply_message:
            try:
                controller = FacebookWebhookController()
                sent = controller.send_facebook_message(self.partner_id.id, self.reply_message)
                
                _logger.info(f'Message sent: {sent}')

                if sent:
                    # If sent successfully, create a new conversation record for the reply
                    self.create({
                        'partner_id': self.partner_id.id,
                        'message': self.reply_message,
                        'sender': 'odoo',
                        'odoo_user_id': self.env.user.id,
                    })
                    # Clear the reply field
                    self.reply_message = False
                    # Post the reply in the chatter
                    self.message_post(body=f" {self.reply_message}")
                    return {'type': 'ir.actions.act_window_close'}
                else:
                    raise Exception("Failed to send message to Facebook")
            except Exception as e:
                error_message = f"Error sending message to Facebook: {str(e)}"
                _logger.error(error_message)
                self.message_post(body=error_message)
        else:
            _logger.warning("Attempted to send reply with empty message")
        return False
