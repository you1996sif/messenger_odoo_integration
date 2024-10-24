/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useBus } from "@web/core/utils/hooks";
import { Component, onMounted, useState } from "@odoo/owl";

export class FacebookConversationHandler extends Component {
    setup() {
        this.state = useState({
            messages: [],
        });
        
        this.busService = useService("bus_service");
        this.orm = useService("orm");
        this.messagingService = useService("messaging");
        
        onMounted(() => {
            this.busService.subscribe("mail.message/insert", (payload) => {
                this.handleNewMessage(payload);
            });
            
            this.busService.subscribe("mail.message/update", (payload) => {
                this.handleMessageUpdate(payload);
            });
        });
    }

    handleNewMessage(payload) {
        if (payload.type === "message_posted") {
            // Trigger a reload of the view
            this.messagingService.refresh();
        }
    }

    handleMessageUpdate(payload) {
        if (payload.type === "message_updated") {
            // Refresh messaging when message is updated
            this.messagingService.refresh();
        }
    }
}

FacebookConversationHandler.template = "messenger_integration.FacebookConversationHandler";

// Register the component
registry.category("main_components").add("FacebookConversationHandler", {
    Component: FacebookConversationHandler,
});