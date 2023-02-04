### Prerequisites

- Admin access to Kubernetes cluster
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/)
- [Helm 3](https://helm.sh)
- [FluxCD](https://fluxcd.io)

### Resource Requirements

- **Container Registry**, Comes with Github and Gitlab, or can be purchased or self-hosted.
- **Default StorageClass**, Make sure you've a default `storageclass`. Verify with command `kubectl get sc`.
- **RWX Storage**, Additional storage class with access mode RWX needs to be setup. Alternatives: AWS EFS CSI, rook.io, openebs.io, [seeweedfs](https://github.com/seaweedfs/seaweedfs-operator), etc.
- **MariaDB** Make sure access to MariaDB database with frappe specific configuration is available. Alternatives, [Managed DbaaS](<https://github.com/frappe/frappe/wiki/Using-Frappe-with-Amazon-RDS-(or-any-other-DBaaS)>), [Self-host](https://github.com/frappe/frappe/wiki/Setup-MariaDB-Server), In Cluster helm chart (default).
- **S3 storage**, Recommended to use restic S3 snapshots backups of files.
- **LoadBalancer** service will be created once you install ingress controller, make sure it is budgeted. Install ingress-controller of choice. Documentation refers to [kubernetes/ingress-nginx](https://kubernetes.github.io/ingress-nginx)
- **Cert Manager**, This needs to be installed and configured to generate letsencrypt certificates with http or dns challenge. It is required for auto management of tls for ingresses created. Refer cert-manager.io for more.
- Start with at least 2 nodes in case of separate data server and 3 nodes in case of in-cluster data.
- In case of in-cluster data make sure the nodes have more than 4GB RAM.
- In any case make sure you backup database and files in regularly intervals.

### Backups

- Take 3 backups, 1 Primary backup and 2 copies.
- Save backups on different media types
- Keep 1 backup off-site
- Setup CRON Job for this and make sure disaster recovery measures are in place.

### Install Flux

```shell
flux install --components=source-controller,helm-controller
```

Note: Above command just installs the source controller and helm controller for the CRD needed. Skip the `--components` argument in case you wish to use FluxCD gitops.

### Install K8s Bench

Add and update repo

```shell
helm repo add k8s-bench https://k8s-bench.castlecraft.in
helm repo update k8s-bench
```

Install Helm Release for `k8s-bench`

```shell
helm upgrade --install \
  --create-namespace \
  --namespace bench-system \
  --set api.createFluxRBAC=true \
  --set api.enabled=true \
  --set api.apiKey=admin \
  --set api.apiSecret=changeit \
  manage-sites k8s-bench/k8s-bench
```

Note:

- Change and note down the `api.apiKey` and `api.apiSecret`. They will be later added to `site_config.json` of `k8s_bench_interface` site.
- You can convert the command to `values.yaml` and use it with fluxcd gitops.

### Install K8s Bench Interface

This is just another frappe framework app. Use official helm chart to install this app.

Add and update repo

```shell
helm repo add frappe https://helm.erpnext.com
helm repo update frappe
```

Download and configure `values.yaml`

```shell
curl -fsSL https://gitlab.com/castlecraft/k8s_bench_interface/-/raw/main/values-template.yaml >values.yaml
vim values.yaml
```

Install K8s-bench UI

```shell
helm upgrade \
  --create-namespace \
  --install k8s-bench-ui \
  --namespace k8s-bench-ui \
  -f values.yaml \
  frappe/erpnext
```

Note:

- You can convert values generation and the command to `values.yaml` and use it with fluxcd gitops.

This should install the specified in values
