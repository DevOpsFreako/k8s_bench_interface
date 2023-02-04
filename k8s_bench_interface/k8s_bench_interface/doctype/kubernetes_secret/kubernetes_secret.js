// Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
// For license information, please see license.txt

/* global frappe, __ */
frappe.ui.form.on('Kubernetes Secret', {
  refresh: function (frm) {
    if (!frm.doc.__islocal) {
      frm.toggle_enable('secret_name', false);
      frm.toggle_enable('secret_namespace', false);
      frm.toggle_enable('secret_type', false);
      frm.add_custom_button('Update', () => {
        frappe.call({
          method: 'k8s_bench_interface.endpoints.update_secret',
          args: { secret_name: frm.doc.name },
          callback: r => {
            frappe.msgprint(__('Secret Updated'));
          },
        });
      });
    }
    if (frm.doc.secret_type === 'kubernetes.io/dockerconfigjson') {
      frm.toggle_display('sb_string_data', false);
    }
    if (frm.doc.secret_type !== 'kubernetes.io/dockerconfigjson') {
      frm.toggle_reqd('data', true);
      toggleDisplay(frm, false);
    }
  },
  secret_type: function (frm) {
    if (frm.doc.secret_type === 'kubernetes.io/dockerconfigjson') {
      frm.toggle_reqd('data', false);
      frm.toggle_display('data', false);
      toggleDisplay(frm, true);
    } else {
      frm.toggle_reqd('data', true);
      frm.toggle_display('data', true);
      toggleDisplay(frm, false);
    }
  },
});

function toggleDisplay(frm, isVisible) {
  frm.toggle_display(
    ['registry_url', 'registry_username', 'registry_password'],
    isVisible,
  );
}
