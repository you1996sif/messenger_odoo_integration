from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request, Response
from ..controllers.nnewmessenger import FacebookWebhookController  
import logging
from contextlib import contextmanager


_logger = logging.getLogger(__name__)



class FacebookUserConversation(models.Model):
    _name = 'facebook.user.conversation'
    _description = 'Facebook User Conversation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='حساب العميل', required=True)
    facebook_id = fields.Char(related='partner_id.facebook_id', string='ID', store=True)
    client_name = fields.Char(string='اسم العميل ')
    note = fields.Char( string='ملاحظات')
    last_message_date = fields.Datetime(string='Last Message Date')
    conversation_status = fields.Selection([
        ('active', 'Active'),
        ('archived', 'Archived')
    ], default='active', string='Status')
    message_ids = fields.One2many('facebook_conversation', 'user_conversation_id', string='Messages')
    sale_order_ids = fields.One2many('sale.order', 'partner_id', string='Sale Orders', related='partner_id.sale_order_ids')
    order_line_ids = fields.One2many('sale.order.line', compute='_compute_order_lines')
    
    
    street = fields.Char(related='partner_id.street', string='Street', readonly=False, required=True)
    street2 = fields.Char(related='partner_id.street2', string='Street 2', readonly=False)
    state_id = fields.Many2one(related='partner_id.state_id', string='State', readonly=False, required=True)
    city = fields.Char(related='partner_id.city', string='City', readonly=False, required=True)
    zip = fields.Char(related='partner_id.zip', string='ZIP', readonly=False)
    country_id = fields.Many2one(related='partner_id.country_id', string='Country', readonly=False, required=True)
    phone = fields.Char(related='partner_id.phone', string='Phone', readonly=False, required=True)
    mobile = fields.Char(related='partner_id.mobile', string='Mobile')
    email = fields.Char(related='partner_id.email', string='Email', readonly=False)
    website = fields.Char(related='partner_id.website', string='Website', readonly=False)
    lang = fields.Selection(related='partner_id.lang', string='Language', readonly=False)
    category_id = fields.Many2many(related='partner_id.category_id', string='Tags', readonly=False)
    district_id = fields.Many2one(related='partner_id.district_id', string='District', readonly=False, required=True)
    
    def action_open_create_sale_order_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Sale Order',
            'res_model': 'create.sale.order.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.partner_id.id},
        }
    @api.depends('sale_order_ids.order_line')
    def _compute_order_lines(self):
        for record in self:
            record.order_line_ids = record.sale_order_ids.mapped('order_line')
    
        
        
        
    def action_add_sale_order(self):
        return {
            'name': _('Add Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_origin': f'Facebook Conversation: {self.id}',
            },
            'target': 'new',
        }

    def action_add_order_line(self):
        if not self.sale_order_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Sale Order'),
                    'message': _('Please create a sale order first.'),
                    'type': 'warning',
                }
            }
        return {
            'name': _('Add Order Line'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'view_mode': 'form',
            'context': {
                'default_order_id': self.sale_order_ids[0].id,
            },
            'target': 'new',
        }
        
        
        
        
        
        
    def name_get(self):
        return [(rec.id, f"{rec.partner_id.name} - Facebook Chat") for rec in self]
    
    
    
    helpdesk_ticket_ids = fields.One2many('helpdesk.ticket', 'facebook_conversation_id', string='Helpdesk Tickets')
    ticket_count = fields.Integer(compute='_compute_ticket_count', string='Ticket Count')

    def _compute_ticket_count(self):
        for record in self:
            record.ticket_count = len(record.helpdesk_ticket_ids)

    def action_create_ticket(self):
        """Create a helpdesk ticket from the Facebook conversation."""
        self.ensure_one()
        
        # Get the last message for the ticket description
        last_message = self.message_ids and self.message_ids[0].message or ''
        
        # Create the helpdesk ticket
        ticket_vals = {
            'name': _('Support Request from Facebook - %s') % self.partner_id.name,
            'partner_id': self.partner_id.id,
            'facebook_conversation_id': self.id,
            'description': last_message,
            'partner_email': self.partner_id.email,
            'partner_phone': self.partner_id.phone or self.partner_id.mobile,
        }
        
        ticket = self.env['helpdesk.ticket'].create(ticket_vals)
        
        # Add a note in the ticket about its creation from Facebook
        ticket.message_post(
            body=_('This ticket was created from a Facebook conversation'),
            message_type='notification'
        )
        
        # Show the created ticket to the user
        return {
            'type': 'ir.actions.act_window',
            'name': _('Helpdesk Ticket'),
            'res_model': 'helpdesk.ticket',
            'res_id': ticket.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    def action_view_tickets(self):
        """View all tickets related to this conversation."""
        self.ensure_one()
        return {
            'name': _('Helpdesk Tickets'),
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.ticket',
            'domain': [('facebook_conversation_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_facebook_conversation_id': self.id},
        }

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
        # Skip Facebook processing if message is from Facebook
        if self.env.context.get('from_facebook'):
            return super(FacebookUserConversation, self).message_post(**kwargs)
            
        message = super(FacebookUserConversation, self).message_post(**kwargs)
        
        try:
            controller = FacebookWebhookController()
            clean_body = controller.strip_html(message.body)
            if clean_body:
                sent = controller.send_facebook_message(
                    self.partner_id.id,
                    clean_body,
                    env=self.env
                )
                
                if not sent:
                    raise UserError(_("Failed to send message to Facebook."))
                return message
        except Exception as e:
            _logger.error('Error sending message to Facebook: %s', str(e))
            raise UserError(_("Failed to send message: %s") % str(e))
            
            return message
    # def message_post(self, **kwargs):
    #     _logger.info(f"message_post called with context: {self.env.context}")
    #     if self.env.context.get('facebook_message'):
    #         return self.send_facebook_message(kwargs.get('body'))
    #     return super(FacebookUserConversation, self).message_post(**kwargs)

    def send_facebook_message(self, message):
        self.ensure_one()
        controller = FacebookWebhookController()
        clean_message = controller.strip_html(message)
        if clean_message:
            sent = controller.send_facebook_message(self.partner_id.id, clean_message, env=self.env)
            if sent:
                self.message_post(
                    body=clean_message,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=self.env.user.partner_id.id,
                )
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
    # def send_facebook_message(self, message):
    #     self.ensure_one()
    #     _logger.info(f"Attempting to send Facebook message: {message}")
    #     controller = self.env['facebook.webhook.controller'].sudo()
    #     clean_message = controller.strip_html(message)
    #     if clean_message:
    #         _logger.info(f"Cleaned message: {clean_message}")
    #         sent = controller.send_facebook_message(self.partner_id.id, clean_message, env=self.env)
    #         _logger.info(f"Message sent status: {sent}")
    #         if sent:
    #             self.env['facebook_conversation'].sudo().create({
    #                 'user_conversation_id': self.id,
    #                 'partner_id': self.partner_id.id,
    #                 'message': clean_message,
    #                 'sender': 'odoo',
    #                 'odoo_user_id': self.env.user.id,
    #                 'message_type': 'comment',
    #             })
    #             self.write({'last_message_date': fields.Datetime.now()})
    #             return True
    #         else:
    #             error_msg = _("Failed to send message to Facebook.")
    #             _logger.error(error_msg)
    #             raise UserError(error_msg)
    #     else:
    #         _logger.warning("Attempted to send empty message")
    #     return False
    
    # def add_message_to_chatter(self, message_text, sender, message_id=False):
    #     self.env['facebook_conversation'].sudo().create({
    #         'user_conversation_id': self.id,
    #         'partner_id': self.partner_id.id,
    #         'message': message_text,
    #         'sender': sender,
    #         'odoo_user_id': self.env.user.id if sender == 'odoo' else False,
    #         'message_type': 'comment',
    #         'message_id': message_id,
    #     })
    #     self.write({'last_message_date': fields.Datetime.now()})
        
    
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
        
    def add_message_to_chatter(self, message_text, sender, message_id=False):
        _logger.info('Processing message to chatter: %s', message_id)
        
        with facebook_transaction(self):
            # Check for existing message
            if message_id:
                existing_message = self.env['facebook_conversation'].sudo().search([
                    ('message_id', '=', message_id)
                ], limit=1)
                if existing_message:
                    _logger.info('Message already exists: %s', message_id)
                    return

            # Post message to chatter
            self.with_context(from_facebook=True).message_post(
                body=message_text,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                author_id=self.partner_id.id if sender == 'customer' else self.env.user.partner_id.id,
            )
            
            try:
                # Create facebook conversation record if needed
                if message_id:
                    self.env['facebook_conversation'].sudo().create({
                        'user_conversation_id': self.id,
                        'partner_id': self.partner_id.id,
                        'message': message_text,
                        'sender': sender,
                        'odoo_user_id': self.env.user.id if sender == 'odoo' else False,
                        'message_type': 'comment',
                        'message_id': message_id,
                    })

                # Update last message date
                self.write({'last_message_date': fields.Datetime.now()})

                # Cancel any related emails
                if message_text:
                    self.env['mail.mail'].sudo().search_and_cancel_by_body(message_text)
                    
            except Exception as e:
                _logger.error('Error processing message: %s', str(e))
                raise
    
@contextmanager
def facebook_transaction(self):
    """Context manager for handling Facebook-related transactions."""
    try:
        with self.env.cr.savepoint():
            yield
    except Exception as e:
        _logger.error("Facebook transaction error: %s", str(e))
        raise UserError(_("Failed to process Facebook message: %s") % str(e))