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
        
        
    
   
   
   
   
   
   
   
   
   
    def message_post(self, **kwargs):
        """Override message_post to handle Facebook message sending and chatter updates"""
        # If message is from Facebook, post directly to chatter
        if self.env.context.get('from_facebook'):
            return super(FacebookUserConversation, self).message_post(**kwargs)

        # First create the message in chatter
        message = super(FacebookUserConversation, self).message_post(**kwargs)
        
        if message and message.body and not self.env.context.get('skip_facebook'):
            try:
                controller = FacebookWebhookController()
                clean_body = controller.strip_html(message.body)
                
                if clean_body:
                    # Generate a unique message ID
                    message_id = str(uuid.uuid4())
                    
                    # Send to Facebook
                    with self.env.cr.savepoint():
                        sent = controller.send_facebook_message(
                            partner_id=self.partner_id.id,
                            message=clean_body,
                            env=self.env
                        )
                        
                        if sent:
                            # Create Facebook conversation record
                            self.env['facebook_conversation'].sudo().create({
                                'user_conversation_id': self.id,
                                'partner_id': self.partner_id.id,
                                'message': clean_body,
                                'sender': 'odoo',
                                'odoo_user_id': self.env.user.id,
                                'message_type': 'comment',
                                'message_id': message_id
                            })
                            
                            # Update last message date
                            self.write({
                                'last_message_date': fields.Datetime.now()
                            })
                        else:
                            raise UserError(_("Failed to send message to Facebook."))
                            
            except Exception as e:
                _logger.error('Error sending message to Facebook: %s', str(e))
                raise UserError(_("Failed to send message: %s") % str(e))
        
        return message

    def add_message_to_chatter(self, message_text, sender, message_id=False):
        """Handle incoming messages from Facebook"""
        self.ensure_one()
        
        try:
            # Check for existing message to avoid duplicates
            if message_id:
                existing_message = self.env['facebook_conversation'].sudo().search([
                    ('message_id', '=', message_id)
                ], limit=1)
                
                if existing_message:
                    _logger.info('Duplicate message detected: %s', message_id)
                    return
            
            with self.env.cr.savepoint():
                # Post to chatter with proper attribution
                author_id = self.partner_id.id if sender == 'customer' else self.env.user.partner_id.id
                
                message = self.with_context(
                    from_facebook=True,
                    mail_create_nosubscribe=True
                ).message_post(
                    body=message_text,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=author_id
                )
                
                # Create facebook conversation record
                conversation = self.env['facebook_conversation'].sudo().create({
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
                
                # Commit the transaction
                self.env.cr.commit()
                
        except Exception as e:
            _logger.error('Error processing Facebook message: %s', str(e))
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
    
    