/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class MessageHandler extends Component {
    static template = "messenger_integration.MessageHandler";
    
    setup() {
        const messageBus = registry.category("services").get("bus_service");
        const rpc = registry.category("services").get("rpc");
        
        if (messageBus) {
            messageBus.subscribe("mail.message/insert", (message) => {
                this.refreshView();
            });
            
            messageBus.subscribe("mail.message/update", (message) => {
                this.refreshView();
            });
        }
    }

    refreshView() {
        // Force view refresh
        this.env.bus.trigger("REFRESH_VIEW");
    }
}

// Register the component
registry.category("main_components").add("MessageHandler", {
    Component: MessageHandler,
});

// Register a simpler service without messaging dependency
const messageHandlerService = {
    dependencies: ["bus_service", "rpc"],
    start(env, { bus_service, rpc }) {
        return {
            refresh() {
                env.bus.trigger("REFRESH_VIEW");
            },
        };
    },
};

registry.category("services").add("message_handler", messageHandlerService);