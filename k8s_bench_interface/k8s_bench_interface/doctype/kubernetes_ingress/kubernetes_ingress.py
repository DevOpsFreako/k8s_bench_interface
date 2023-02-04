# Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document


class KubernetesIngress(Document):
    def autoname(self):
        self.name = self.get_name()

    def before_insert(self):
        self.validate_and_save()

    def on_trash(self):
        self.delete_resource()

    def validate_and_save(self):
        annotations = {}
        for ant in self.annotations:
            annotations[ant.key] = ant.value

        res = requests.post(
            frappe.conf.k8s_bench_url + "/ingress/create",
            json={
                "name": self.ingress_name,
                "namespace": self.namespace,
                "host": self.host,
                "service_name": self.service_name,
                "service_port": self.service_port,
                "cert_secret_name": self.cert_secret_name,
                "is_wildcard": True if self.is_wildcard else False,
                "annotations": annotations,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        res.raise_for_status()
        self.append("status_logs", {"log": res.text})

    def delete_resource(self):
        res = requests.post(
            frappe.conf.k8s_bench_url + "/ingress/delete",
            json={
                "name": self.ingress_name,
                "namespace": self.namespace,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        res.raise_for_status()

    def get_name(self):
        return f"{self.namespace.lower().strip()}-{self.ingress_name.lower().strip()}"  # noqa: E501
