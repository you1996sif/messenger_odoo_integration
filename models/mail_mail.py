from odoo import models, api

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