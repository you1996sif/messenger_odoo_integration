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
                        # Create the record but don't set state to sent yet
                        # It will be set to sent after successful Facebook sending
                        _logger.info("Created facebook conversation message record")
            except (ValueError, SyntaxError) as e:
                _logger.error("Error parsing headers: %s", str(e))
                pass

        return super().create(values)

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        # Split records between Facebook messages and regular emails
        facebook_messages = self.filtered(lambda m: m.is_facebook_message)
        regular_emails = self - facebook_messages
        
        # Process Facebook messages
        for message in facebook_messages:
            try:
                # Get the related Facebook conversation
                conversation = self.env['facebook.user.conversation'].browse(message.res_id)
                if conversation:
                    # Here you would call your method to send to Facebook
                    # This is a placeholder - replace with your actual Facebook sending logic
                    self.env['facebook.user.conversation'].send_facebook_message(
                        conversation_id=conversation.id,
                        message_body=message.body_html,  # or message.body if you prefer plain text
                        attachment_ids=message.attachment_ids,
                    )
                    
                    # Mark as sent after successful Facebook sending
                    message.write({
                        'state': 'sent',
                        'date': fields.Datetime.now()
                    })
                    _logger.info(f"Successfully sent Facebook message for conversation {conversation.id}")
            except Exception as e:
                _logger.error(f"Error sending Facebook message: {str(e)}")
                if raise_exception:
                    raise
        
        # Process regular emails normally
        if regular_emails:
            return super(MailMail, regular_emails)._send(
                auto_commit=auto_commit,
                raise_exception=raise_exception,
                smtp_session=smtp_session
            )
        return True

    @api.model
    def search_and_cancel_by_body(self, body_text):
        if not body_text:
            return
        try:
            # Search for emails containing the given text in the body
            emails = self.search([
                ('body_html', 'ilike', body_text),
                ('state', 'in', ['outgoing', 'ready'])
            ])
            
            if emails:
                emails.write({'state': 'cancel'})
                _logger.info("Cancelled %d email(s) with body containing: %s", len(emails), body_text)
            else:
                _logger.info("No emails found to cancel with body containing: %s", body_text)
                
        except Exception as e:
            _logger.error("Error in search_and_cancel_by_body: %s", str(e))