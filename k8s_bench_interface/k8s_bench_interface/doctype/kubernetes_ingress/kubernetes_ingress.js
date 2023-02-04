// Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
// For license information, please see license.txt

/* global frappe, __ */
frappe.ui.form.on('Kubernetes Ingress', {
  refresh: function (frm) {
    if (!frm.doc.__islocal) {
      frm.toggle_enable('ingress_name', false);
      frm.toggle_enable('namespace', false);
      frm.toggle_enable('host', false);

      frm.add_custom_button('Update', () => {
        frappe.call({
          method: 'k8s_bench_interface.endpoints.update_ingress',
          args: { ingress: frm.doc.name },
          callback: r => {
            frappe.msgprint(__('Kubernetes Ingress Updated'));
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
  frm.set_value('namespace', message.namespace);
  frm.set_value('service_name', message.nginx_svc);
  frm.set_value('service_port', message.nginx_svc_port);
}
