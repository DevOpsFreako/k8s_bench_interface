// Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
// For license information, please see license.txt

/* global frappe, __ */
frappe.ui.form.on('Flux Helm Source', {
  refresh: function (frm) {
    if (frm.doc.kind === 'HelmRepository') {
      frm.toggle_display('branch', false);
    }
    if (!frm.doc.__islocal) {
      frm.toggle_enable('kind', false);
      frm.toggle_enable('namespace', false);
      frm.toggle_enable('source_name', false);
      frm.add_custom_button('Update', () => {
        frappe.call({
          method: 'k8s_bench_interface.endpoints.update_helmsource',
          args: { helmsource: frm.doc.name },
          callback: r => {
            frappe.msgprint(__('Flux Helm Source Updated'));
          },
        });
      });
    }
  },
  kind: function (frm) {
    if (frm.doc.kind === 'HelmRepository') {
      frm.toggle_display('branch', false);
    } else if (frm.doc.kind === 'GitRepository') {
      frm.toggle_display('branch', true);
    }
  },
});
