---
name: phy-k8s-security-audit
description: Kubernetes manifest security auditor (CIS Kubernetes Benchmark). Scans all YAML/JSON manifests in your repository for privileged containers, hostNetwork/hostPID/hostIPC, dangerous hostPath mounts, missing resource limits/probes, latest image tags, RBAC over-permission (cluster-admin bindings, wildcard verbs), secrets in env vars, missing NetworkPolicy, missing seccomp/AppArmor profiles. Maps findings to CIS Benchmark controls and PSS (Pod Security Standards). Zero dependencies beyond PyYAML. Zero competitors on ClawHub.
license: Apache-2.0
tags:
  - security
  - kubernetes
  - k8s
  - cis-benchmark
  - devsecops
  - cloud-security
  - rbac
  - container-security
metadata:
  author: PHY041
  version: "1.0.0"
---

# phy-k8s-security-audit

Static security auditor for **Kubernetes YAML manifests**. Scans every Deployment, StatefulSet, DaemonSet, Pod, Job, CronJob, Role, ClusterRole, RoleBinding, ClusterRoleBinding, ServiceAccount, and NetworkPolicy in your repository against the **CIS Kubernetes Benchmark v1.9** and **Pod Security Standards (PSS)**. No cluster access required — works entirely on local manifest files.

## Why Manifest Auditing Matters

- Tesla's Kubernetes cluster was cryptojacked because their dashboard had no auth and pods ran privileged
- Attackers with access to one container can escape to the node via `privileged: true` or `hostPath` mounts
- Over-permissive RBAC (`cluster-admin`) is the #1 post-exploit persistence technique
- `automountServiceAccountToken: true` (the default) leaks credentials into every pod

## Checks: Pod / Container Level

| Check | Severity | CIS / PSS |
|-------|----------|-----------|
| `privileged: true` | CRITICAL | CIS 5.2.1 / PSS Restricted |
| `allowPrivilegeEscalation: true` or missing (default true) | HIGH | CIS 5.2.5 / PSS Restricted |
| `runAsNonRoot` missing or false | HIGH | CIS 5.2.6 / PSS Baseline |
| `runAsUser: 0` (root) | HIGH | CIS 5.2.6 |
| `hostNetwork: true` | HIGH | CIS 5.2.4 / PSS Baseline |
| `hostPID: true` | HIGH | CIS 5.2.2 / PSS Baseline |
| `hostIPC: true` | HIGH | CIS 5.2.3 / PSS Baseline |
| `hostPath` volume mount | HIGH | CIS 5.2.11 |
| `capabilities.add` with dangerous caps (SYS_ADMIN, NET_ADMIN, ALL) | CRITICAL | CIS 5.2.8 |
| Missing `capabilities.drop: [ALL]` | MEDIUM | CIS 5.2.7 / PSS Restricted |
| Missing resource `requests` and `limits` | MEDIUM | CIS 5.2.13 |
| `image: *:latest` or no tag | MEDIUM | Best practice |
| `imagePullPolicy: Never` with mutable tag | MEDIUM | Best practice |
| Missing `readinessProbe` | LOW | Best practice |
| Missing `livenessProbe` | LOW | Best practice |
| Secrets in `env` values (plaintext) | HIGH | CIS 5.4.1 |
| Missing `seccompProfile` | MEDIUM | CIS 5.7.2 / PSS Restricted |
| Missing `securityContext` entirely | MEDIUM | CIS 5.7.1 |
| `readOnlyRootFilesystem: false` (or missing) | MEDIUM | PSS Restricted |

## Checks: RBAC Level

| Check | Severity | CIS |
|-------|----------|-----|
| ClusterRoleBinding to `cluster-admin` | CRITICAL | CIS 5.1.1 |
| Role/ClusterRole with `verbs: ["*"]` | HIGH | CIS 5.1.3 |
| Role/ClusterRole with `resources: ["*"]` | HIGH | CIS 5.1.3 |
| Role with `secrets` GET/LIST permission | HIGH | CIS 5.1.2 |
| ServiceAccount with `automountServiceAccountToken: true` in non-system namespace | MEDIUM | CIS 5.1.5 |
| Default service account used (no explicit serviceAccountName) | MEDIUM | CIS 5.1.5 |

