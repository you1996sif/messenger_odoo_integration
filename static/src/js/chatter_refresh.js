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


import { useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export function useAutoRefresh(refreshInterval = 2000) {
    const orm = useService("orm");

    useEffect(() => {
        const intervalId = setInterval(() => {
            console.log('Auto-refreshing');
            orm.call("mail.message", "get_messages", [], {
                // You might need to adjust these parameters based on your needs
                model: this.props.resModel,
                res_id: this.props.resId,
                limit: 100,
            }).then((messages) => {
                // Update the messages in the chatter
                // This part depends on how your chatter is implemented
                // You might need to dispatch an action or update the state
                console.log('Received new messages:', messages);
            });
        }, refreshInterval);

        return () => {
            clearInterval(intervalId);
        };
    });
}