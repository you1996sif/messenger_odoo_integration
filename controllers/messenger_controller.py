from odoo import http
import logging
from odoo.http import request, Response
import json
import urllib.parse

_logger = logging.getLogger(__name__)

# Your Facebook verify token (ensure this is kept safe and matches the one used in your webhook setup)
vtoken = 'oYHb-#P.l.jZ#9iwF!g4Hhr7RRJtEL\?o8.\?=-|.If2W=A)fc-Q8EzX9@;V[sU:{iU5{WcyWxX*],@|@JjmK:bpRkr!pkxs29M;2X0z\JtO|.xi]yw5b@=*{7-1@Y-7#BprB|jP(fU-DSSrUl.:W.FGqZ/BV.y,'

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
        Processes each entry in the webhook event. Each entry can contain multiple types of events (messages, changes, etc.).
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
        Handles incoming messages from the Facebook webhook and stores them in the `messenger_message` model.
        """
        message = event['message']
        sender_id = event['sender']['id']
        _logger.info(f'Received message: {message} from {sender_id}')
        
        # Create a new message record in the `messenger_message` model
        request.env['messenger_message'].sudo().create({
            'name': message.get('mid'),
            'text': message.get('text', ''),  # Store the message text, or empty if not available
            'sender_id': sender_id,
        })

    def _handle_messaging_postbacks(self, event):
        """
        Handles postback events from the Facebook webhook, which are triggered by user interactions
        with buttons in Messenger.
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
        _logger.info(f'Received read receipt: {read}')
        # Implement logic to handle message read receipts if needed

