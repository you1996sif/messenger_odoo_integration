/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted } from "@odoo/owl";

export class MessageHandler extends Component {
    static template = "messenger_integration.MessageHandler";
    static props = { };

    setup() {
        this.messagingService = useService("messaging");
        this.busService = useService("bus_service");
        
        onWillStart(async () => {
            await this.messagingService.isReady;
        });
        
        onMounted(() => {
            this._setupMessageListeners();
        });
    }

    _setupMessageListeners() {
        this.busService.subscribe("mail.message/insert", this._onMessageUpdate.bind(this));
        this.busService.subscribe("mail.message/update", this._onMessageUpdate.bind(this));
    }

    _onMessageUpdate(payload) {
        if (payload && this.messagingService) {
            this.messagingService.refresh();
        }
    }
}