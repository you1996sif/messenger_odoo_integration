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

/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { useEffect } from "@odoo/owl";

class AutoRefreshFormController extends FormController {
    setup() {
        super.setup();
        
        this.autoRefreshInterval = 2000; // 2 seconds
        this.autoRefreshIntervalId = null;

        useEffect(() => {
            console.log('AutoRefreshFormController mounted');
            this.startAutoRefresh();
            return () => {
                console.log('AutoRefreshFormController will unmount');
                this.stopAutoRefresh();
            };
        });
    }

    startAutoRefresh() {
        console.log('Starting auto-refresh');
        if (!this.autoRefreshIntervalId) {
            this.autoRefreshIntervalId = setInterval(() => {
                console.log('Auto-refreshing');
                this.refreshChatter();
            }, this.autoRefreshInterval);
        }
    }

    stopAutoRefresh() {
        console.log('Stopping auto-refresh');
        if (this.autoRefreshIntervalId) {
            clearInterval(this.autoRefreshIntervalId);
            this.autoRefreshIntervalId = null;
        }
    }

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
    }
}

// Define the new form view
const autoRefreshFormView = {
    ...formView,
    Controller: AutoRefreshFormController,
};

// Register the new form view
registry.category("views").add("auto_refresh_form", autoRefreshFormView);

// Patch the original FormController for backwards compatibility
patch(FormController.prototype, AutoRefreshFormController.prototype);