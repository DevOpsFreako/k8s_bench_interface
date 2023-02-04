# Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
# For license information, please see license.txt

import json

import frappe
import requests
from frappe.model.document import Document

from k8s_bench_interface.utils import get_resources_dict


class CustomBuild(Document):
    def autoname(self):
        self.name = self.get_name()

    def before_insert(self):
        self.validate_and_save()

    def on_trash(self):
        self.delete_resource()

    def get_name(self):
        return f"{self.namespace.lower().strip()}-{self.job_name.lower().strip()}"  # noqa: E501

    def validate_and_save(self):
        node_selector = {}
        for selector in self.node_selectors:
            node_selector[selector.key] = selector.value

        resources = get_resources_dict(
            requests_cpu=self.requests_cpu,
            requests_memory=self.requests_memory,
            limits_cpu=self.limits_cpu,
            limits_memory=self.limits_memory,
        )

        res = requests.post(
            frappe.conf.k8s_bench_url + "/jobs/build-bench",
            json={
                "job_name": self.job_name,
                "namespace": self.namespace,
                "cache": self.cache,
                "push_secret_name": self.push_secret_name,
                "destination_image_name": self.destination_image_name,
                "container_file_path": self.container_file_path,
                "frappe_path": self.frappe_path,
                "frappe_branch": self.frappe_branch,
                "python_version": self.python_version,
                "node_version": self.node_version,
                "apps_json": json.loads(self.apps_json),
                "git_repo_context": self.git_repo_context,
                "insecure_registry": self.insecure_registry,
                "use_new_run": self.use_new_run,
                "snapshot_mode": self.snapshot_mode,
                "host_aliases": json.loads(self.host_aliases),
                "resources": resources,
                "node_selector": node_selector,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        res.raise_for_status()
        self.append("build_logs", {"log": res.text})

    def delete_resource(self):
        res = requests.post(
            frappe.conf.k8s_bench_url + "/jobs/delete-job",
            json={
                "job_name": self.job_name,
                "namespace": self.namespace,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                pass
