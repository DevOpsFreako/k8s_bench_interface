## Prerequisites

- Linux machine with multi threaded CPU and large memory
- docker
- docker compose v2
- VS Code
- VS Code Devcontainer Extension

## Setup Devcontainer

clone this repository and setup VS Code devcontainer

```shell
git clone https://gitlab.com/castlecraft/k8s_bench_interface
cd k8s_bench_interface
cp -R devcontainer .devcontainer
```

Reopen workspace in devcontainer.

## Setup development environment

Bootstrap environment

```shell
python bootstrap.py
```

Bootstrap script does the following:

- Setup k8s-bench for development
- Setup frappe-bench
- Enables developer mode
- Add `k8s_bench_interface` app to bench
- Create site `http://k8s-bench-ui.localhost:8000`
- Install `k8s_bench_interface` on site `k8s-bench-ui.localhost`
- Set `k8s_bench_url`, `k8s_bench_key` and `k8s_bench_secret` in `site_config.json`
- Adds line to start k8s-bench api on port 3000 to `Procfile`

Setup Flux and In Cluster NFS Server

```shell
bash /workspace/development/k8s_bench/tests/api/setup.sh
```

## Start development

```shell
cd frappe-bench
bench start
```

Open `http://k8s-bench-ui.localhost:8000` in browser, Complete the setup wizard and start development

Standard Frappe Bench is available for development, add your custom app to it and use frappe python api in your app to manage cluster resources `frappe.new_doc("Bench Command")`

## Performant machine required

- The setup starts normal frappe-bench related services as well as installs helm releases on local cluster. It will need as many threads and memory as you can provide and development can be done locally.
- The machine used to develop this is `Lenovo IdeaPad 330-15ARR`. It has `AMD Ryzen 5 2500U with Radeon Vega Mobile Gfx` with 4 CPU cores, 8 threads and 20GB RAM.

## Mock production locally

Execute the commands in devcontainer.

Install Load Balancer. Command Reference: https://kubernetes.github.io/ingress-nginx/deploy/#gce-gke

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

Setup FluxCD and In Cluster NFS Server

```shell
/workspace/development/k8s_bench/tests/api/setup.sh
```

Install K8s-bench

```shell
helm repo add k8s-bench https://k8s-bench.castlecraft.in
helm repo update k8s-bench
helm upgrade --install \
  --create-namespace \
  --namespace bench-system \
  --set api.createFluxRBAC=true \
  --set api.enabled=true \
  --set api.apiKey=admin \
  --set api.apiSecret=changeit \
  manage-sites k8s-bench/k8s-bench
```

Install K8s-bench-ui

```shell
helm repo add frappe https://helm.erpnext.com
helm repo update frappe
helm upgrade \
  --create-namespace \
  --install k8s-bench-ui \
  --namespace k8s-bench-ui \
  -f /workspace/values-template.yaml \
  frappe/erpnext
```

Site will be available on `https://k8s-bench-ui.localhost`

Teardown

```shell
helm uninstall -n k8s-bench-ui k8s-bench-ui --wait
kubectl delete namespace k8s-bench-ui
helm uninstall -n bench-system manage-sites --wait
kubectl delete namespace bench-system
/workspace/development/k8s_bench/tests/api/teardown.sh
kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```
