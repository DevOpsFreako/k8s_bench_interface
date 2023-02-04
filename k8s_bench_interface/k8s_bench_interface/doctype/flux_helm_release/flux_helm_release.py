# Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
# For license information, please see license.txt

import json

import frappe
import requests
from frappe.model.document import Document


class FluxHelmRelease(Document):
    def autoname(self):
        self.name = self.get_name()

    def before_insert(self):
        self.validate_and_save()

    def on_trash(self):
        self.delete_resource()

    def validate_and_save(self):
        sourceref = frappe.get_doc("Flux Helm Source", self.sourceref)
        res = requests.post(
            frappe.conf.k8s_bench_url + "/flux/add-helmrelease",
            json={
                "name": self.release_name,
                "namespace": self.namespace,
                "release_interval": self.release_interval,
                "chart_interval": self.chart_interval,
                "chart": self.chart,
                "version": self.version,
                "source_ref": {
                    "kind": sourceref.kind,
                    "name": sourceref.source_name,
                    "namespace": sourceref.namespace,
                },
                "values": json.loads(self.values),
                "remediate_last_failure": True
                if self.remediate_last_failure
                else False,
                "timeout": self.timeout,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        res.raise_for_status()
        self.append("status_logs", {"log": res.text})

    def delete_resource(self):
        res = requests.post(
            frappe.conf.k8s_bench_url + "/flux/delete-helmrelease",
            json={
                "name": self.release_name,
                "namespace": self.namespace,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        res.raise_for_status()

    def get_name(self):
        return f"{self.namespace.lower().strip()}-{self.release_name.lower().strip()}"  # noqa: E501
