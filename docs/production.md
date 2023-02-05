### Prerequisites

- Admin access to Kubernetes cluster
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/)
- [Helm 3](https://helm.sh)
- [FluxCD](https://fluxcd.io)
- [Cert Manager](https://cert-manager.io) Optional for automating letsencrypt certificates. Not required in case of purchased wildcard certificates.

### Resource and Budget Requirements

**Container Registry**

Budget for this is required to push the built container images. It can also be used to cache layers for faster builds. If you have private apps, you may need a private registry. GitHub provides `ghcr.io` and Gitlab provides `registry.gitlab.com`. More alternatives here. [CNCF Landscape/Container Registry](https://landscape.cncf.io/card-mode?category=container-registry&grouping=category).

**Database**

Budget for database as per the availability and scale requirements. Make sure access to database with frappe specific configuration is available. Some of available alternatives, [Managed DbaaS](<https://github.com/frappe/frappe/wiki/Using-Frappe-with-Amazon-RDS-(or-any-other-DBaaS)>), [Self-host](https://github.com/frappe/frappe/wiki/Setup-MariaDB-Server), If you use helm chart to install database make sure you have default `StorageClass` available, it is necessary to attach block storage to store volume for MariaDB Primary Server. This storageclass is separate from the RWX Storage Class mentioned below.

**RWX Storage**

Additional storage class with access mode RWX needs to be available. Alternatives: [AWS EFS CSI](https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html), [Rook](https://rook.io), [OpenEBS](https://openebs.io), [seaweedfs](https://github.com/seaweedfs/seaweedfs-operator), etc. In case of In-Cluster Helm Chart for NFS server. Additional default storage class will be required. It is used to connect block storage to store files served by NFS server.

**S3 storage**

Recommended to use restic S3 snapshots backups of files. Each site can have their own snapshots. Bench level snapshots can be taken irrespective of site level snapshots. Required in case of serving production sites that may not enable individual S3 backups.

**LoadBalancer**

Cloud load balancer will be created once you install ingress controller, make sure it is budgeted. Install ingress-controller of choice. Documentation refers to [kubernetes/ingress-nginx](https://kubernetes.github.io/ingress-nginx)

**Nodes**

Start with at least 2 nodes in case of separate data server and 3 nodes in case of in-cluster data. In case of in-cluster data make sure the nodes have more than 4GB RAM. In any case make sure you backup database and files in regularly intervals.

**DNS Management**

In case Cert Manager is used to automate letsencrypt wildcard certificates with `dns01` challenge then make sure the service you are using to manage DNS is supported or has a webhook available. [Supported DNS01 providers](https://cert-manager.io/docs/configuration/acme/dns01/#supported-dns01-providers). If your service is not supported you can move the nameservers to the supported service or purchase wildcard certificates and set them as secret in cluster without using cert manager.

### Backups

- Take at least 2 backups, 1 Primary backup and 1 copy
- Save backups on different media types
- Keep at least 1 backup off-site
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
