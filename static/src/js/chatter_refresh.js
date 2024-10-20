// // /** @odoo-module **/

// // import { FormController } from "@web/views/form/form_controller";
// // import { patch } from "@web/core/utils/patch";
// // import { useEffect } from "@odoo/owl";

// // patch(FormController.prototype, {
// //     setup(...args) {
// //         const originalSetup = FormController.prototype.setup;
// //         originalSetup.call(this, ...args);
        
// //         useEffect(() => {
// //             const chatter = this.el.querySelector('.o_Chatter');
// //             if (chatter) {
// //                 const onSendButtonClick = this.onSendButtonClick.bind(this);
// //                 chatter.addEventListener('click', onSendButtonClick);
// //                 return () => {
// //                     chatter.removeEventListener('click', onSendButtonClick);
// //                 };
// //             }
// //         });
// //     },

// //     onSendButtonClick(event) {
// //         if (event.target.closest('.o_Composer_buttonSend')) {
// //             setTimeout(() => {
// //                 if (this.model && this.model.root) {
// //                     this.model.root.load();
// //                 }
// //                 const chatter = this.el.querySelector('.o_Chatter');
// //                 if (chatter) {
// //                     const messageList = chatter.querySelector('.o_Chatter_scrollPanel');
// //                     if (messageList) {
// //                         messageList.scrollTop = messageList.scrollHeight;
// //                     }
// //                 }
// //             }, 500);
// //         }
// //     },
// // });

// /** @odoo-module **/

// import { registry } from "@web/core/registry";
// import { useEffect } from "@odoo/owl";
// import { useBus, useService } from "@web/core/utils/hooks";
// import { ChatterContainer } from "@mail/components/chatter/chatter_container";

// class AutoRefreshChatter extends ChatterContainer {
//     setup() {
//         super.setup();
        
//         this.orm = useService("orm");
//         this.messaging = useService("messaging");
        
//         useBus(this.messaging.bus, "discuss.channel/new_message", this.refreshChatter);
        
//         useEffect(() => {
//             const intervalId = setInterval(() => {
//                 this.refreshChatter();
//             }, 2000); // Refresh every 2 seconds
            
//             return () => clearInterval(intervalId);
//         });
//     }

//     async refreshChatter() {
//         if (this.chatter) {
//             await this.chatter.refresh();
//         }
//     }
// }

// registry.category("fields").add("auto_refresh_chatter", AutoRefreshChatter);

// export default AutoRefreshChatter;