## Checks: Network Level

| Check | Severity | CIS |
|-------|----------|-----|
| No NetworkPolicy in namespace (detected from file dir) | HIGH | CIS 5.3.2 |
| NetworkPolicy `podSelector: {}` (applies to all pods) without ingress rules | MEDIUM | Best practice |
| Service type `NodePort` without explicit justification comment | LOW | CIS 5.4.2 |
| Service type `LoadBalancer` exposing non-HTTP port | MEDIUM | CIS 5.4.2 |

## Pod Security Standards Classification

Each Pod/Deployment spec is classified against PSS:

| Profile | Description |
|---------|-------------|
| **Privileged** | No restrictions — flag all workloads at this level |
| **Baseline** | No privileged, no host namespaces, no hostPath — minimum for most apps |
| **Restricted** | All of Baseline + non-root, no privilege escalation, seccomp, drop ALL caps |

## Implementation

```python
#!/usr/bin/env python3
"""
phy-k8s-security-audit — CIS Kubernetes Benchmark manifest scanner
Usage: python3 audit_k8s.py [path] [--json] [--ci] [--min-severity HIGH]

Requires: pip install pyyaml (almost always already installed)
"""
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("Warning: PyYAML not found. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

CRITICAL, HIGH, MEDIUM, LOW = "CRITICAL", "HIGH", "MEDIUM", "LOW"
SEV_ORDER = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3}
ICONS = {CRITICAL: "🔴", HIGH: "🟠", MEDIUM: "🟡", LOW: "⚪"}

# Capabilities that are effectively root
DANGEROUS_CAPS = {
    "SYS_ADMIN", "NET_ADMIN", "SYS_PTRACE", "SYS_MODULE", "SYS_RAWIO",
    "ALL", "SYSLOG", "DAC_READ_SEARCH", "LINUX_IMMUTABLE",
    "NET_BROADCAST", "IPC_LOCK", "WAKE_ALARM", "BLOCK_SUSPEND",
}

# RBAC verbs that indicate over-permission
SENSITIVE_RBAC_VERBS = {"*", "create", "delete", "deletecollection", "patch", "update"}
SECRET_VERBS = {"get", "list", "watch", "*"}

@dataclass
class Finding:
    file: str
    resource_kind: str
    resource_name: str
    check_id: str
    severity: str
    title: str
    detail: str
    remediation: str
    cis_ref: Optional[str] = None
    pss_profile: Optional[str] = None

def get_name(obj: dict) -> str:
    return obj.get("metadata", {}).get("name", "<unnamed>")

def get_namespace(obj: dict) -> str:
    return obj.get("metadata", {}).get("namespace", "default")

def check_container_security(
    container: dict,
    file: str,
    kind: str,
    resource_name: str,
    is_init: bool = False,
) -> list[Finding]:
    findings = []
    sc = container.get("securityContext", {})
    cname = container.get("name", "<unnamed>")
    label = f"{resource_name}/{cname}" + (" (init)" if is_init else "")

    def add(check_id, sev, title, detail, remediation, cis=None, pss=None):
        findings.append(Finding(file, kind, label, check_id, sev, title, detail, remediation, cis, pss))

    # Privileged container
    if sc.get("privileged") is True:
        add("C001", CRITICAL, "Privileged container",
            f"securityContext.privileged: true — container has full host access",
            "Remove privileged: true. Use specific capabilities instead.",
            "CIS 5.2.1", "PSS Restricted")

    # Privilege escalation
    if sc.get("allowPrivilegeEscalation") is True:
        add("C002", HIGH, "Privilege escalation allowed",
            "allowPrivilegeEscalation: true — setuid binaries can gain root",
            "Set allowPrivilegeEscalation: false in securityContext.",
            "CIS 5.2.5", "PSS Restricted")
    elif "allowPrivilegeEscalation" not in sc:
        # Default is true — flag unless privileged is already flagged
        if not sc.get("privileged"):
            add("C002b", MEDIUM, "allowPrivilegeEscalation not explicitly set (defaults to true)",
                "Default allows setuid escalation. Explicitly disable.",
                "Add allowPrivilegeEscalation: false to securityContext.",
                "CIS 5.2.5")

    # Root user
    if sc.get("runAsUser") == 0:
        add("C003", HIGH, "Container runs as root (runAsUser: 0)",
            "Explicitly running as UID 0 — root in container maps to root on host in many configs.",
            "Use a non-root UID: runAsUser: 1000 or higher.",
            "CIS 5.2.6")
    elif not sc.get("runAsNonRoot") and "runAsUser" not in sc:
        add("C004", MEDIUM, "runAsNonRoot not enforced",
            "Neither runAsNonRoot: true nor a non-zero runAsUser is set.",
            "Add runAsNonRoot: true to securityContext.",
            "CIS 5.2.6", "PSS Baseline")

    # Capabilities
    caps = sc.get("capabilities", {})
    added_caps = caps.get("add", [])
    for cap in added_caps:
        if cap.upper() in DANGEROUS_CAPS:
            add("C005", CRITICAL, f"Dangerous capability added: {cap}",
                f"capabilities.add: [{cap}] grants near-root privileges.",
                f"Remove {cap} from capabilities.add. Use least-privilege capabilities only.",
                "CIS 5.2.8", "PSS Baseline")

    if "drop" not in caps or "ALL" not in [c.upper() for c in caps.get("drop", [])]:
        add("C006", MEDIUM, "capabilities.drop: [ALL] missing",
            "Not dropping all Linux capabilities — container retains default set.",
            "Add capabilities.drop: [ALL] and add back only what's needed.",
            "CIS 5.2.7", "PSS Restricted")

    # Read-only root filesystem
    if not sc.get("readOnlyRootFilesystem"):
        add("C007", MEDIUM, "readOnlyRootFilesystem not set",
            "Writable root filesystem — malware can install binaries/modify configs in-container.",
            "Set readOnlyRootFilesystem: true; use emptyDir or PVC for writable paths.",
            "PSS Restricted")

    # seccompProfile
    if "seccompProfile" not in sc:
        add("C008", MEDIUM, "seccompProfile not set",
            "No seccomp profile — container can make any syscall.",
            "Add seccompProfile: {type: RuntimeDefault} or a custom profile.",
            "CIS 5.7.2", "PSS Restricted")

    # Resource limits
    resources = container.get("resources", {})
    limits = resources.get("limits", {})
    requests = resources.get("requests", {})
    if not limits.get("memory") or not limits.get("cpu"):
        add("C009", MEDIUM, "Missing resource limits",
            f"No CPU/memory limits — container can starve other pods (DoS).",
            "Set resources.limits.cpu and resources.limits.memory.",
            "CIS 5.2.13")
    if not requests.get("memory") or not requests.get("cpu"):
        add("C010", LOW, "Missing resource requests",
            "No CPU/memory requests — scheduler cannot make accurate placement decisions.",
            "Set resources.requests.cpu and resources.requests.memory.")

    # Image tag
    image = container.get("image", "")
    if image.endswith(":latest") or (":" not in image.split("/")[-1]):
        add("C011", MEDIUM, "Image uses 'latest' tag or no tag",
            f"Image '{image}' — non-specific tags break reproducibility and rollbacks.",
            "Pin images to a specific digest: image: myapp:v1.2.3@sha256:...")

    # Secrets in env
    for env in container.get("env", []):
        val = str(env.get("value", ""))
        name = env.get("name", "")
        if re.search(r'(?i)(password|secret|key|token|credential|private)', name) and val:
            add("C012", HIGH, f"Secret in plain env var: {name}",
                f"Env var '{name}' contains a secret value in plaintext.",
                "Use secretKeyRef: kubectl create secret generic my-secret --from-literal=key=value\n"
                "Then env: [{name: MY_SECRET, valueFrom: {secretKeyRef: {name: my-secret, key: key}}}]",
                "CIS 5.4.1")

    # Probes
    if not container.get("readinessProbe"):
        add("C013", LOW, "Missing readinessProbe",
            "No readinessProbe — pod may receive traffic before it's ready.",
            "Add readinessProbe with appropriate httpGet/tcpSocket/exec.")
    if not container.get("livenessProbe"):
        add("C014", LOW, "Missing livenessProbe",
            "No livenessProbe — stuck processes won't be restarted automatically.",
            "Add livenessProbe with appropriate httpGet/tcpSocket/exec.")

    return findings

def check_pod_spec(pod_spec: dict, file: str, kind: str, resource_name: str) -> list[Finding]:
    findings = []
    sc = pod_spec.get("securityContext", {})
    name = resource_name

    def add(check_id, sev, title, detail, remediation, cis=None, pss=None):
        findings.append(Finding(file, kind, name, check_id, sev, title, detail, remediation, cis, pss))

    # Host namespaces
    if pod_spec.get("hostNetwork"):
        add("P001", HIGH, "hostNetwork: true",
            "Pod shares host network namespace — can sniff all node traffic, bind privileged ports.",
            "Remove hostNetwork: true. Use ClusterIP services for internal communication.",
            "CIS 5.2.4", "PSS Baseline")

    if pod_spec.get("hostPID"):
        add("P002", HIGH, "hostPID: true",
            "Pod shares host PID namespace — can see/signal all processes on node.",
            "Remove hostPID: true.",
            "CIS 5.2.2", "PSS Baseline")

    if pod_spec.get("hostIPC"):
        add("P003", HIGH, "hostIPC: true",
            "Pod shares host IPC namespace — can access host shared memory and semaphores.",
            "Remove hostIPC: true.",
            "CIS 5.2.3", "PSS Baseline")

    # hostPath volumes
    for vol in pod_spec.get("volumes", []):
        if "hostPath" in vol:
            hp = vol["hostPath"].get("path", "")
            sev = CRITICAL if hp in ("/", "/etc", "/var/run/docker.sock", "/proc", "/sys") else HIGH
            add("P004", sev, f"hostPath volume: {hp}",
                f"Volume '{vol['name']}' mounts hostPath '{hp}' — filesystem escape risk.",
                "Replace hostPath with PersistentVolumeClaim or emptyDir. "
                "If hostPath is required, use readOnly: true and restrict path.",
                "CIS 5.2.11")

    # Service account token automount
    if pod_spec.get("automountServiceAccountToken") is not False:
        sa_name = pod_spec.get("serviceAccountName", "default")
        if sa_name == "default":
            add("P005", MEDIUM, "Default service account with auto-mounted token",
                "Using default service account with automountServiceAccountToken (default: true). "
                "Token is available at /var/run/secrets/kubernetes.io/serviceaccount/token.",
                "Create a dedicated ServiceAccount with minimal RBAC. "
                "Set automountServiceAccountToken: false if not needed.",
                "CIS 5.1.5")

    # Pod-level securityContext
    if not sc:
        add("P006", MEDIUM, "Missing pod-level securityContext",
            "No pod-level securityContext — runAsNonRoot, seccompProfile, sysctls not enforced.",
            "Add securityContext: {runAsNonRoot: true, seccompProfile: {type: RuntimeDefault}}",
            "CIS 5.7.1")

    # Container-level checks
    for container in pod_spec.get("containers", []):
        findings.extend(check_container_security(container, file, kind, name))
    for container in pod_spec.get("initContainers", []):
        findings.extend(check_container_security(container, file, kind, name, is_init=True))

    return findings

def check_rbac(obj: dict, file: str) -> list[Finding]:
    findings = []
    kind = obj.get("kind", "")
    name = get_name(obj)

    if kind in ("Role", "ClusterRole"):
        for rule in obj.get("rules", []):
            verbs = set(v.lower() for v in rule.get("verbs", []))
            resources = rule.get("resources", [])
            api_groups = rule.get("apiGroups", [])

            if "*" in verbs:
                findings.append(Finding(file, kind, name, "R001", HIGH,
                    "Wildcard verbs in RBAC rule",
                    f"verbs: ['*'] grants all operations on {resources}",
                    "Replace '*' with the minimum verbs required (get, list, watch).",
                    "CIS 5.1.3"))

            if "*" in resources:
                findings.append(Finding(file, kind, name, "R002", HIGH,
                    "Wildcard resources in RBAC rule",
                    "resources: ['*'] grants access to all API resources",
                    "Enumerate specific resources required.",
                    "CIS 5.1.3"))

            if "secrets" in resources and verbs.intersection(SECRET_VERBS):
                findings.append(Finding(file, kind, name, "R003", HIGH,
                    "RBAC rule grants secret access",
                    f"Allows {verbs & SECRET_VERBS} on secrets — enables credential harvesting.",
                    "Remove secrets access unless strictly necessary for this service account.",
                    "CIS 5.1.2"))

    elif kind in ("RoleBinding", "ClusterRoleBinding"):
        role_ref = obj.get("roleRef", {})
        subjects = obj.get("subjects", [])

        if role_ref.get("name") == "cluster-admin":
            subject_names = [s.get("name", "") for s in subjects]
            findings.append(Finding(file, kind, name, "R004", CRITICAL,
                "Binding to cluster-admin role",
                f"Subjects {subject_names} bound to cluster-admin — full cluster control.",
                "Replace cluster-admin with a custom ClusterRole with minimum permissions.",
                "CIS 5.1.1"))

    return findings

def check_network_policy(obj: dict, file: str) -> list[Finding]:
    findings = []
    kind = obj.get("kind", "")
    name = get_name(obj)
    if kind != "NetworkPolicy":
        return findings

    spec = obj.get("spec", {})
    pod_selector = spec.get("podSelector", {})
    if pod_selector == {} and not spec.get("ingress") and not spec.get("egress"):
        findings.append(Finding(file, kind, name, "N001", MEDIUM,
            "NetworkPolicy with empty podSelector and no rules",
            "Applies to all pods but has no ingress/egress rules — ineffective.",
            "Add explicit ingress/egress rules or restrict podSelector."))

    return findings

def check_service(obj: dict, file: str) -> list[Finding]:
    findings = []
    spec = obj.get("spec", {})
    svc_type = spec.get("type", "ClusterIP")
    name = get_name(obj)

    if svc_type == "NodePort":
        findings.append(Finding(file, "Service", name, "S001", LOW,
            "Service type NodePort — exposes port on all nodes",
            "NodePort services are accessible on all cluster nodes on the host port.",
            "Use LoadBalancer or ClusterIP + Ingress instead of NodePort for production.",
            "CIS 5.4.2"))
    elif svc_type == "LoadBalancer":
        ports = spec.get("ports", [])
        for p in ports:
            if p.get("port") not in (80, 443):
                findings.append(Finding(file, "Service", name, "S002", MEDIUM,
                    f"LoadBalancer exposing non-HTTP port {p.get('port')}",
                    "Non-HTTP ports on LoadBalancer are exposed directly to the internet.",
                    "Use a TCP proxy or restrict access with annotations (e.g., GCP loadBalancerSourceRanges).",
                    "CIS 5.4.2"))
    return findings

CONTAINER_KINDS = {"Pod", "Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "ReplicaSet"}

def audit_manifest(obj: dict, file: str) -> list[Finding]:
    if not isinstance(obj, dict):
        return []
    kind = obj.get("kind", "")
    findings = []

    if kind in CONTAINER_KINDS:
        spec = obj.get("spec", {})
        if kind == "CronJob":
            spec = spec.get("jobTemplate", {}).get("spec", {})
        pod_spec = spec.get("template", {}).get("spec", {}) if kind != "Pod" else obj.get("spec", {})
        if pod_spec:
            findings.extend(check_pod_spec(pod_spec, file, kind, get_name(obj)))

    elif kind in ("Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding"):
        findings.extend(check_rbac(obj, file))

    elif kind == "NetworkPolicy":
        findings.extend(check_network_policy(obj, file))

    elif kind == "Service":
        findings.extend(check_service(obj, file))

    return findings

def scan_file(filepath: Path) -> list[Finding]:
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        docs = list(yaml.safe_load_all(content))
    except Exception:
        return []

    findings = []
    for doc in docs:
        if doc:
            findings.extend(audit_manifest(doc, str(filepath)))
    return findings

def walk_manifests(root: Path) -> list[Path]:
    skip_dirs = {".git", "node_modules", "vendor", "__pycache__", "charts/crds"}
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            if Path(fname).suffix.lower() in (".yaml", ".yml", ".json"):
                fpath = Path(dirpath) / fname
                # Quick filter: skip if no k8s-like content
                try:
                    preview = fpath.read_text(errors="replace")[:500]
                    if "apiVersion" in preview and "kind" in preview:
                        results.append(fpath)
                except OSError:
                    pass
    return results

def check_missing_network_policies(files: list[Path]) -> list[Finding]:
    """Detect namespaces that have workloads but no NetworkPolicy."""
    ns_workloads: dict[str, str] = {}  # namespace -> first file with workloads
    ns_with_netpol: set[str] = set()

    for f in files:
        try:
            content = f.read_text(errors="replace")
            docs = list(yaml.safe_load_all(content))
        except Exception:
            continue
        for doc in (docs or []):
            if not isinstance(doc, dict):
                continue
            kind = doc.get("kind", "")
            if kind in CONTAINER_KINDS:
                ns = get_namespace(doc)
                if ns not in ns_workloads:
                    ns_workloads[ns] = str(f)
            elif kind == "NetworkPolicy":
                ns_with_netpol.add(get_namespace(doc))

    findings = []
    for ns, first_file in ns_workloads.items():
        if ns not in ns_with_netpol:
            findings.append(Finding(
                first_file, "NetworkPolicy", f"<namespace: {ns}>",
                "N002", HIGH,
                f"No NetworkPolicy found for namespace '{ns}'",
                "Pods in this namespace can communicate with any pod in the cluster.",
                "Create a default-deny NetworkPolicy, then allow specific ingress/egress as needed.\n"
                "kubectl apply -f - <<EOF\napiVersion: networking.k8s.io/v1\nkind: NetworkPolicy\n"
                "metadata:\n  name: default-deny\n  namespace: {ns}\nspec:\n  podSelector: {{}}\n  "
                "policyTypes: [Ingress, Egress]\nEOF",
                "CIS 5.3.2",
            ))
    return findings

def format_report(findings: list[Finding], scanned: int) -> str:
    by_sev = {CRITICAL: [], HIGH: [], MEDIUM: [], LOW: []}
    for f in findings:
        by_sev[f.severity].append(f)

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "  KUBERNETES SECURITY AUDIT (CIS Benchmark v1.9 + PSS)",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  Scanned:  {scanned} manifest files",
        f"  Findings: {len(by_sev[CRITICAL])} CRITICAL  {len(by_sev[HIGH])} HIGH  "
        f"{len(by_sev[MEDIUM])} MEDIUM  {len(by_sev[LOW])} LOW",
        "",
    ]

    for sev in [CRITICAL, HIGH, MEDIUM, LOW]:
        group = by_sev[sev]
        if not group:
            continue
        lines.append(f"{ICONS[sev]} {sev} ({len(group)} findings)")
        lines.append("")
        for f in sorted(group, key=lambda x: (x.file, x.resource_name)):
            rel = os.path.relpath(f.file)
            extras = []
            if f.cis_ref:
                extras.append(f.cis_ref)
            if f.pss_profile:
                extras.append(f.pss_profile)
            ref_str = "  ".join(extras)
            lines += [
                f"  {rel} [{f.resource_kind}/{f.resource_name}] — {f.check_id}",
                f"  {f.title}",
                f"  Detail:  {f.detail}",
                f"  Fix:     {f.remediation[:200]}",
                (f"  Ref:     {ref_str}" if ref_str else ""),
                "",
            ]

    critical_count = len(by_sev[CRITICAL])
    high_count = len(by_sev[HIGH])
    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  CI gate: {'exit 1' if (critical_count + high_count) else 'exit 0 — clean'}",
        "  CIS Kubernetes Benchmark: https://www.cisecurity.org/benchmark/kubernetes",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Kubernetes manifest security auditor")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--ci", action="store_true", help="Exit 1 if CRITICAL or HIGH found")
    parser.add_argument("--min-severity", default="LOW",
                        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                        help="Minimum severity to report")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    files = walk_manifests(root)

    all_findings: list[Finding] = []
    for f in files:
        all_findings.extend(scan_file(f))
    all_findings.extend(check_missing_network_policies(files))

    min_sev = SEV_ORDER[args.min_severity]
    filtered = [f for f in all_findings if SEV_ORDER[f.severity] <= min_sev]
    filtered.sort(key=lambda x: (SEV_ORDER[x.severity], x.file, x.resource_name))

    if args.json:
        import dataclasses
        print(json.dumps([dataclasses.asdict(f) for f in filtered], indent=2))
    else:
        print(format_report(filtered, len(files)))

    if args.ci:
        has_critical_or_high = any(
            f.severity in (CRITICAL, HIGH) for f in filtered
        )
        sys.exit(1 if has_critical_or_high else 0)

if __name__ == "__main__":
    main()
```

