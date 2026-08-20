#!/usr/bin/env python3
"""Generate icons.json from CNCF artwork and Kubernetes architecture icons."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = ROOT / "icons"
OUTPUT = ROOT / "icons.json"

CNCF_BLUE = "#0086C9"
K8S_BLUE = "#326CE5"

# Prefer explicit labels for acronyms / unusual casing; others fall back to humanize().
CATEGORY_NAMES = {
    "argo": "Argo",
    "artifact-hub": "Artifact Hub",
    "backstage": "Backstage",
    "bpfman": "bpfman",
    "buildpacks": "Buildpacks",
    "cdk8s": "cdk8s",
    "cert-manager": "cert-manager",
    "chaos-mesh": "Chaos Mesh",
    "cilium": "Cilium",
    "cloud-custodian": "Cloud Custodian",
    "cloudevents": "CloudEvents",
    "cloudnativepg": "CloudNativePG",
    "cni": "CNI",
    "connect-rpc": "Connect RPC",
    "containerd": "containerd",
    "coredns": "CoreDNS",
    "crio": "CRI-O",
    "crossplane": "Crossplane",
    "cubefs": "CubeFS",
    "dapr": "Dapr",
    "devspace": "DevSpace",
    "dragonfly": "Dragonfly",
    "envoy": "Envoy",
    "envoy-gateway": "Envoy Gateway",
    "etcd": "etcd",
    "falco": "Falco",
    "flagger": "Flagger",
    "fluent-bit": "Fluent Bit",
    "fluentd": "Fluentd",
    "flux": "Flux",
    "grpc": "gRPC",
    "hami": "HAMi",
    "harbor": "Harbor",
    "helm": "Helm",
    "in-toto": "in-toto",
    "istio": "Istio",
    "jaeger": "Jaeger",
    "jobset": "JobSet",
    "k0s": "k0s",
    "k3s": "k3s",
    "k8gb": "K8GB",
    "k8s-control-plane": "Kubernetes Control Plane",
    "k8s-infrastructure": "Kubernetes Infrastructure",
    "k8s-resources": "Kubernetes Resources",
    "k8sgpt": "k8sgpt",
    "keda": "KEDA",
    "kepler": "Kepler",
    "keycloak": "Keycloak",
    "knative": "Knative",
    "ko": "ko",
    "kserve": "KServe",
    "kube-rs": "kube-rs",
    "kubeedge": "KubeEdge",
    "kubeflow": "Kubeflow",
    "kubeflow-spark-operator": "Kubeflow Spark Operator",
    "kubernetes": "Kubernetes",
    "kubevirt": "KubeVirt",
    "kueue": "Kueue",
    "kueueviz": "KueueViz",
    "kuma": "Kuma",
    "kyverno": "Kyverno",
    "linkerd": "Linkerd",
    "litmus": "LitmusChaos",
    "llm-d": "llm-d",
    "longhorn": "Longhorn",
    "lws": "LWS",
    "metal3-io": "Metal3",
    "metallb": "MetalLB",
    "nats": "NATS",
    "notary": "Notary",
    "oauth2-proxy": "OAuth2 Proxy",
    "opcr": "OPCR",
    "open-cluster-management": "Open Cluster Management",
    "open-policy-agent": "Open Policy Agent",
    "opencost": "OpenCost",
    "openebs": "OpenEBS",
    "openfeature": "OpenFeature",
    "openfga": "OpenFGA",
    "opengemini": "openGemini",
    "openkruise": "OpenKruise",
    "opentelemetry": "OpenTelemetry",
    "opentofu": "OpenTofu",
    "openyurt": "OpenYurt",
    "operator-framework": "Operator Framework",
    "oscal-compass": "OSCAL Compass",
    "ovn-kubernetes": "OVN-Kubernetes",
    "prometheus": "Prometheus",
    "rook": "Rook",
    "sops": "SOPS",
    "spiffe": "SPIFFE",
    "spire": "SPIRE",
    "stacker": "Stacker",
    "strimzi": "Strimzi",
    "tekton": "Tekton",
    "thanos": "Thanos",
    "tikv": "TiKV",
    "tinkerbell": "Tinkerbell",
    "tuf": "TUF",
    "velero": "Velero",
    "vitess": "Vitess",
    "volcano": "Volcano",
    "wasm-edge-runtime": "WasmEdge",
    "wasmcloud": "wasmCloud",
    "ztunnel": "ztunnel",
}

TOKEN_NAMES = {
    "api": "API",
    "c": "C",
    "cm": "CM",
    "cncf": "CNCF",
    "crb": "CRB",
    "crd": "CRD",
    "cri": "CRI",
    "dns": "DNS",
    "ds": "DS",
    "etcd": "etcd",
    "grpc": "gRPC",
    "hpa": "HPA",
    "ing": "Ing",
    "io": "IO",
    "k": "K",
    "k8s": "K8s",
    "netpol": "NetPol",
    "ns": "NS",
    "opa": "OPA",
    "pdb": "PDB",
    "pg": "PG",
    "pv": "PV",
    "pvc": "PVC",
    "rb": "RB",
    "rpc": "RPC",
    "rs": "RS",
    "sa": "SA",
    "sc": "SC",
    "sts": "STS",
    "svc": "Svc",
    "vol": "Vol",
}

# Keep tags small: category + short aliases only (search still matches name/fullname).
EXTRA_TAGS = {
    "argo": ["gitops", "workflows", "cd"],
    "artifact-hub": ["registry", "helm"],
    "backstage": ["developer-portal", "idp"],
    "buildpacks": ["oci", "build"],
    "cert-manager": ["tls", "certificates"],
    "chaos-mesh": ["chaos", "testing"],
    "cilium": ["cni", "networking", "ebpf"],
    "cloud-custodian": ["policy", "cloud"],
    "cloudevents": ["events"],
    "cni": ["networking"],
    "connect-rpc": ["rpc", "grpc"],
    "containerd": ["runtime", "cri"],
    "devspace": ["dev", "ide"],
    "coredns": ["dns"],
    "crio": ["runtime", "cri"],
    "crossplane": ["iac", "control-plane"],
    "dapr": ["microservices", "sidecar"],
    "dragonfly": ["p2p", "registry"],
    "envoy": ["proxy", "gateway"],
    "envoy-gateway": ["gateway", "proxy"],
    "etcd": ["kv", "consensus"],
    "falco": ["security", "runtime"],
    "flagger": ["progressive-delivery", "canary"],
    "fluent-bit": ["logging"],
    "fluentd": ["logging"],
    "flux": ["gitops", "cd"],
    "grpc": ["rpc"],
    "harbor": ["registry"],
    "helm": ["package", "charts"],
    "in-toto": ["supply-chain", "security"],
    "istio": ["service-mesh", "mesh"],
    "jaeger": ["tracing"],
    "jobset": ["batch", "jobs"],
    "keda": ["autoscaling", "event-driven"],
    "knative": ["serverless"],
    "ko": ["build", "go"],
    "kserve": ["ml", "inference"],
    "kube-rs": ["rust", "client"],
    "kubeedge": ["edge"],
    "kubeflow": ["ml", "ai"],
    "kubeflow-spark-operator": ["ml", "spark"],
    "kubernetes": ["k8s"],
    "kubevirt": ["vm", "virtualization"],
    "kueue": ["batch", "queue", "scheduling"],
    "kyverno": ["policy"],
    "linkerd": ["service-mesh", "mesh"],
    "litmus": ["chaos", "testing"],
    "longhorn": ["storage"],
    "lws": ["batch", "inference"],
    "nats": ["messaging"],
    "notary": ["signing", "supply-chain"],
    "opcr": ["policy", "oci"],
    "open-policy-agent": ["opa", "policy"],
    "opencost": ["finops", "cost"],
    "openfeature": ["feature-flags"],
    "openfga": ["authz", "fga"],
    "opentelemetry": ["otel", "observability"],
    "oscal-compass": ["compliance", "oscal"],
    "prometheus": ["metrics", "monitoring"],
    "rook": ["storage", "ceph"],
    "sops": ["secrets", "encryption"],
    "spiffe": ["identity"],
    "spire": ["identity"],
    "stacker": ["oci", "build"],
    "strimzi": ["kafka", "messaging"],
    "tekton": ["ci", "pipelines"],
    "thanos": ["metrics", "prometheus"],
    "tikv": ["kv", "database"],
    "tinkerbell": ["bare-metal", "provisioning"],
    "tuf": ["supply-chain", "security"],
    "velero": ["backup", "disaster-recovery"],
    "vitess": ["mysql", "database"],
    "volcano": ["batch", "scheduling"],
    "wasmcloud": ["wasm"],
    "ztunnel": ["ambient", "mesh"],
    "k8s-resources": ["k8s", "resources"],
    "k8s-control-plane": ["k8s", "control-plane"],
    "k8s-infrastructure": ["k8s", "infrastructure"],
}

K8S_RESOURCE_NAMES = {
    "c-role": "Cluster Role",
    "cm": "ConfigMap",
    "crb": "Cluster Role Binding",
    "crd": "Custom Resource Definition",
    "cronjob": "CronJob",
    "deploy": "Deployment",
    "ds": "DaemonSet",
    "ep": "Endpoints",
    "group": "Group",
    "hpa": "Horizontal Pod Autoscaler",
    "ing": "Ingress",
    "job": "Job",
    "limits": "Limit Range",
    "netpol": "Network Policy",
    "ns": "Namespace",
    "pod": "Pod",
    "psp": "Pod Security Policy",
    "pv": "Persistent Volume",
    "pvc": "Persistent Volume Claim",
    "quota": "Resource Quota",
    "rb": "Role Binding",
    "role": "Role",
    "rs": "ReplicaSet",
    "sa": "Service Account",
    "sc": "Storage Class",
    "secret": "Secret",
    "sts": "StatefulSet",
    "svc": "Service",
    "user": "User",
    "vol": "Volume",
}

K8S_CONTROL_PLANE_NAMES = {
    "api": "API Server",
    "c-c-m": "Cloud Controller Manager",
    "c-m": "Controller Manager",
    "k-proxy": "Kube Proxy",
    "kubelet": "Kubelet",
    "sched": "Scheduler",
}

K8S_INFRA_NAMES = {
    "control-plane": "Control Plane",
    "etcd": "etcd",
    "node": "Node",
}

ICON_VARIANT_RE = re.compile(
    r"^(.+)-icon-(color|black|white|grey|gray|wireframe|solid-color|"
    r"reverse-color|color-inverted|color-dark|color-light)$"
)


def humanize(slug: str) -> str:
    words = []
    for word in slug.split("-"):
        words.append(TOKEN_NAMES.get(word, word.capitalize()))
    return " ".join(words)


def category_label(category: str) -> str:
    return CATEGORY_NAMES.get(category, humanize(category))


def display_name(category: str, slug: str) -> str:
    labeled = slug.endswith("-labeled")
    base = slug[: -len("-labeled")] if labeled else slug

    if category == "k8s-resources":
        name = K8S_RESOURCE_NAMES.get(base, humanize(base))
    elif category == "k8s-control-plane":
        name = K8S_CONTROL_PLANE_NAMES.get(base, humanize(base))
    elif category == "k8s-infrastructure":
        name = K8S_INFRA_NAMES.get(base, humanize(base))
    else:
        match = ICON_VARIANT_RE.fullmatch(slug)
        if match:
            variant = match.group(2)
            if variant == "gray":
                variant = "grey"
            # Prefer category label even when upstream prefix differs (e.g. opa-*).
            name = f"{category_label(category)} ({variant})"
        else:
            name = humanize(slug)

    if labeled:
        name = f"{name} (labeled)"
    return name


def tags_for(category: str, slug: str) -> list[str]:
    tags = {category}
    tags.update(EXTRA_TAGS.get(category, []))
    if slug.endswith("-labeled"):
        tags.add("labeled")
    elif category.startswith("k8s-"):
        tags.add("unlabeled")
    for variant in (
        "color-inverted",
        "color-dark",
        "color-light",
        "solid-color",
        "reverse-color",
        "wireframe",
        "color",
        "black",
        "white",
        "grey",
        "gray",
    ):
        if slug.endswith(f"-{variant}") or f"-icon-{variant}" in slug:
            tags.add("grey" if variant == "gray" else variant)
            break
    return sorted(tags)


def description_for(category: str, label: str, fullname: str) -> str:
    if category.startswith("k8s-"):
        return f"{fullname} Kubernetes architecture icon ({label})."
    return f"{fullname} CNCF project icon ({label})."


def accent_for(category: str) -> str:
    if category.startswith("k8s-") or category == "kubernetes":
        return K8S_BLUE
    return CNCF_BLUE


def build_entries() -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for svg_path in sorted(ICONS_DIR.glob("*/*.svg")):
        relative = svg_path.relative_to(ROOT)
        category = relative.parts[1]
        slug = svg_path.stem
        label = category_label(category)
        fullname = display_name(category, slug)
        entries.append(
            {
                "path": relative.as_posix(),
                "tags": tags_for(category, slug),
                "category": category,
                "color": accent_for(category),
                "description": description_for(category, label, fullname),
                "fullname": fullname,
                "name": slug,
            }
        )

    entries.sort(
        key=lambda icon: (
            str(icon["category"]).casefold(),
            str(icon["fullname"]).casefold(),
            str(icon["path"]),
        )
    )
    return entries


def main() -> None:
    entries = build_entries()
    if not entries:
        raise SystemExit(f"No SVG icons found under {ICONS_DIR}")

    OUTPUT.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(entries)} icons to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
