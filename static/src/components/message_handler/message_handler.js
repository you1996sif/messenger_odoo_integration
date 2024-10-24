/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart } from "@odoo/owl";

export class MessageHandler extends Component {
    static template = "messenger_integration.MessageHandler";
    static props = {};

    setup() {
        // Properly get services using useService
        this.busService = useService("bus_service");
        this.rpc = useService("rpc");
        this.orm = useService("orm");

        onWillStart(() => {
            // Set up bus subscriptions
            this._setupBusSubscriptions();
        });
    }

    _setupBusSubscriptions() {
        if (this.busService) {
            this.busService.addChannel('mail.message/insert');
            this.busService.addChannel('mail.message/update');
            
            this.busService.addEventListener('notification', ({ detail: notifications }) => {
                for (const { payload, type } of notifications) {
                    if (type === 'mail.message/insert' || type === 'mail.message/update') {
                        this._handleMessageNotification(payload);
                    }
                }
            });
        }
    }

    _handleMessageNotification(payload) {
        if (payload && this.env.services.action) {
            // Trigger view refresh
            this.env.services.action.doAction({
                type: 'ir.actions.client',
                tag: 'reload',
            });
        }
    }
}

// Register the component
registry.category("main_components").add("MessageHandler", {
    Component: MessageHandler,
});