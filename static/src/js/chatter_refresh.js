/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { patch } from "@web/core/utils/patch";
import { useEffect } from "@odoo/owl";

patch(FormController.prototype, 'ChatterRefreshFormController', {
    setup() {
        this._super(...arguments);
        
        useEffect(() => {
            this.el.addEventListener('click', this.onSendButtonClick.bind(this));
        });
    },

    onSendButtonClick(event) {
        if (event.target.closest('.o_Composer_buttonSend')) {
            // Wait for the message to be sent
            setTimeout(() => {
                this.model.root.load();
                const chatter = this.model.root.chatter;
                if (chatter && chatter.refresh) {
                    chatter.refresh();
                }
            }, 500);
        }
    },
});

// Patch the form view to use our extended FormController
patch(formView, 'ChatterRefreshFormView', {
    Controller: FormController,
});