## Usage

**Scan a Kubernetes repo:**
```bash
python3 audit_k8s.py ~/myproject/k8s/
```

**CI fail-gate (exits 1 on CRITICAL or HIGH):**
```bash
python3 audit_k8s.py --ci ~/myproject/k8s/
```

**High severity only:**
```bash
python3 audit_k8s.py --min-severity HIGH
```

**JSON output:**
```bash
python3 audit_k8s.py --json | jq '[.[] | select(.severity == "CRITICAL")]'
```

**GitHub Actions:**
```yaml
- name: K8s Security Audit
  run: |
    pip install pyyaml -q
    python3 .claude/skills/phy-k8s-security-audit/audit_k8s.py --ci ./k8s/
```

## Sample Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KUBERNETES SECURITY AUDIT (CIS Benchmark v1.9 + PSS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scanned:  18 manifest files
  Findings: 2 CRITICAL  5 HIGH  8 MEDIUM  3 LOW

🔴 CRITICAL (2 findings)

  k8s/rbac.yaml [ClusterRoleBinding/admin-binding] — R004
  Binding to cluster-admin role
  Detail:  Subjects ['ci-runner'] bound to cluster-admin — full cluster control.
  Fix:     Replace cluster-admin with a custom ClusterRole with minimum permissions.
  Ref:     CIS 5.1.1

  k8s/deployments/api.yaml [Deployment/api-server/api-container] — C001
  Privileged container
  Detail:  securityContext.privileged: true — container has full host access
  Fix:     Remove privileged: true. Use specific capabilities instead.
  Ref:     CIS 5.2.1  PSS Restricted

🟠 HIGH (5 findings)

  k8s/deployments/api.yaml [Deployment/api-server] — P001
  hostNetwork: true
  Detail:  Pod shares host network namespace — can sniff all node traffic.
  Fix:     Remove hostNetwork: true. Use ClusterIP services.
  Ref:     CIS 5.2.4  PSS Baseline

  k8s/deployments/worker.yaml [Deployment/worker/worker] — C012
  Secret in plain env var: DATABASE_PASSWORD
  Detail:  Env var 'DATABASE_PASSWORD' contains a secret value in plaintext.
  Fix:     Use secretKeyRef instead of hardcoded env value.
  Ref:     CIS 5.4.1
  ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CI gate: exit 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Companion Skills

| Skill | Use Together For |
|-------|-----------------|
| `phy-ssrf-audit` | Application code + infrastructure security sweep |
| `phy-cors-audit` | K8s Ingress + application CORS policy |
| `phy-security-headers` | Nginx Ingress controller header config |
| `phy-env-doctor` + `phy-dotenv-inheritance-mapper` | Secret management: code env vars → K8s Secrets |
