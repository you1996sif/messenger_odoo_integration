from odoo import http
import logging
from odoo.http import request, Response
import json
import urllib.parse
import requests

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
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not partner.facebook_id:
            return False

        # Your Facebook page access token
        # access_token = request.env['ir.config_parameter'].sudo().get_param('facebook.page_access_token')

        url = f'https://graph.facebook.com/v11.0/me/messages?access_token={access_token}'
        payload = {
            'recipient': {'id': partner.facebook_id},
            'message': {'text': message}
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return True
        else:
            _logger.error(f"Failed to send Facebook message: {response.text}")
            return False

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
        """
        Handles incoming POST requests from Facebook, containing webhook events (messages, postbacks, etc.).
        """
        _logger.info('Received POST request with webhook data')
        data = json.loads(request.httprequest.data.decode('utf-8'))
        _logger.info(f'Received data: {data}')

        # Loop through all the entries in the webhook data
        for entry in data.get('entry', []):
            self._process_entry(entry)

        return 'Success'

    def _process_entry(self, entry):
        """
        Processes each entry in the webhook event.
        Each entry can contain multiple types of events (messages, changes, etc.).
        """
        if 'changes' in entry:
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
            for event in entry['messaging']:
                self._handle_messaging_event(event)

    def _handle_messaging_event(self, event):
        """
        Handles messaging-related events like messages, postbacks, delivery confirmations, and read receipts.
        """
        if 'message' in event:
            self._handle_messages(event)
        elif 'postback' in event:
            self._handle_messaging_postbacks(event)
        elif 'delivery' in event:
            self._handle_message_deliveries(event)
        elif 'read' in event:
            self._handle_message_reads(event)

    def _handle_messages(self, event):
        """
        Handles incoming messages from the Facebook webhook, checks if the customer exists,
        and either communicates via Chatter or adds a new partner.
        """
        message = event['message']
        sender_id = event['sender']['id']
        _logger.info(f'Received message: {message} from {sender_id}')

        # Fetch user profile information from Facebook
        user_profile = self._get_user_profile(sender_id)
        email = user_profile.get('email')
      

        if email:
          
            # Check if the customer exists
            partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)

            if partner:
                # Customer exists, communicate via Chatter
                self._send_message_to_chatter(partner, message['text'])
            else:
                # Customer doesn't exist, create a new partner
                partner = self._create_new_partner(user_profile)
                self._send_message_to_chatter(partner, message['text'])
        # Store the message in the `messenger_message` model
            request.env['facebook_conversation'].sudo().create_from_facebook(partner, message['text'])
       
        
        request.env['messenger_message'].sudo().create({
            'name': message.get('mid'),
            'text': message.get('text', ''),
            'sender_id': sender_id,
        })

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
        
    def send_facebook_message(self, partner_id, message):
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not partner.facebook_id:
            return False

        # Your Facebook page access token
       
        url = f'https://graph.facebook.com/v11.0/me/messages?access_token={access_token}'
        payload = {
            'recipient': {'id': partner.facebook_id},
            'message': {'text': message}
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            # Message sent successfully, create a record in our conversation model
            request.env['facebook_conversation'].sudo().create({
                'partner_id': partner.id,
                'message': message,
                'sender': 'odoo',
                'odoo_user_id': request.env.user.id,
            })
            return True
        else:
            _logger.error(f"Failed to send Facebook message: {response.text}")
            return False
