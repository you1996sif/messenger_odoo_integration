/** @odoo-module **/

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";
import { useInterval } from "@web/core/utils/timing";
import { onWillDestroy } from "@odoo/owl";

patch(Chatter, {
    setup() {
        const _super = this._super.bind(this);
        _super(...arguments);
        
        if (this.props.record.resModel === 'facebook.user.conversation') {
            const interval = useInterval(() => {
                this.reloadThread();
            }, 1000);
            
            onWillDestroy(() => {
                if (interval) {
                    interval.clear();
                }
            });
        }
    },

    async reloadThread() {
        if (this.props.record) {
            await this.props.record.load();
            this.render();
        }
    }
});