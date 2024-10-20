import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { useAutoRefresh } from "./chatter_refresh";
import { patch } from "@web/core/utils/patch";

patch(FormController.prototype, {
    setup() {
        this._super(...arguments);
        useAutoRefresh();
    },
});

export const AutoRefreshFormView = {
    ...formView,
    Controller: FormController,
};