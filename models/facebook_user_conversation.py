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
    


    # def message_post(self, **kwargs):
    #     message = super(FacebookUserConversation, self).message_post(**kwargs)
        
    #     # Send the message to Facebook only if it's not coming from Facebook
    #     if not self.env.context.get('from_facebook'):
    #         controller = FacebookWebhookController()
    #         clean_body = controller.strip_html(message.body)
    #         if clean_body:
    #             sent = controller.send_facebook_message(self.partner_id.id, clean_body, env=self.env)
                
    #             if not sent:
    #                 raise UserError(_("Failed to send message to Facebook."))
        
    #     return message
    def message_post(self, **kwargs):
        # Check if the message is coming from the Facebook conversation view
        if self.env.context.get('facebook_message'):
            return self.send_facebook_message(kwargs.get('body'))
        return super(FacebookUserConversation, self).message_post(**kwargs)

    def send_facebook_message(self, message):
        controller = FacebookWebhookController()
        clean_message = controller.strip_html(message)
        if clean_message:
            sent = controller.send_facebook_message(self.partner_id.id, clean_message, env=self.env)
            if sent:
                self.env['facebook_conversation'].sudo().create({
                    'user_conversation_id': self.id,
                    'partner_id': self.partner_id.id,
                    'message': clean_message,
                    'sender': 'odoo',
                    'odoo_user_id': self.env.user.id,
                    'message_type': 'comment',
                })
                self.write({'last_message_date': fields.Datetime.now()})
                return True
            else:
                raise UserError(_("Failed to send message to Facebook."))
        return False
    
    def add_message_to_chatter(self, message_text, sender, message_id=False):
        self.env['facebook_conversation'].sudo().create({
            'user_conversation_id': self.id,
            'partner_id': self.partner_id.id,
            'message': message_text,
            'sender': sender,
            'odoo_user_id': self.env.user.id if sender == 'odoo' else False,
            'message_type': 'comment',
            'message_id': message_id,
        })
        self.write({'last_message_date': fields.Datetime.now()})
        
        
    # def add_message_to_chatter(self, message_text, sender, message_id=False):
    #     self.with_context(from_facebook=True).message_post(
    #         body=message_text,
    #         message_type='comment',
    #         subtype_xmlid='mail.mt_comment',
    #         author_id=self.partner_id.id if sender == 'customer' else self.env.user.id,
    #     )

    #     self.env['facebook_conversation'].sudo().create({
    #         'user_conversation_id': self.id,
    #         'partner_id': self.partner_id.id,
    #         'message': message_text,
    #         'sender': sender,
    #         'odoo_user_id': self.env.user.id if sender == 'odoo' else False,
    #         'message_type': 'comment',
    #         'message_id': message_id,  # Add this line
    #     })

    #     self.write({'last_message_date': fields.Datetime.now()})