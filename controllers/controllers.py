# -*- coding: utf-8 -*-
# from odoo import http


# class MessengerIntegration(http.Controller):
#     @http.route('/messenger_integration/messenger_integration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/messenger_integration/messenger_integration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('messenger_integration.listing', {
#             'root': '/messenger_integration/messenger_integration',
#             'objects': http.request.env['messenger_integration.messenger_integration'].search([]),
#         })

#     @http.route('/messenger_integration/messenger_integration/objects/<model("messenger_integration.messenger_integration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('messenger_integration.object', {
#             'object': obj
#         })

