// Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
// For license information, please see license.txt

/* global frappe, __ */
frappe.ui.form.on('Bench Command', {
  refresh: function (frm) {
    if (!frm.doc.__islocal) {
      frm.disable_form();
      frm.add_custom_button('Fetch Status', () => {
        frappe.call({
          method: 'k8s_bench_interface.endpoints.update_bench_command_status',
          args: { bench_command: frm.doc.name },
          callback: r => {
            frappe.msgprint(__('Bench Command Status Updated'));
          },
        });
      });
    }
  },
  bench: function (frm) {
    if (frm.doc.bench) {
      frappe.call({
        method: 'k8s_bench_interface.endpoints.get_bench_properties',
        args: { helmrelease: frm.doc.bench },
        callback: res => {
          const message = res.message;
          resetValue(frm, message);
        },
      });
    } else {
      resetValue(frm, {});
    }
  },
});

function resetValue(frm, message) {
  frm.set_value('image', message.full_image_name);
  frm.set_value('namespace', message.namespace);
  frm.set_value('sites_pvc', message.sites_pvc);
  // frm.set_value("logs_pvc", message.logs_pvc);
}
