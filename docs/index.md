### Frappe App and UI to operate the K8s-bench

This is a Frappe Framework App to interact with [k8s-bench](https://k8s-bench.castlecraft.in)

- Create and Delete Namespaces
- Create, Update and Delete Secrets
- Create, Update and Delete Sources for bench helm charts.
- Create, Update and Delete Bench releases as per sources.
- Create and Delete Jobs to build custom bench images
- Create and Delete Jobs to run bench commands for given bench

Use this app as is to control benches and sites on benches on a Kubernetes cluster.

Use this app along with your custom apps as abstraction to build SaaS/PaaS over bench.
