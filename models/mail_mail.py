from odoo import models, api, _
from odoo.exceptions import UserError


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, values):
        # Check if the email is related to facebook.user.conversation
        if values.get('model') == 'facebook.user.conversation':
            # Set the state to 'sent' immediately
            values['state'] = 'sent'
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
        # Search for emails containing the given text in the body
        emails = self.search([('body_html', 'ilike', body_text), ('state', 'in', ['outgoing', 'ready'])])
        
        if not emails:
            raise UserError(_("No matching emails found to cancel."))
        
        # Cancel the found emails
        cancelled_count = emails.write({'state': 'cancel'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Emails Cancelled"),
                'message': _("%s email(s) have been cancelled.") % cancelled_count,
                'type': 'success',
                'sticky': False,
            }
        }