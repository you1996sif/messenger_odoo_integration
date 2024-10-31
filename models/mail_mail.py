from odoo import models, api, _, fields
from odoo.exceptions import UserError
import ast
import logging

_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'

    is_facebook_message = fields.Boolean(
        string='Is Facebook Message',
        help='Technical field to identify messages meant for Facebook',
        default=False
    )

    @api.model
    def create(self, values):
        if 'headers' in values:
            try:
                headers = ast.literal_eval(values['headers'])
                if isinstance(headers, dict) and 'X-Odoo-Objects' in headers:
                    x_odoo_objects = headers['X-Odoo-Objects']
                    if isinstance(x_odoo_objects, str) and x_odoo_objects.startswith('facebook.user.conversation'):
                        values['is_facebook_message'] = True
                        # Don't mark as sent yet
                        _logger.info("Created facebook conversation message record")
            except (ValueError, SyntaxError) as e:
                _logger.error("Error parsing headers: %s", str(e))
                pass

        mail = super().create(values)
        
        # Trigger immediate processing for facebook messages
        if mail.is_facebook_message:
            self._trigger_facebook_message_process(mail)
        
        return mail

    def _trigger_facebook_message_process(self, mail):
        """Process Facebook message and update chatter immediately"""
        try:
            # Process the Facebook message
            conversation = self.env['facebook.user.conversation'].browse(mail.res_id)
            if conversation:
                # Here you would add your Facebook sending logic
                # For now, we'll just mark it as processed
                mail.write({
                    'state': 'sent',
                    'date': fields.Datetime.now()
                })
                
                # Force update the message_ids in the chatter
                if mail.mail_message_id:
                    mail.mail_message_id.write({
                        'message_type': 'comment',
                        'subtype_id': self.env.ref('mail.mt_comment').id,
                    })
                    
                    # Notify UI about the new message
                    self.env['bus.bus']._sendone(
                        conversation,
                        'mail.message/insert',
                        {
                            'message': mail.mail_message_id.message_format()[0],
                            'record_name': conversation.display_name,
                        }
                    )
                    
                _logger.info(f"Successfully processed Facebook message for conversation {conversation.id}")
                
        except Exception as e:
            _logger.error(f"Error processing Facebook message: {str(e)}")
            mail.write({'state': 'exception'})

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        # Skip email sending for Facebook messages
        facebook_messages = self.filtered(lambda m: m.is_facebook_message)
        regular_emails = self - facebook_messages
        
        # Mark Facebook messages as sent without email processing
        if facebook_messages:
            facebook_messages.write({
                'state': 'sent',
                'date': fields.Datetime.now()
            })
        
        # Process regular emails normally
        if regular_emails:
            return super(MailMail, regular_emails)._send(
                auto_commit=auto_commit,
                raise_exception=raise_exception,
                smtp_session=smtp_session
            )
        return True

    @api.model
    def process_email_queue(self, ids=None):
        """Override to handle Facebook messages differently"""
        if ids is None:
            ids = []
        messages = self.browse(ids) if ids else self.search([
            ('state', 'in', ['outgoing', 'ready']),
            '|',
            ('scheduled_date', '<=', fields.Datetime.now()),
            ('scheduled_date', '=', False)
        ])
        
        # Split and process Facebook messages separately
        facebook_messages = messages.filtered(lambda m: m.is_facebook_message)
        regular_emails = messages - facebook_messages
        
        # Process Facebook messages
        for message in facebook_messages:
            self._trigger_facebook_message_process(message)
        
        # Process regular emails
        return super(MailMail, regular_emails).process_email_queue()