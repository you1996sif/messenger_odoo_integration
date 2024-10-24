/** @odoo-module **/

import { registry } from "@web/core/registry";

export const messageService = {
    dependencies: ["bus_service", "orm"],
    
    start(env, { bus_service, orm }) {
        return {
            setup() {
                // Service setup logic
            },
            async refresh() {
                // Refresh logic
                await orm.call('bus.bus', 'trigger_refresh');
            },
        };
    },
};

registry.category("services").add("message_service", messageService);