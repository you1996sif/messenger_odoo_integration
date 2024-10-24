/** @odoo-module **/

import { registry } from "@web/core/registry";
import { MessageHandler } from "../components/message_handler/message_handler";

// Register the main component
registry.category("main_components").add("MessageHandler", {
    Component: MessageHandler,
});

// Simplified service registration
const messageHandlerService = {
    dependencies: ["bus_service", "messaging"],
    
    start(env, { bus_service, messaging }) {
        return {
            async refresh() {
                if (messaging.modelManager) {
                    await messaging.modelManager.messagingCreated;
                    messaging.refresh();
                }
            },
        };
    },
};

// Add service to registry
registry.category("services").add("message_handler", messageHandlerService);