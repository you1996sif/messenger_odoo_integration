/** @odoo-module */

import { ThreadField } from "@mail/core/common/thread_field";
import { patch } from "@web/core/utils/patch";

patch(ThreadField.prototype, {
    setup() {
        super.setup();
        this.startAutoRefresh();
    },

    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Set up auto-refresh every second
        this.refreshInterval = setInterval(() => {
            this.reloadThread();
        }, 1000);
    },

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        super.destroy();
    },

    reloadThread() {
        // Trigger thread reload
        this.props.reloadCallback?.();
    }
});