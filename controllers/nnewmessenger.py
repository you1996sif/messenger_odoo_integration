from datetime import datetime, timedelta
# from ..models.mail_mail import MailMail
from odoo import http, fields, api
import logging
from odoo.http import request, Response
import json
import urllib.parse
import requests
import re
import uuid
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

# Your Facebook verify token (ensure this is kept safe and matches the one used in your webhook setup)
vtoken = 'oYHb-#P.l.jZ#9iwF!g4Hhr7RRJtEL\?o8.\?=-|.If2W=A)fc-Q8EzX9@;V[sU:{iU5{WcyWxX*],@|@JjmK:bpRkr!pkxs29M;2X0z\JtO|.xi]yw5b@=*{7-1@Y-7#BprB|jP(fU-DSSrUl.:W.FGqZ/BV.y,'
access_token = 'EAAdiPcd2QOoBOwK9b5udNZCK1eTDtzZAmPFiMCZCZCCC88CbmfyTgooPq1H8BrOgP4rUQRcub5ZAT1plBstEzsdUiKDIIgAlZCLCoU0z0Bul1bRQtXYlsLwNFmdA9PJXDWXeXFiaAz1JrchKIVUe5tjG1Dn7cY5vz2W2qZAWxcWOlr1zc4pmoA7gDhi5u4CU9K4'

