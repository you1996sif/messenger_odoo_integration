odoo.define('messenger_integration.Conversation', function (require) {
    "use strict";

    var core = require('web.core');
    var BasicController = require('web.BasicController');
    var session = require('web.session');

    BasicController.include({
        _pushMessage: function (message) {
            var self = this;
            this._super.apply(this, arguments);
            
            // Handle new message notifications
            self.call('bus_service', 'addChannel', 'mail.message');
            self.call('bus_service', 'onNotification', self, function (notifications) {
                notifications.forEach(function (notification) {
                    if (notification[0] === 'mail.message/insert') {
                        self.trigger_up('reload');
                    }
                });
            });
        },
    });
});