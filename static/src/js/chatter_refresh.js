/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { patch } from "@web/core/utils/patch";
import { useEffect } from "@odoo/owl";

patch(FormController.prototype, 'ChatterRefreshFormController', {
    setup() {
        this._super(...arguments);
        
        useEffect(() => {
            const chatter = this.jquery && this.jquery('.o_Chatter')[0];
            if (chatter) {
                const observer = new MutationObserver(() => {
                    if (chatter.querySelector('.o_Composer_buttonSend')) {
                        this.setupSendButtonListener(chatter);
                        observer.disconnect();
                    }
                });
                observer.observe(chatter, { childList: true, subtree: true });
            }
        });
    },

    setupSendButtonListener(chatter) {
        const sendButton = chatter.querySelector('.o_Composer_buttonSend');
        if (sendButton) {
            sendButton.addEventListener('click', () => {
                // Wait for the message to be sent
                setTimeout(() => {
                    this.model.root.load();
                    if (this.model.root.chatter) {
                        this.model.root.chatter.refresh();
                    }
                }, 500);
            });
        }
    },
});

// If you want to apply this to all form views:
patch(formView, 'ChatterRefreshFormView', {
    Controller: FormController,
});

// If you want to create a new view type:
// export const chatterRefreshFormView = {
//     ...formView,
//     Controller: FormController,
// };
// registry.category("views").add("chatter_refresh_form", chatterRefreshFormView);