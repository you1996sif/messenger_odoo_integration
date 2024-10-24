/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted } from "@odoo/owl";

export class MessageHandler extends Component {
    static template = "messenger_integration.MessageHandler";
    static props = {};

    setup() {
        this.messaging = useService("messaging");
        this.bus = useService("bus_service");
        
        onWillStart(async () => {
            await this.messaging.isReady;
        });
        
        onMounted(() => {
            this._subscribeToBus();
        });
    }

    _subscribeToBus() {
        this.bus.subscribe("mail.message/insert", (payload) => {
            if (payload) {
                this.messaging.refresh();
            }
        });
        
        this.bus.subscribe("mail.message/update", (payload) => {
            if (payload) {
                this.messaging.refresh();
            }
        });
    }
}