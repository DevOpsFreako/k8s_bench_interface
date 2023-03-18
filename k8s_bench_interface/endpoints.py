import json

import frappe
import requests

from k8s_bench_interface.utils import get_string_data


@frappe.whitelist(methods=["POST"])
def update_helmrelease_status(helmrelease: str):
    hr = frappe.get_doc("Flux Helm Release", helmrelease)
    res = requests.get(
        frappe.conf.k8s_bench_url + "/flux/get-helmrelease-status",
        params={
            "name": hr.release_name,
            "namespace": hr.namespace,
        },
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    hr.append("status_logs", {"log": res.text})
    hr.save()
    return hr


@frappe.whitelist(methods=["POST"])
def update_custom_build_status(build_name: str):
    build = frappe.get_doc("Custom Build", build_name)
    res = requests.get(
        frappe.conf.k8s_bench_url + "/jobs/get-status",
        params={
            "job_name": build.job_name,
            "namespace": build.namespace,
        },
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    build.append("build_logs", {"log": res.text})
    build.save()
    return build.as_dict()


@frappe.whitelist(methods=["POST"])
def update_bench_command_status(bench_command: str):
    command = frappe.get_doc("Bench Command", bench_command)
    res = requests.get(
        frappe.conf.k8s_bench_url + "/jobs/get-status",
        params={
            "job_name": command.job_name,
            "namespace": command.namespace,
        },
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    command.append("command_logs", {"log": res.text})
    command.save()
    return command.as_dict()


@frappe.whitelist()
def get_bench_properties(helmrelease: str):
    hr = frappe.get_doc("Flux Helm Release", helmrelease)
    values = json.loads(hr.values)
    image = values.get("image", {}).get("repository", "frappe/erpnext")
    tag = values.get("image", {}).get("tag", "latest")
    image_pull_secrets = values.get("imagePullSecrets", [])
    return {
        "image": image,
        "tag": tag,
        "full_image_name": f"{image}:{tag}",
        "values": values,
        "image_pull_secrets": image_pull_secrets,
        "namespace": hr.namespace,
        "sites_pvc": f"{hr.release_name}-erpnext",
        "logs_pvc": f"{hr.release_name}-erpnext-logs",
        "nginx_svc": f"{hr.release_name}-erpnext",
        "nginx_svc_port": 8080,
        "gunicorn_svc": f"{hr.release_name}-erpnext-gunicorn",
        "gunicorn_svc_port": 8000,
        "socketio_svc": f"{hr.release_name}-erpnext-socketio",
        "socketio_svc_port": 9000,
    }


@frappe.whitelist(methods=["POST"])
def update_secret(secret_name):
    secret = frappe.get_doc("Kubernetes Secret", secret_name)
    string_data = get_string_data(secret)

    res = requests.post(
        frappe.conf.k8s_bench_url + "/core/update-secret",
        json={
            "name": secret.secret_name,
            "namespace": secret.secret_namespace,
            "string_data": string_data,
            "secret_type": secret.secret_type,
        },
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    return res.json()


@frappe.whitelist(methods=["POST"])
def update_helmrelease(helmrelease: str):
    hr = frappe.get_doc("Flux Helm Release", helmrelease)
    sourceref = frappe.get_doc("Flux Helm Source", hr.sourceref)
    res = requests.post(
        frappe.conf.k8s_bench_url + "/flux/update-helmrelease",
        json={
            "name": hr.release_name,
            "namespace": hr.namespace,
            "release_interval": hr.release_interval,
            "chart_interval": hr.chart_interval,
            "chart": hr.chart,
            "version": hr.version,
            "source_ref": {
                "kind": sourceref.kind,
                "name": sourceref.source_name,
                "namespace": sourceref.namespace,
            },
            "values": json.loads(hr.values),
            "remediate_last_failure": True
            if hr.remediate_last_failure
            else False,  # noqa: E501
            "timeout": hr.timeout,
        },
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    hr.append("status_logs", {"log": res.text})
    hr.save()
    return hr.as_dict()


@frappe.whitelist(methods=["POST"])
def update_helmsource(helmsource: str):
    hs = frappe.get_doc("Flux Helm Source", helmsource)
    res = requests.post(
        frappe.conf.k8s_bench_url + "/flux/update-helmsource",
        json={
            "name": hs.source_name,
            "namespace": hs.namespace,
            "kind": hs.kind,
            "interval": hs.interval,
            "url": hs.url,
            "secret_ref": frappe.get_value(
                "Kubernetes Secret", hs.secret_ref, "secret_name"
            ),
        },
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    return hs.as_dict()


@frappe.whitelist(methods=["POST"])
def update_ingress_status(ingress: str):
    ki = frappe.get_doc("Kubernetes Ingress", ingress)
    res = requests.get(
        frappe.conf.k8s_bench_url + "/ingress/get-status",
        params={
            "name": ki.ingress_name,
            "namespace": ki.namespace,
        },
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    ki.append("status_logs", {"log": res.text})
    ki.save()
    return ki.as_dict()


@frappe.whitelist(methods=["POST"])
def update_ingress(ingress: str):
    ki = frappe.get_doc("Kubernetes Ingress", ingress)
    res = requests.post(
        frappe.conf.k8s_bench_url + "/ingress/patch",
        json={
            "name": ki.ingress_name,
            "namespace": ki.namespace,
            "service_name": ki.service_name,
            "service_port": ki.service_port,
        },
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    ki.append("status_logs", {"log": res.text})
    ki.save()
    return ki.as_dict()


@frappe.whitelist(methods=["POST"])
def update_bench_cronjob_status(bench_cronjob: str):
    cronjob = frappe.get_doc("Bench CronJob", bench_cronjob)
    res = requests.get(
        frappe.conf.k8s_bench_url + "/cronjobs/get-status",
        params={
            "name": cronjob.job_name,
            "namespace": cronjob.namespace,
        },
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    cronjob.append("command_logs", {"log": res.text})
    cronjob.save()
    return cronjob.as_dict()


@frappe.whitelist()
def get_pod_exec_info(pod_name: str = None):
    res = requests.get(
        frappe.conf.k8s_bench_url + "/terminal/get-short-token",
        auth=(frappe.conf.k8s_bench_key, frappe.conf.k8s_bench_secret),
    )
    res.raise_for_status()
    token = res.json().get("token")
    return {
        "token": token,
        "terminal_socket_endpoint": frappe.conf.terminal_socket_endpoint
        or "wss:///terminal",
    }
