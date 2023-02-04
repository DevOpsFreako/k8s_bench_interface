# Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe import _
from frappe.model.document import Document


class FluxHelmSource(Document):
    def autoname(self):
        self.name = self.get_name()

    def before_insert(self):
        self.validate_secret_namespace()
        self.validate_and_save()

    def on_trash(self):
        self.delete_resource()

    def get_name(self):
        return f"{self.namespace.lower().strip()}-{self.source_name.lower().strip()}"  # noqa: E501

    def validate_secret_namespace(self):
        if self.secret_ref:
            secret_ref = frappe.get_doc("Kubernetes Secret", self.secret_ref)
            if secret_ref.secret_namespace != self.namespace:
                frappe.throw(_("Invalid Secret Ref Namespace"))

    def validate_and_save(self):
        res = requests.post(
            frappe.conf.k8s_bench_url + "/flux/add-helmsource",
            json={
                "name": self.source_name,
                "namespace": self.namespace,
                "kind": self.kind,
                "interval": self.interval,
                "url": self.url,
                "secret_ref": frappe.get_value(
                    "Kubernetes Secret", self.secret_ref, "secret_name"
                ),
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        res.raise_for_status()

    def delete_resource(self):
        res = requests.post(
            frappe.conf.k8s_bench_url + "/flux/delete-helmsource",
            json={
                "name": self.source_name,
                "namespace": self.namespace,
                "kind": self.kind,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                pass
