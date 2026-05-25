#!/usr/bin/env python3
"""ERPClaw OS — Dependency Resolver

Topological sort on module dependency graph from module_registry.json.
Resolves installation order, detects circular dependencies, and checks
for prefix collisions between modules.
"""
import json
import os
from collections import defaultdict


def load_registry(registry_path=None):
    """Load module registry JSON.

    Args:
        registry_path: Path to module_registry.json. If None, uses default location.

    Returns:
        dict of {module_name: module_info}
    """
    if registry_path is None:
        # Default: relative to erpclaw scripts directory
        registry_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "module_registry.json",
        )

    if not os.path.isfile(registry_path):
        return {}

    with open(registry_path, "r") as f:
        data = json.load(f)

    return data.get("modules", {})


def resolve_install_order(modules, registry=None, registry_path=None):
    """Resolve installation order via topological sort.

    Args:
        modules: list of module names to install
        registry: dict of {module_name: module_info} (optional, loaded from path if None)
        registry_path: path to module_registry.json

    Returns:
        dict with:
        - order: list of module names in install order
        - added_dependencies: modules added to satisfy dependencies
        - errors: list of error strings
    """
    if registry is None:
        registry = load_registry(registry_path)

    modules_set = set(modules)
    errors = []

    # 1. Expand dependencies: add all required modules
    all_needed = set()
    added_deps = set()

    def expand(mod_name):
        if mod_name in all_needed:
            return
        all_needed.add(mod_name)
        if mod_name not in registry:
            errors.append(f"Module '{mod_name}' not found in registry")
            return
        for dep in registry[mod_name].get("requires", []):
            if dep not in modules_set:
                added_deps.add(dep)
            expand(dep)

    for m in modules:
        expand(m)

    if errors:
        return {"order": [], "added_dependencies": list(added_deps), "errors": errors}

    # 2. Topological sort (Kahn's algorithm)
    # Build adjacency and in-degree
    in_degree = defaultdict(int)
    graph = defaultdict(list)

    for mod_name in all_needed:
        if mod_name not in in_degree:
            in_degree[mod_name] = 0
        for dep in registry.get(mod_name, {}).get("requires", []):
            if dep in all_needed:
                graph[dep].append(mod_name)
                in_degree[mod_name] += 1

    # Start with modules that have no dependencies
    queue = sorted([m for m in all_needed if in_degree[m] == 0])
    order = []

    while queue:
        node = queue.pop(0)
        order.append(node)
        for neighbor in sorted(graph[node]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(all_needed):
        # Circular dependency detected
        remaining = all_needed - set(order)
        errors.append(f"Circular dependency detected among: {sorted(remaining)}")
        return {"order": order, "added_dependencies": list(added_deps), "errors": errors}

    return {
        "order": order,
        "added_dependencies": sorted(added_deps),
        "errors": [],
    }


def detect_circular_deps(modules, registry=None, registry_path=None):
    """Detect circular dependencies in a set of modules.

    Args:
        modules: list of module names
        registry: dict of {module_name: module_info}
        registry_path: path to module_registry.json

    Returns:
        list of cycles found (each cycle is a list of module names).
        Empty list = no cycles.
    """
    if registry is None:
        registry = load_registry(registry_path)

    # DFS-based cycle detection
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {m: WHITE for m in modules if m in registry}
    cycles = []

    def dfs(node, path):
        color[node] = GRAY
        path.append(node)

        for dep in registry.get(node, {}).get("requires", []):
            if dep not in color:
                continue
            if color[dep] == GRAY:
                # Found cycle
                cycle_start = path.index(dep)
                cycles.append(path[cycle_start:] + [dep])
            elif color[dep] == WHITE:
                dfs(dep, path)

        path.pop()
        color[node] = BLACK

    for m in modules:
        if m in color and color[m] == WHITE:
            dfs(m, [])

    return cycles


def detect_prefix_collisions(modules, registry=None, registry_path=None):
    """Detect action prefix collisions between modules.

    Two modules with the same prefix would have overlapping action names.

    Args:
        modules: list of module names
        registry: dict of {module_name: module_info}
        registry_path: path to module_registry.json

    Returns:
        list of collision dicts: [{prefix, modules: [mod1, mod2]}]
    """
    if registry is None:
        registry = load_registry(registry_path)

    # Derive prefix from module name
    prefix_map = defaultdict(list)
    for mod_name in modules:
        if mod_name not in registry:
            continue
        # Common prefix derivation: module name or first part
        # e.g., healthclaw → health, educlaw → educ, retailclaw → retail
        prefix = mod_name.replace("claw", "").replace("-", "_").split("_")[0]
        if prefix:
            prefix_map[prefix].append(mod_name)

    collisions = []
    for prefix, mods in prefix_map.items():
        if len(mods) > 1:
            collisions.append({
                "prefix": prefix,
                "modules": mods,
            })

    return collisions