class FacebookWebhookController(http.Controller):
    @http.route('/privacy_policy', type='http', auth='public', website=True)
    def privacy_policy(self, **kwargs):
        """
        This endpoint serves the privacy policy page, which is required for Facebook apps.
        """
        return request.render('messenger_integration.privacy_policy_template')

    @http.route('/facebook_webhook', type='http', auth='public', methods=['POST', 'GET'], csrf=False)
    def facebook_webhook(self, **kwargs):
        """
        Main webhook endpoint. This method will handle both GET requests for verification
        and POST requests for receiving events.
        """
        try:
            if request.httprequest.method == 'GET':
                return self._handle_verification(kwargs)
            elif request.httprequest.method == 'POST':
                return self._handle_webhook_event()
        except Exception as e:
            _logger.exception(f'Error in facebook_webhook: {str(e)}')
            return Response("Internal Server Error", status=500)


    @http.route('/facebook/send_message', type='json', auth='user')
    def send_facebook_message_route(self, partner_id, message):
        _logger.info(f"Attempting to send Facebook message to partner {partner_id}: {message}")
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not partner.facebook_id:
            return False

        conversation = request.env['facebook.user.conversation'].sudo().create_or_update_conversation(partner.id)
        sent = self.send_facebook_message(partner_id, message)
        _logger.info('11111111111 sent sent sent sent sent')
        _logger.info( sent)


        if sent:
            _logger.info(' 222222222sent sent sent sent sent')
            conversation.add_message_to_chatter(message, 'odoo')
            return True
        else:
            _logger.error(f"Failed to send Facebook message to partner {partner_id}")
            return False
        
        
    @staticmethod
    def strip_html(text):
        return re.sub('<[^<]+?>', '', text)
    def _handle_verification(self, kwargs):
        """
        Handles the webhook verification when a GET request is received from Facebook.
        This is part of the Facebook app webhook setup process.
        """
        _logger.info('Received GET request for webhook verification')
        hub_mode = kwargs.get('hub.mode')
        token = kwargs.get('hub.verify_token')
        challenge = kwargs.get('hub.challenge')
        _logger.info(f'hub.mode: {hub_mode}, hub.verify_token: {token}, hub.challenge: {challenge}')

        # Verify token and respond with the challenge if everything matches
        if hub_mode == 'subscribe' and token == urllib.parse.unquote(vtoken):
            _logger.info('Webhook verified successfully')
            return challenge
        else:
            _logger.warning('Webhook verification failed')
            return Response("Failed verification", status=403)

    def _handle_webhook_event(self):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            _logger.info(f'Received data: {data}')

            for entry in data.get('entry', []):
                _logger.info(f'entry: {entry}')
                self._process_entry(entry)
                

            _logger.info('returning 200:')
            # MailMail.reload_page()
            # request.env['mail.mail'].sudo().reload_page()
            
            return Response("OK", status=200)
        
        except Exception as e:
            _logger.exception(f'Error in _handle_webhook_event: {str(e)}')
            return Response("Internal Server Error", status=500)


    def _process_entry(self, entry):
        """
        Processes each entry in the webhook event.
        Each entry can contain multiple types of events (messages, changes, etc.).
        """
        if 'changes' in entry:
            _logger.info('changes')
            
            for change in entry['changes']:
                field = change.get('field')
                value = change.get('value')
                if field:
                    method_name = f'_handle_{field}'
                    if hasattr(self, method_name):
                    
                        getattr(self, method_name)(value)
                    else:
                        _logger.warning(f'No handler for field: {field}')

        if 'messaging' in entry:
            _logger.info('messagingggggggggggg')
            for event in entry['messaging']:
                self._handle_messaging_event(event)

    def _handle_messaging_event(self, event):
        """
        Handles messaging-related events like messages, postbacks, delivery confirmations, and read receipts.
        """
        _logger.info('_handle_messaging_eventtttttttttt')
        if 'message' in event:
            self._handle_messages(event)
            _logger.info("'message'in event:")
        elif 'postback' in event:
            _logger.info(" elif 'postback' in event:")
            self._handle_messaging_postbacks(event)
        elif 'delivery' in event:
            _logger.info(" eelif 'delivery' in event:")
            self._handle_message_deliveries(event)
        elif 'read' in event:
            _logger.info("elif 'read' in event:")
            self._handle_message_reads(event)

    def _handle_messages(self, event):
        """
        Handles incoming messages from Facebook webhook.
        """
        try:
            message = event.get('message', {})
            sender_id = event['sender']['id']
            
            # Skip if message is from our page
            if sender_id == '110208201788618':  # Your page ID
                return True
                
            message_id = message.get('mid')
            text = message.get('text', '')
            
            if not message_id or not text:
                _logger.info('Skipping message without ID or text')
                return True

            _logger.info('Processing message: %s from %s', message_id, sender_id)
            
            user_profile = self._get_user_profile(sender_id)
            partner = self._get_or_create_partner(user_profile)
            conversation = request.env['facebook.user.conversation'].sudo().create_or_update_conversation(partner.id)
            
            clean_message = self.strip_html(text)
            if clean_message:
                conversation.with_context(from_facebook=True).add_message_to_chatter(
                    clean_message, 
                    'customer', 
                    message_id
                )
                
            return True
            
        except Exception as e:
            _logger.error("Error processing Facebook message: %s", str(e))
            return False

    def _get_or_create_partner(self, user_profile):
        Partner = request.env['res.partner'].sudo()
        partner = Partner.search([('facebook_id', '=', user_profile['id'])], limit=1)
        if not partner:
            partner = Partner.create({
                'name': user_profile.get('name', 'Facebook User'),
                'facebook_id': user_profile['id'],
                'email': user_profile.get('email'),
            })
        return partner


    def _get_user_profile(self, sender_id):
        """
        Fetches user profile information from Facebook.
        You'll need to implement this method using Facebook's Graph API.
        """
        # TODO: Implement Facebook Graph API call to get user profile
        # For now, we'll return a dummy profile
        return {
            'id': sender_id,
            'email': f'{sender_id}@example.com',
            'name': f'User {sender_id}',
        }

    def _create_new_partner(self, user_profile):
        """
        Creates a new partner in Odoo based on the user profile from Facebook.
        """
        return request.env['res.partner'].sudo().create({
            'name': user_profile.get('name'),
            'email': user_profile.get('email'),
            'facebook_id': user_profile.get('id'),
        })

    def _send_message_to_chatter(self, partner, message_text):
        """
        Sends a message to the partner's Chatter in Odoo.
        """
        message_text = self.strip_html(message_text)
       
        partner.message_post(body=message_text, message_type='comment')

    def _handle_messaging_postbacks(self, event):
        """
        Handles postback events from the Facebook webhook, which are triggered by user interactions with buttons in Messenger.
        """
        postback = event['postback']
        sender_id = event['sender']['id']
        _logger.info(f'Received postback: {postback} from {sender_id}')
        # Here you can process the postback, and store data if necessary
        # For example, log the postback payload or trigger some action

    def _handle_message_deliveries(self, event):
        """
        Handles message delivery confirmations from Facebook, indicating that the message was delivered.
        """
        delivery = event['delivery']
        _logger.info(f'Received delivery receipt: {delivery}')
        # Implement logic to handle message deliveries if needed

    def _handle_message_reads(self, event):
        """
        Handles message read receipts, indicating that the user has read the message.
        """
        read = event['read']
        # Implement logic to handle message read receipts if needed

    # def send_facebook_message(self, partner_id, message, env=None):
    #     if env is None:
    #         env = request.env
    #     if env.context.get('from_facebook'):
    #         _logger.info(f"Skipping send for incoming message: {message}")
    #         return True
    #     partner = env['res.partner'].sudo().browse(partner_id)
    #     if not partner.facebook_id:
    #         _logger.error(f"No Facebook ID found for partner {partner_id}")
    #         return False
        
    #     clean_message = self.strip_html(message)
        
    #     if not clean_message:
    #         _logger.warning(f"Attempted to send empty message to partner {partner_id}")
    #         return False
        
    #     existing_message = env['facebook_conversation'].sudo().search([
    #         ('partner_id', '=', partner_id),
    #         ('message', '=', clean_message),
    #         ('sender', '=', 'odoo')
    #     ], limit=1)
        
    #     if existing_message:
    #         _logger.info(f"Message already sent to partner {partner_id}: {clean_message}")
    #         return True
    #     _logger.info(f"Attempting to send message to partner {partner_id}: {clean_message}")
    #     partner = env['res.partner'].sudo().browse(partner_id)
    #     if not partner.facebook_id:
    #         _logger.error(f"No Facebook ID found for partner {partner_id}")
    #         return False

    #     # Your Facebook page access token
    #     message_id = str(uuid.uuid4())
    #     url = f'https://graph.facebook.com/v11.0/me/messages?access_token={access_token}'
    #     payload = {
    #         'recipient': {'id': partner.facebook_id},
    #         'message': {'text': message},
    #         'metadata': message_id
    #     }
    #     response = requests.post(url, json=payload)
    #     if response.status_code == 200:
    #         try:
    #             conversation = env['facebook.user.conversation'].sudo().create_or_update_conversation(partner.id)
    #             env['facebook_conversation'].sudo().create({
    #                 'user_conversation_id': conversation.id,
    #                 'partner_id': partner.id,
    #                 'message': clean_message,
    #                 'sender': 'odoo',
    #                 'odoo_user_id': env.user.id,
    #                 'message_type': 'comment',
    #                 'message_id': message_id,
    #             })
    #             # Update the last_message_date of the conversation
    #             conversation.sudo().write({'last_message_date': fields.Datetime.now()})
    #             env.cr.commit()  # Commit the transaction
    #             return True
    #         except Exception as e:
    #             _logger.error(f"Error creating Facebook message: {str(e)}")
    #             env.cr.rollback()  # Rollback the transaction in case of error
    #             return False
    #     else:
    #         _logger.error(f"Failed to send Facebook message: {response.text}")
    #         return False
    
    def _check_messaging_window(self, partner_id):
        """
        Check if we can send a message based on Facebook's messaging window policy.
        Returns (bool, str) - (can_send, policy_type)
        """
        # Get the last interaction from this user
        last_message = self.env['facebook_conversation'].search([
            ('partner_id', '=', partner_id),
            ('sender', '=', 'customer')
        ], order='create_date desc', limit=1)

        if last_message:
            # 24-hour standard messaging window
            last_interaction = fields.Datetime.from_string(last_message.create_date)
            window_end = last_interaction + timedelta(hours=24)
            
            if datetime.now() <= window_end:
                return True, 'standard'

        # Check if we have a valid tag for message outside window
        return self._check_message_tags(partner_id)

    def _check_message_tags(self, partner_id):
        """
        Check if we can send a message using one of Facebook's allowed tags
        Returns (bool, str) - (can_send, tag_type)
        """
        partner = self.env['res.partner'].browse(partner_id)
        
        # Check for active order - CONFIRMED_EVENT_UPDATE tag
        active_order = self.env['sale.order'].search([
            ('partner_id', '=', partner_id),
            ('state', 'in', ['sale', 'done']),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=30))
        ], limit=1)
        
        if active_order:
            return True, 'CONFIRMED_EVENT_UPDATE'

        # Check for customer service issue - CUSTOMER_FEEDBACK tag
        active_ticket = self.env['helpdesk.ticket'].search([
            ('partner_id', '=', partner_id),
            ('stage_id.is_close', '=', False)
        ], limit=1)
        
        if active_ticket:
            return True, 'CUSTOMER_FEEDBACK'

        return False, None
    
    
    def __init__(self):
        super().__init__()
        self.env = request.env if request else None
        

    def send_facebook_message(self, recipient_id, message_text, env=None):
        """
        Send message to Facebook Messenger
        """
        if env:
            self.env = env
        
        if not self.env:
            raise ValueError("No Odoo environment available")
            
        try:
            # Get the page access token from system parameters
            page_access_token = self.env['ir.config_parameter'].sudo().get_param('facebook_page_access_token')
            page_access_token = access_token
            
            if not page_access_token:
                _logger.error("Facebook page access token not found")
                return False

            url = f"https://graph.facebook.com/v18.0/me/messages"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                'recipient': {'id': recipient_id},
                'message': {'text': message_text},
                'access_token': page_access_token
            }
            
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()
            
            if response.status_code != 200:
                _logger.error(f"Failed to send Facebook message: {response_data}")
                return False
                
            return True
            
        except Exception as e:
            _logger.error(f"Failed to send Facebook message: {str(e)}")
            return False

        # conversation = env['facebook.user.conversation'].sudo().create_or_update_conversation(partner.id)
        # env['facebook_conversation'].sudo().create({
        #     'user_conversation_id': conversation.id,
        #     'message': message,
        #     'sender': 'odoo',
        #     'odoo_user_id': env.user.id,
        #     'message_type': 'comment',
        # })
        # conversation.message_post(body=message, message_type='comment', subtype_xmlid='mail.mt_comment')
        

        # if response.status_code == 200:
        #     conversation = env['facebook.user.conversation'].sudo().create_or_update_conversation(partner.id)
        #     # Message sent successfully, create a record in our conversation model
        #     request.env['facebook_conversation'].sudo().with_context(from_facebook=True).create({
        #         'partner_id': partner.id,
        #         'message': message,
        #         'sender': 'odoo',
        #         'odoo_user_id': request.env.user.id,
        #         'user_conversation_id': conversation.id,
        #         'message_type': 'comment',
        #     })
        #     conversation.sudo().write({'last_message_date': fields.Datetime.now()})
        #     # conversation.message_post(body=message, message_type='comment', subtype_xmlid='mail.mt_comment')
        #     return True
        # else:
        #     _logger.error(f"Failed to send Facebook message: {response.text}")
        #     return False
            
        # Your Facebook page access token

    
        # conversation = env['facebook.user.conversation'].sudo().create_or_update_conversation(partner.id)
        # env['facebook_conversation'].sudo().create({
        #     'user_conversation_id': conversation.id,
        #     'message': message,
        #     'sender': 'odoo',
        #     'odoo_user_id': env.user.id,
        #     'message_type': 'comment',
        # })
        # conversation.message_post(body=message, message_type='comment', subtype_xmlid='mail.mt_comment')
      
