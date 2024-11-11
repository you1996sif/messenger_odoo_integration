# from odoo import models, api, _, fields
# from odoo.exceptions import UserError
# import ast
# import logging

# _logger = logging.getLogger(__name__)


# class MailMail(models.Model):
#     _inherit = 'mail.mail'

#     @api.model
#     def create(self, values):
#         if 'headers' in values:
#             try:
#                 headers = ast.literal_eval(values['headers'])
#                 if isinstance(headers, dict) and 'X-Odoo-Objects' in headers:
#                     x_odoo_objects = headers['X-Odoo-Objects']
#                     if isinstance(x_odoo_objects, str) and x_odoo_objects.startswith('facebook.user.conversation'):
#                         # Set the state to 'sent' immediately
#                         values['state'] = 'sent'
#                         # Optionally, set a sent date
#                         values['date'] = fields.Datetime.now()
#             except (ValueError, SyntaxError):
#                 # If there's an error parsing the headers, just proceed normally
#                 pass

#         return super(MailMail, self).create(values)

#     def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
#         # For emails related to facebook.user.conversation, mark as sent without actually sending
#         facebook_mails = self.filtered(lambda m: m.model == 'facebook.user.conversation')
#         if facebook_mails:
#             facebook_mails.write({'state': 'sent'})
        
#         # Process other emails normally
#         return super(MailMail, self - facebook_mails)._send(
#             auto_commit=auto_commit, raise_exception=raise_exception, smtp_session=smtp_session)
        
#     @api.model
#     def search_and_cancel_by_body(self, body_text):
#         if not body_text:
#             return
#         try:
#             # Search for emails containing the given text in the body
#             emails = self.search([
#                 ('body_html', 'ilike', body_text),
#                 ('state', 'in', ['outgoing', 'ready'])
#             ])
            
#             if emails:
#                 emails.write({'state': 'cancel'})
#                 _logger.info("Cancelled %d email(s) with body containing: %s", len(emails), body_text)
#             else:
#                 _logger.info("No emails found to cancel with body containing: %s", body_text)
                
#         except Exception as e:
#             _logger.error("Error in search_and_cancel_by_body: %s", str(e))


from odoo import models, api, _, fields
from odoo.exceptions import UserError
import ast
import logging

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, values):
        _logger.info('create')
        
        if 'headers' in values:
            _logger.info(' if headers')
            try:
                _logger.info('try')
                headers = ast.literal_eval(values['headers'])
                _logger.info('headers')
                _logger.info(headers)
                if isinstance(headers, dict) and 'X-Odoo-Objects' in headers:
                    _logger.info(' isinstance(headers,')
                    x_odoo_objects = headers['X-Odoo-Objects']
                    if isinstance(x_odoo_objects, str) and x_odoo_objects.startswith('facebook.user.conversation'):
                        _logger.info(' instance(x_odoo_objects,')
                        # Set the state to 'sent' immediately
                        values['state'] = 'sent'
                        # Optionally, set a sent date
                        values['date'] = fields.Datetime.now()
            except (ValueError, SyntaxError):
                # If there's an error parsing the headers, just proceed normally
                pass
        _logger.info(' ggggggggggggggggg')

        return super(MailMail, self).create(values)

  
    @api.model
    def search_and_cancel_by_body(self, body_text):
        _logger.info('search_and_cancel_by_body')
        if not body_text:
            _logger.info('if not body_text')
            return
        else:
            
            _logger.info('else')
            return {
        'type': 'ir.actions.client',
        'tag': 'reload'}
       
    @api.model
    def reload_page(self):
        """Trigger a page reload via client action"""
        _logger.info('Triggering page reload')
        followers = self.message_follower_ids.filtered(
            lambda f: f.partner_id == self.env.user.partner_id
        )
        if followers:
            followers.sudo().unlink()
        _logger.info("if followers:")
        try:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        except Exception as e:
            _logger.error(f'Error during reload: {str(e)}')
            return False