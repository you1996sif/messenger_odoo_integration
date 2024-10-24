from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request, Response
from ..controllers.nnewmessenger import FacebookWebhookController  
import logging
from contextlib import contextmanager
import uuid


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
    


    

    def send_message_to_facebook(self, message_text, message_id=None):
        """Separate method to handle Facebook message sending with improved logging"""
        _logger.info(f"Sending message to Facebook: {message_text}")
        
        try:
            controller = FacebookWebhookController()
            clean_body = controller.strip_html(message_text)
            
            if not clean_body:
                _logger.warning("Empty message after cleaning HTML")
                return False
                
            if not message_id:
                message_id = str(uuid.uuid4())
                
            with self.env.cr.savepoint():
                sent = controller.send_facebook_message(
                    partner_id=self.partner_id.id,
                    message=clean_body,
                    env=self.env
                )
                
                if sent:
                    _logger.info(f"Message sent successfully to Facebook. Creating conversation record with ID: {message_id}")
                    
                    # Create Facebook conversation record
                    conv_record = self.env['facebook_conversation'].sudo().create({
                        'user_conversation_id': self.id,
                        'partner_id': self.partner_id.id,
                        'message': clean_body,
                        'sender': 'odoo',
                        'odoo_user_id': self.env.user.id,
                        'message_type': 'comment',
                        'message_id': message_id,
                        'date': fields.Datetime.now()
                    })
                    
                    _logger.info(f"Created Facebook conversation record: {conv_record.id}")
                    
                    # Update last message date
                    self.write({'last_message_date': fields.Datetime.now()})
                    
                    # Explicitly commit the transaction
                    self.env.cr.commit()
                    return True
                    
                _logger.error("Failed to send message to Facebook")
                return False
                
        except Exception as e:
            _logger.exception("Error in send_message_to_facebook: %s", str(e))
            self.env.cr.rollback()
            return False

    def message_post(self, **kwargs):
        """Enhanced message posting with proper bus notifications"""
        if self.env.context.get('from_facebook'):
            return super(FacebookUserConversation, self).message_post(**kwargs)

        try:
            # Create message in chatter
            message = super(FacebookUserConversation, self).message_post(**kwargs)
            _logger.info(f"Created chatter message: {message.id}")

            if message and message.body and not self.env.context.get('skip_facebook'):
                controller = FacebookWebhookController()
                sent = controller.send_facebook_message(
                    partner_id=self.partner_id.id,
                    message=message.body,
                    env=self.env
                )

                if sent:
                    # Notify bus about the new message
                    self._notify_message_update(message)
                else:
                    _logger.error("Failed to send message to Facebook")

            return message

        except Exception as e:
            _logger.exception(f"Error in message_post: {str(e)}")
            raise UserError(_("Failed to process message: %s") % str(e))

    def _notify_message_update(self, message):
        """Notify the bus about message updates"""
        self.ensure_one()
        notification_data = {
            'type': 'message_posted',
            'message': {
                'id': message.id,
                'body': message.body,
                'date': fields.Datetime.to_string(message.date),
                'author_id': [
                    message.author_id.id,
                    message.author_id.display_name
                ] if message.author_id else False,
            },
            'model': self._name,
            'res_id': self.id,
        }

        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'mail.message/insert',
            notification_data
        )

    def add_message_to_chatter(self, message_text, sender, message_id=False):
        """Handle incoming Facebook messages with proper UI updates"""
        self.ensure_one()
        
        try:
            if message_id:
                existing = self.env['facebook_conversation'].sudo().search([
                    ('message_id', '=', message_id)
                ], limit=1)
                if existing:
                    _logger.info(f"Skipping duplicate message: {message_id}")
                    return True

            with self.env.cr.savepoint():
                # Post to chatter
                author_id = self.partner_id.id if sender == 'customer' else self.env.user.partner_id.id
                message = self.with_context(
                    from_facebook=True,
                    mail_create_nosubscribe=True,
                    tracking_disable=True,
                    mail_notify_author=True  # Ensure author gets notified
                ).message_post(
                    body=message_text,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=author_id,
                    notification_ids=[(0, 0, {
                        'res_partner_id': self.env.user.partner_id.id,
                        'notification_type': 'inbox'
                    })]
                )

                # Create Facebook conversation record
                self.env['facebook_conversation'].sudo().create({
                    'user_conversation_id': self.id,
                    'partner_id': self.partner_id.id,
                    'message': message_text,
                    'sender': sender,
                    'odoo_user_id': self.env.user.id if sender == 'odoo' else False,
                    'message_type': 'comment',
                    'message_id': message_id or str(uuid.uuid4())
                })

                # Update last message date
                self.write({'last_message_date': fields.Datetime.now()})

                # Notify about the new message
                if message:
                    self._notify_message_update(message)

                self.env.cr.commit()
                return True

        except Exception as e:
            self.env.cr.rollback()
            _logger.exception(f"Error processing Facebook message: {str(e)}")
            raise UserError(_("Failed to process Facebook message: %s") % str(e))

    @api.model
    def create_or_update_conversation(self, partner_id):
        """Create or update conversation with proper notifications"""
        conversation = self.search([('partner_id', '=', partner_id)], limit=1)
        if not conversation:
            conversation = self.create({
                'partner_id': partner_id,
                'facebook_id': self.env['res.partner'].browse(partner_id).facebook_id,
            })
        else:
            conversation.write({'last_message_date': fields.Datetime.now()})
            
        return conversation

    def add_message_to_chatter(self, message_text, sender, message_id=False):
        """Handle incoming Facebook messages with improved transaction handling"""
        self.ensure_one()
        _logger.info("Processing incoming Facebook message: %s, sender: %s, message_id: %s", 
                    message_text, sender, message_id)

        try:
            # Duplicate check with proper error handling
            if message_id:
                existing = self.env['facebook_conversation'].sudo().search([
                    ('message_id', '=', message_id)
                ], limit=1)
                
                if existing:
                    _logger.info("Skipping duplicate message: %s", message_id)
                    return True

            with self.env.cr.savepoint():
                # Post to chatter with all necessary context
                author_id = self.partner_id.id if sender == 'customer' else self.env.user.partner_id.id
                
                message = self.with_context(
                    from_facebook=True,
                    mail_create_nosubscribe=True,
                    tracking_disable=True,
                    mail_notify_force_send=False
                ).message_post(
                    body=message_text,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=author_id,
                )
                
                if not message:
                    raise UserError(_("Failed to create message in chatter"))

                # Create conversation record
                conv_record = self.env['facebook_conversation'].sudo().create({
                    'user_conversation_id': self.id,
                    'partner_id': self.partner_id.id,
                    'message': message_text,
                    'sender': sender,
                    'odoo_user_id': self.env.user.id if sender == 'odoo' else False,
                    'message_type': 'comment',
                    'message_id': message_id or str(uuid.uuid4()),
                    'date': fields.Datetime.now()
                })

                self.write({'last_message_date': fields.Datetime.now()})
                
                # Explicit commit
                self.env.cr.commit()
                return True

        except Exception as e:
            _logger.exception("Error processing Facebook message: %s", str(e))
            self.env.cr.rollback()
            raise UserError(_("Failed to process Facebook message: %s") % str(e))
        
        
        
    
@contextmanager
def facebook_transaction(self):
    """Context manager for handling Facebook-related transactions."""
    try:
        with self.env.cr.savepoint():
            yield
    except Exception as e:
        _logger.error("Facebook transaction error: %s", str(e))
        raise UserError(_("Failed to process Facebook message: %s") % str(e))
    
    