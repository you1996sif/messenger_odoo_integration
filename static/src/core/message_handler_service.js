/** @odoo-module **/

import { registry } from "@web/core/registry";
import { MessageHandler } from "../components/message_handler/message_handler";
import { multiTabService } from "@web/core/multi_tab_service";

// Register the main component
registry.category("main_components").add("MessageHandler", {
    Component: MessageHandler,
});

// Register the service with correct dependencies
const messageHandlerService = {
    dependencies: ["bus_service", "messaging"],
    start(env, { bus_service, messaging }) {
        return {
            refresh() {
                messaging.refresh();
            },
        };
    },
};

registry.category("services").add("message_handler", messageHandlerService);