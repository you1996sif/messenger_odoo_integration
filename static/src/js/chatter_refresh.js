/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useEffect, onWillStart } from "@odoo/owl";

patch(FormController.prototype, {
    setup() {
        const superSetup = this._super;
        if (superSetup) {
            superSetup.call(this, ...arguments);
        }
        
        onWillStart(() => {
            this.chatterRefreshSetup();
        });
    },

    chatterRefreshSetup() {
        useEffect(() => {
            const chatter = this.el && this.el.querySelector('.o_Chatter');
            if (chatter) {
                chatter.addEventListener('click', this.onSendButtonClick.bind(this));
            }
            return () => {
                if (chatter) {
                    chatter.removeEventListener('click', this.onSendButtonClick.bind(this));
                }
            };
        });
    },

    onSendButtonClick(event) {
        if (event.target.closest('.o_Composer_buttonSend')) {
            // Wait for the message to be sent
            setTimeout(() => {
                if (this.model && this.model.root) {
                    this.model.root.load();
                }
                const chatter = this.el && this.el.querySelector('.o_Chatter');
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