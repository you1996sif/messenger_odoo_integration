from odoo import models, api, _, fields
from odoo.exceptions import UserError
import ast
import logging

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, values):
        if 'headers' in values:
            try:
                headers = ast.literal_eval(values['headers'])
                if isinstance(headers, dict) and 'X-Odoo-Objects' in headers:
                    x_odoo_objects = headers['X-Odoo-Objects']
                    if isinstance(x_odoo_objects, str) and x_odoo_objects.startswith('facebook.user.conversation'):
                        # Set the state to 'sent' immediately
                        values['state'] = 'sent'
                        # Optionally, set a sent date
                        values['date'] = fields.Datetime.now()
            except (ValueError, SyntaxError):
                # If there's an error parsing the headers, just proceed normally
                pass

        return super(MailMail, self).create(values)

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        # For emails related to facebook.user.conversation, mark as sent without actually sending
        facebook_mails = self.filtered(lambda m: m.model == 'facebook.user.conversation')
        if facebook_mails:
            facebook_mails.write({'state': 'sent'})
        
        # Process other emails normally
        return super(MailMail, self - facebook_mails)._send(
            auto_commit=auto_commit, raise_exception=raise_exception, smtp_session=smtp_session)
        
    @api.model
    def search_and_cancel_by_body(self, body_text):
        emails = self.search([('body_html', 'ilike', body_text), ('state', 'in', ['outgoing', 'ready'])])
        if emails:
            cancelled_count = emails.write({'state': 'cancel'})
            _logger.info(f"{cancelled_count} email(s) cancelled with body containing: {body_text}")
        else:
            _logger.info(f"No emails found to cancel with body containing: {body_text}")