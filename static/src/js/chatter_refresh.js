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

import { useState, useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

function useAutoRefresh(refreshInterval = 2000) {
    const orm = useService("orm");
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        const intervalId = setInterval(async () => {
            const fetchedMessages = await orm.call(
                "facebook_conversation",
                "search_read",
                [[["user_conversation_id", "=", this.props.resId]]],
                { fields: ["date", "sender", "message"], limit: 100, order: "date desc" }
            );
            setMessages(fetchedMessages);
        }, refreshInterval);

        return () => clearInterval(intervalId);
    });

    return messages;
}

patch(FormController.prototype, {
    setup() {
        this._super(...arguments);
        if (this.props.resModel === 'facebook.user.conversation') {
            this.messages = useAutoRefresh.call(this);
        }
    },
});