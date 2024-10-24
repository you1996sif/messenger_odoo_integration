/** @odoo-module **/

import { registry } from "@web/core/registry";
import { MessageHandler } from "../components/message_handler/message_handler";

// Register the main component
registry.category("main_components").add("MessageHandler", {
    Component: MessageHandler,
    props: {},  // Add any props if needed
});

// Register a service if needed
const messageHandlerService = {
    dependencies: ["bus_service", "thread_service"],
    start(env, { bus_service, thread_service }) {
        return {
            refresh() {
                thread_service.refresh();
            },
        };
    },
};

registry.category("services").add("message_handler", messageHandlerService);