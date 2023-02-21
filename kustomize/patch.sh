#!/bin/bash
set -e
cat <&0 > kustomize/all.yaml
kubectl kustomize kustomize && rm -f kustomize/all.yaml
