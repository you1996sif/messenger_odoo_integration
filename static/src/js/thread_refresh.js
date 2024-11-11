/** @odoo-module **/

import { ThreadField } from "@mail/core/common/thread_field";
import { patch } from "@web/core/utils/patch";

patch(ThreadField.prototype, 'messenger_integration/static/src/js/thread_refresh.js', {
    setup() {
        this._super(...arguments);
        this.setupAutoRefresh();
    },

    setupAutoRefresh() {
        if (this.props.record.resModel === 'facebook.user.conversation') {
            this.startRefreshInterval();
        }
    },

    startRefreshInterval() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.refreshInterval = setInterval(() => {
            this.reloadMessages();
        }, 1000);
    },

    async reloadMessages() {
        if (this.threadService) {
            await this.threadService.fetchMessages();
        }
    },

    onWillDestroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this._super(...arguments);
    },
});