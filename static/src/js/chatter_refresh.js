/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useEffect, useRef } from "@odoo/owl";

patch(FormController.prototype, {
    setup() {
        this._super(...arguments);
        
        this.rootRef = useRef('root');
        
        useEffect(() => {
            const chatter = this.rootRef.el && this.rootRef.el.querySelector('.o_Chatter');
            if (chatter) {
                const onSendButtonClick = this.onSendButtonClick.bind(this);
                chatter.addEventListener('click', onSendButtonClick);
                return () => {
                    chatter.removeEventListener('click', onSendButtonClick);
                };
            }
        });
    },

    onSendButtonClick(event) {
        if (event.target.closest('.o_Composer_buttonSend')) {
            // Wait for the message to be sent
            setTimeout(() => {
                if (this.model && this.model.root) {
                    this.model.root.load();
                }
                const chatter = this.rootRef.el && this.rootRef.el.querySelector('.o_Chatter');
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