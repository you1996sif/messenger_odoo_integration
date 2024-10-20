// /** @odoo-module **/

// import { FormController } from "@web/views/form/form_controller";
// import { patch } from "@web/core/utils/patch";
// import { useEffect } from "@odoo/owl";

// patch(FormController.prototype, {
//     setup(...args) {
//         const originalSetup = FormController.prototype.setup;
//         originalSetup.call(this, ...args);
        
//         useEffect(() => {
//             const chatter = this.el.querySelector('.o_Chatter');
//             if (chatter) {
//                 const onSendButtonClick = this.onSendButtonClick.bind(this);
//                 chatter.addEventListener('click', onSendButtonClick);
//                 return () => {
//                     chatter.removeEventListener('click', onSendButtonClick);
//                 };
//             }
//         });
//     },

//     onSendButtonClick(event) {
//         if (event.target.closest('.o_Composer_buttonSend')) {
//             setTimeout(() => {
//                 if (this.model && this.model.root) {
//                     this.model.root.load();
//                 }
//                 const chatter = this.el.querySelector('.o_Chatter');
//                 if (chatter) {
//                     const messageList = chatter.querySelector('.o_Chatter_scrollPanel');
//                     if (messageList) {
//                         messageList.scrollTop = messageList.scrollHeight;
//                     }
//                 }
//             }, 500);
//         }
//     },
// });

/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";

patch(FormController.prototype, 'AutoRefreshFormController', {
    setup() {
        this._super(...arguments);
        this.autoRefreshInterval = 2000; // 2 seconds
        this.autoRefreshIntervalId = null;
        this.env.bus.on('ROUTE_CHANGE', this, this.stopAutoRefresh);
        this.env.bus.on('FORM_VIEW_RENDERED', this, this.startAutoRefresh);
    },

    startAutoRefresh() {
        if (!this.autoRefreshIntervalId) {
            this.autoRefreshIntervalId = setInterval(() => {
                this.refreshChatter();
            }, this.autoRefreshInterval);
        }
    },

    stopAutoRefresh() {
        if (this.autoRefreshIntervalId) {
            clearInterval(this.autoRefreshIntervalId);
            this.autoRefreshIntervalId = null;
        }
    },

    refreshChatter() {
        if (this.model && this.model.root) {
            this.model.root.load();
            const chatter = this.el.querySelector('.o_Chatter');
            if (chatter) {
                const messageList = chatter.querySelector('.o_Chatter_scrollPanel');
                if (messageList) {
                    messageList.scrollTop = messageList.scrollHeight;
                }
            }
        }
    },

    destroy() {
        this.stopAutoRefresh();
        this.env.bus.off('ROUTE_CHANGE', this, this.stopAutoRefresh);
        this.env.bus.off('FORM_VIEW_RENDERED', this, this.startAutoRefresh);
        this._super(...arguments);
    },
});

// Extend the form view to use our patched FormController
const autoRefreshFormView = {
    ...formView,
    Controller: FormController,
};

// Register the new form view
registry.category("views").add("auto_refresh_form", autoRefreshFormView);