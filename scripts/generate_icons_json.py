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

CATEGORY_NAMES = {
    "argo": "Argo",
    "backstage": "Backstage",
    "cilium": "Cilium",
    "containerd": "containerd",
    "coredns": "CoreDNS",
    "crio": "CRI-O",
    "crossplane": "Crossplane",
    "dapr": "Dapr",
    "envoy": "Envoy",
    "etcd": "etcd",
    "falco": "Falco",
    "fluent-bit": "Fluent Bit",
    "fluentd": "Fluentd",
    "flux": "Flux",
    "grpc": "gRPC",
    "harbor": "Harbor",
    "helm": "Helm",
    "istio": "Istio",
    "jaeger": "Jaeger",
    "k8s-control-plane": "Kubernetes Control Plane",
    "k8s-infrastructure": "Kubernetes Infrastructure",
    "k8s-resources": "Kubernetes Resources",
    "knative": "Knative",
    "kubernetes": "Kubernetes",
    "kyverno": "Kyverno",
    "linkerd": "Linkerd",
    "nats": "NATS",
    "open-policy-agent": "Open Policy Agent",
    "opentelemetry": "OpenTelemetry",
    "prometheus": "Prometheus",
    "rook": "Rook",
    "spiffe": "SPIFFE",
    "spire": "SPIRE",
    "tekton": "Tekton",
    "thanos": "Thanos",
}

TOKEN_NAMES = {
    "api": "API",
    "c": "C",
    "cm": "CM",
    "crb": "CRB",
    "crd": "CRD",
    "cri": "CRI",
    "dns": "DNS",
    "ds": "DS",
    "etcd": "etcd",
    "grpc": "gRPC",
    "hpa": "HPA",
    "ing": "Ing",
    "k": "K",
    "k8s": "K8s",
    "netpol": "NetPol",
    "ns": "NS",
    "opa": "OPA",
    "pdb": "PDB",
    "pv": "PV",
    "pvc": "PVC",
    "rb": "RB",
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
    "backstage": ["developer-portal", "idp"],
    "cilium": ["cni", "networking", "ebpf"],
    "containerd": ["runtime", "cri"],
    "coredns": ["dns"],
    "crio": ["runtime", "cri"],
    "crossplane": ["iac", "control-plane"],
    "dapr": ["microservices", "sidecar"],
    "envoy": ["proxy", "gateway"],
    "etcd": ["kv", "consensus"],
    "falco": ["security", "runtime"],
    "fluent-bit": ["logging"],
    "fluentd": ["logging"],
    "flux": ["gitops", "cd"],
    "grpc": ["rpc"],
    "harbor": ["registry"],
    "helm": ["package", "charts"],
    "istio": ["service-mesh", "mesh"],
    "jaeger": ["tracing"],
    "knative": ["serverless"],
    "kubernetes": ["k8s"],
    "kyverno": ["policy"],
    "linkerd": ["service-mesh", "mesh"],
    "nats": ["messaging"],
    "open-policy-agent": ["opa", "policy"],
    "opentelemetry": ["otel", "observability"],
    "prometheus": ["metrics", "monitoring"],
    "rook": ["storage", "ceph"],
    "spiffe": ["identity"],
    "spire": ["identity"],
    "tekton": ["ci", "pipelines"],
    "thanos": ["metrics", "prometheus"],
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


def humanize(slug: str) -> str:
    words = []
    for word in slug.split("-"):
        words.append(TOKEN_NAMES.get(word, word.capitalize()))
    return " ".join(words)


def display_name(category: str, slug: str) -> str:
    labeled = slug.endswith("-labeled")
    base = slug[: -len("-labeled")] if labeled else slug

    if category == "k8s-resources":
        name = K8S_RESOURCE_NAMES.get(base, humanize(base))
    elif category == "k8s-control-plane":
        name = K8S_CONTROL_PLANE_NAMES.get(base, humanize(base))
    elif category == "k8s-infrastructure":
        name = K8S_INFRA_NAMES.get(base, humanize(base))
    elif category in CATEGORY_NAMES and re.fullmatch(
        rf"{re.escape(category)}-icon-(color|black|white)", slug
    ):
        variant = slug.rsplit("-", 1)[-1]
        name = f"{CATEGORY_NAMES[category]} ({variant})"
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
    for variant in ("color", "black", "white"):
        if slug.endswith(f"-{variant}") or f"-icon-{variant}" in slug:
            tags.add(variant)
            break
    return sorted(tags)


def description_for(category: str, category_label: str, fullname: str) -> str:
    if category.startswith("k8s-"):
        return f"{fullname} Kubernetes architecture icon ({category_label})."
    return f"{fullname} CNCF project icon ({category_label})."


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
        category_label = CATEGORY_NAMES.get(category, humanize(category))
        fullname = display_name(category, slug)
        entries.append(
            {
                "path": relative.as_posix(),
                "tags": tags_for(category, slug),
                "category": category,
                "color": accent_for(category),
                "description": description_for(category, category_label, fullname),
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
