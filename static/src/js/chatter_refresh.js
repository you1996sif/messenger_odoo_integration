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
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";

function useAutoRefresh(refreshInterval = 2000) {
    const orm = useService("orm");

    useEffect(() => {
        const intervalId = setInterval(() => {
            console.log('Auto-refreshing');
            orm.call("mail.message", "get_messages", [], {
                model: this.props.resModel,
                res_id: this.props.resId,
                limit: 100,
            }).then((messages) => {
                console.log('Received new messages:', messages);
                // Here you would update the messages in your UI
            });
        }, refreshInterval);

        return () => {
            clearInterval(intervalId);
        };
    });
}

patch(FormController.prototype, {
    setup() {
        this._super(...arguments);
        useAutoRefresh.call(this);
    },
});

export const AutoRefreshFormView = {
    ...formView,
    Controller: FormController,
};

registry.category("views").add("auto_refresh_form", AutoRefreshFormView);