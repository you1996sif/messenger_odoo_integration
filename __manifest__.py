# -*- coding: utf-8 -*-
{
    'name': 'asd Messenger Integration',
    'version': '1.0',
    'category': 'Discuss',
    'summary': 'Integrate Facebook Messenger with Odoo',
    'description': """
      This module integrates Facebook Messenger with Odoo,
      allowing you to communicate with customers directly from Odoo.
  """,
  'author': 'Yousif Basil',
    'website': "https://www.yourcompany.com",

    'depends': ['base', 'web', 'contacts', 'mail','sale'],
   
    'data': [
        'security/ir.model.access.csv',
        'views/message_views.xml',
        'views/privacy_policy_templates.xml',
        'views/facebook_conversation_views.xml',
        'views/facebook_user_conversation_views.xml',
        # 'views/helpdesk_ticket_views.xml',
        'wizards/create_sale_order_wizard_views.xml',
       
        

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
  
}

