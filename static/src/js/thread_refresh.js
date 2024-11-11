/** @odoo-module */

import { ThreadController } from "@mail/core/common/thread_controller";
import { patch } from "@web/core/utils/patch";
import { onWillDestroy } from "@odoo/owl";

patch(ThreadController.prototype, 'messenger_integration.ThreadRefresh', {
    setup() {
        super.setup();
        
        if (this.props.threadModel === 'facebook.user.conversation') {
            this.startAutoRefresh();
        }
        
        onWillDestroy(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
        });
    },

    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            if (this.threadService) {
                this.threadService.refresh();
            }
        }, 1000);
    },
});