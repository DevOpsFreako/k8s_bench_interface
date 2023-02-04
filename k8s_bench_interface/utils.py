import base64
import json


def get_resources_dict(
    requests_cpu: str = None,
    requests_memory: str = None,
    limits_cpu: str = None,
    limits_memory: str = None,
):
    resources = {}

    if requests_cpu:
        resources["requests"]["cpu"] = requests_cpu
    if requests_memory:
        resources["requests"]["memory"] = requests_memory
    if limits_cpu:
        resources["limits"]["cpu"] = limits_cpu
    if limits_memory:
        resources["limits"]["memory"] = limits_memory

    return resources


def get_string_data(doc):
    string_data = {}
    if doc.secret_type == "kubernetes.io/dockerconfigjson":
        password = doc.get_password("registry_password")
        secret_key = ".dockerconfigjson"
        auths = {
            "auths": {
                doc.registry_url: {
                    "username": doc.registry_username,
                    "password": password,
                    "auth": base64.b64encode(
                        f"{doc.registry_username}:{password}".encode()
                    )
                    .decode("utf-8")
                    .replace("\n", ""),
                }
            }
        }
        auth_string = json.dumps(auths)
        string_data[secret_key] = auth_string

    else:
        for row in doc.data:
            string_data[row.key] = row.get_password("value")

    return string_data
