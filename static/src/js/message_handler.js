/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted } from "@odoo/owl";

export class MessageHandler extends Component {
    static template = "messenger_integration.MessageHandler";

    setup() {
        this.threadService = useService("thread_service");
        this.bus = useService("bus_service");
        
        onMounted(() => {
            this.bus.subscribe("mail.message/insert", (payload) => {
                if (payload && this.threadService) {
                    this.threadService.refresh();
                }
            });
            
            this.bus.subscribe("mail.message/update", (payload) => {
                if (payload && this.threadService) {
                    this.threadService.refresh();
                }
            });
        });
    }
}