# Copyright (c) 2023, Castlecraft Ecommerce Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document

from k8s_bench_interface.utils import get_resources_dict


class BenchCommand(Document):
    def autoname(self):
        self.name = self.get_name()

    def before_insert(self):
        self.validate_and_save()

    def on_trash(self):
        self.delete_resource()

    def get_name(self):
        return f"{self.namespace.lower().strip()}-{self.job_name.lower().strip()}"  # noqa: E501

    def validate_and_save(self):
        annotations = {}
        for ant in self.annotations:
            annotations[ant.key] = ant.value

        node_selector = {}
        for selector in self.node_selectors:
            node_selector[selector.key] = selector.value

        command_volumes = []

        for vol in self.command_volumes:
            command_volumes.append(
                {
                    "volume_name": vol.volume_name,
                    "pvc_name": vol.pvc_name,
                    "mount_path": vol.mount_path,
                    "read_only": True if vol.read_only else False,
                }
            )

        resources = get_resources_dict(
            requests_cpu=self.requests_cpu,
            requests_memory=self.requests_memory,
            limits_cpu=self.limits_cpu,
            limits_memory=self.limits_memory,
        )

        image_pull_secrets = [
            {
                "name": frappe.get_value(
                    "Kubernetes Secret",
                    sec.secret,
                    "secret_name",
                ),
            }
            for sec in self.image_pull_secrets
        ]
        res = requests.post(
            frappe.conf.k8s_bench_url + "/jobs/bench-command",
            json={
                "job_name": self.job_name,
                "sites_pvc": self.sites_pvc,
                "args": [arg.arg for arg in self.args],
                "command": [cmd.command for cmd in self.commands],
                "logs_pvc": self.logs_pvc,
                "namespace": self.namespace,
                "image_pull_secrets": image_pull_secrets,
                "image": self.image,
                "annotations": annotations,
                "node_selector": node_selector,
                "resources": resources,
                "additional_volumes": command_volumes,
            },
            auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
        )
        res.raise_for_status()
        self.append("command_logs", {"log": res.text})

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
