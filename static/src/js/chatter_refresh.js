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


import { patch } from '@web/core/utils/patch';
import { ChatterContainer } from '@mail/components/chatter_container/chatter_container';

patch(ChatterContainer.prototype, 'ChatterAutoRefresh', {
    setup() {
        this._super(...arguments);
        this.intervalId = null;
    },

    mounted() {
        this._super(...arguments);
        this.startAutoRefresh();
    },

    willUnmount() {
        this._super(...arguments);
        this.stopAutoRefresh();
    },

    startAutoRefresh() {
        this.intervalId = setInterval(() => {
            this.refreshChatter();
        }, 2000); // Refresh every 2 seconds
    },

    stopAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
    },

    async refreshChatter() {
        if (this.chatter) {
            await this.chatter.refresh();
        }
    }
});