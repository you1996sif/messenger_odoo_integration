/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class FacebookConversationHandler extends Component {
    setup() {
        // Get the messaging bus service from the env
        const bus = this.env.services.bus_service;
        const messaging = this.env.services.messaging;

        // Subscribe to message notifications
        bus.subscribe("mail.message/insert", (payload) => {
            if (payload && payload.type === "message_posted") {
                messaging.refresh();
            }
        });

        bus.subscribe("mail.message/update", (payload) => {
            if (payload && payload.type === "message_updated") {
                messaging.refresh();
            }
        });
    }
}

FacebookConversationHandler.template = "messenger_integration.FacebookConversationHandler";

// Register the component
registry.category("main_components").add("FacebookConversationHandler", FacebookConversationHandler);