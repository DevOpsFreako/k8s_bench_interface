# Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document


class KubernetesNamespace(Document):
    def before_insert(self):
        self.validate_and_save()

    def on_trash(self):
        self.delete_resource()

    def validate_and_save(self):
        res = requests.post(
            frappe.conf.k8s_bench_url + "/core/add-namespace",
            json={"name": self.namespace},
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 409:
                pass

    def delete_resource(self):
        res = requests.post(
            frappe.conf.k8s_bench_url + "/core/delete-namespace",
            json={"name": self.namespace},
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                pass
