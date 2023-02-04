// Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
// For license information, please see license.txt

/* global frappe, __ */
frappe.ui.form.on('Custom Build', {
  refresh: function (frm) {
    if (!frm.doc.__islocal) {
      frm.disable_form();
      frm.add_custom_button('Fetch Status', () => {
        frappe.call({
          method: 'k8s_bench_interface.endpoints.update_custom_build_status',
          args: { build_name: frm.doc.name },
          callback: r => {
            frappe.msgprint(__('Custom Build Status Updated'));
          },
        });
      });
    }
  },
});
