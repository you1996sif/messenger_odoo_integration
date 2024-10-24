/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { Component, onMounted } from "@odoo/owl";

export class MessageHandler extends Component {
    static template = "messenger_integration.MessageHandler";
    static props = {};

    setup() {
        this.busService = useService("bus_service");
        this.rpc = useService("rpc");
        
        onMounted(() => {
            this._setupListeners();
        });
    }

    _setupListeners() {
        this.busService.subscribe("mail.message/insert", this._onMessageUpdate.bind(this));
        this.busService.subscribe("mail.message/update", this._onMessageUpdate.bind(this));
    }

    _onMessageUpdate() {
        this.env.bus.trigger("REFRESH_VIEW");
    }
}