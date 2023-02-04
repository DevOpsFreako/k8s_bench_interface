// Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
// For license information, please see license.txt

/* global frappe, __ */
frappe.ui.form.on('Flux Helm Release', {
  refresh: function (frm) {
    if (!frm.doc.__islocal) {
      frm.toggle_enable('release_name', false);
      frm.toggle_enable('namespace', false);
      frm.toggle_enable('sourceref', false);

      frm.add_custom_button('Update', () => {
        frappe.call({
          method: 'k8s_bench_interface.endpoints.update_helmrelease',
          args: { helmrelease: frm.doc.name },
          callback: r => {
            frappe.msgprint(__('Flux Helm Release Updated'));
          },
        });
      });
    }
  },
});
