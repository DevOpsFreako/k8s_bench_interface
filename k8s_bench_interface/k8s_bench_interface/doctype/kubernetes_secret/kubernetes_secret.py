# Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document

from k8s_bench_interface.utils import get_string_data


class KubernetesSecret(Document):
    def autoname(self):
        self.name = f"{self.secret_namespace}-{self.secret_name}"

    def before_insert(self):
        self.validate_and_save()

    def on_trash(self):
        self.delete_resource()

    def validate_and_save(self):
        string_data = get_string_data(self)

        res = requests.post(
            frappe.conf.k8s_bench_url + "/core/add-secret",
            json={
                "name": self.secret_name,
                "namespace": self.secret_namespace,
                "string_data": string_data,
                "secret_type": self.secret_type,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        res.raise_for_status()

    def delete_resource(self):
        res = requests.post(
            frappe.conf.k8s_bench_url + "/core/delete-secret",
            json={
                "name": self.secret_name,
                "namespace": self.secret_namespace,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                pass
