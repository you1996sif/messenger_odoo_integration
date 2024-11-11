/** @odoo-module **/

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";
import { useInterval } from "@web/core/utils/timing";
import { onWillDestroy } from "@odoo/owl";

patch(Chatter.prototype, 'messenger_integration.ChatterRefresh', {
    setup() {
        super.setup();
        
        const refreshInterval = useInterval(() => {
            if (this.props.record.resModel === 'facebook.user.conversation') {
                this.reloadThread();
            }
        }, 1000);
        
        onWillDestroy(() => {
            if (refreshInterval) {
                refreshInterval.clear();
            }
        });
    },

    async reloadThread() {
        await this.props.record.load();
        this.render();
    }
});