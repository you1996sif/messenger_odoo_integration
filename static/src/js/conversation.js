/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ChatterContainer } from "@mail/components/chatter_container/chatter_container";
import { useService } from "@web/core/utils/hooks";

patch(ChatterContainer.prototype, {
    setup() {
        this._super(...arguments);
        
        // Get required services
        this.rpc = useService("rpc");
        this.bus = useService("bus_service");
        
        // Subscribe to message updates
        this.bus.subscribe("mail.message/insert", this.onMessageUpdate.bind(this));
        this.bus.subscribe("mail.message/update", this.onMessageUpdate.bind(this));
    },

    onMessageUpdate(notification) {
        if (this.chatter && this.chatter.thread) {
            this.chatter.thread.fetchData();
        }
    },

    async sendMessage(messageData) {
        const result = await this._super(...arguments);
        // Force refresh after message is sent
        if (this.chatter && this.chatter.thread) {
            await this.chatter.thread.fetchData();
        }
        return result;
    }
});