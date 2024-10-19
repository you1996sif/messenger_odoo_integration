/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { patch } from "@web/core/utils/patch";
import { useEffect } from "@odoo/owl";

patch(FormController.prototype, {
    setup() {
        this._super(...arguments);
        
        useEffect(() => {
            const chatter = this.el.querySelector('.o_Chatter');
            if (chatter) {
                chatter.addEventListener('click', this.onSendButtonClick.bind(this));
            }
        });
    },

    onSendButtonClick(event) {
        if (event.target.closest('.o_Composer_buttonSend')) {
            // Wait for the message to be sent
            setTimeout(() => {
                this.model.root.load();
                const chatter = this.el.querySelector('.o_Chatter');
                if (chatter) {
                    const messageList = chatter.querySelector('.o_Chatter_scrollPanel');
                    if (messageList) {
                        messageList.scrollTop = messageList.scrollHeight;
                    }
                }
            }, 500);
        }
    },
});

// Patch the form view to use our extended FormController
patch(formView, {
    Controller: FormController,
});