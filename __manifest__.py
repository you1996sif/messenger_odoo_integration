# -*- coding: utf-8 -*-
{
    'name': 'Messenger Integration',
    'version': '1.0',
    'category': 'Social',
    'summary': 'Integrate Facebook Messenger with Odoo',
    'description': """
      This module integrates Facebook Messenger with Odoo,
      allowing you to communicate with customers directly from Odoo.
  """,
  'author': 'Yousif Basil',
    'website': "https://www.yourcompany.com",

    'depends': ['base', 'web', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/message_views.xml',
        'views/privacy_policy_templates.xml',
        'views/facebook_conversation_views.xml',
'views/facebook_user_conversation_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
  
}

