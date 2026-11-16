"""dbt manifest.json -> dbt-lineage spec (structure only: names, types, folders, refs, test counts; no data).
Usage: python dbt_manifest.py target/manifest.json -o spec.json [--id billing-lineage] [--select "+fct_mrr"]
                              [--view overview] [--layers staging,intermediate,marts]
Layer = the folder under models/ (fqn[1]); sources, seeds, snapshots, semantic models, metrics, saved queries and
exposures get their own layer.
Write the title, key and notice into the spec before building it: the build refuses an empty notice."""
import argparse
import json
import sys
from pathlib import Path

KEEP = ("model", "seed", "snapshot", "source", "exposure", "semantic_model", "metric", "saved_query")
PREFIX = {"exposure": "exp_", "semantic_model": "sm_", "metric": "metric_", "saved_query": "sq_"}  # may share a model's name
LAYER = {"semantic_model": "semantic", "metric": "metrics", "saved_query": "saved_queries"}


def node_id(uid, n):
    rt = n.get("resource_type")
    if rt == "source":
        return f"src_{n.get('source_name')}_{n.get('name')}"
    return PREFIX.get(rt, "") + n.get("name", uid)


def layer(n):
    rt = n.get("resource_type")
    if rt in LAYER:
        return LAYER[rt]
    if rt in ("source", "seed", "snapshot", "exposure"):
        return rt + "s"
    fqn = n.get("fqn") or []
    return fqn[1] if len(fqn) > 2 else "models"


def to_spec(manifest, sid="dbt-lineage", select=None, view=None, layers=None):
    nodes = dict(manifest.get("nodes") or {})
    every = dict(nodes)
    for key in ("sources", "exposures", "semantic_models", "metrics", "saved_queries"):
        every.update(manifest.get(key) or {})
    tests = {}
    for n in nodes.values():
        if n.get("resource_type") == "test":
            for t in [n.get("attached_node")] if n.get("attached_node") else (n.get("depends_on") or {}).get("nodes", [])[-1:]:
                tests[t] = tests.get(t, 0) + 1
    out = []
    for uid, n in every.items():
        rt = n.get("resource_type")
        if rt not in KEEP:
            continue
        d = {"id": node_id(uid, n), "resource_type": rt, "layer": layer(n),
             "depends_on": [node_id(x, every[x]) for x in (n.get("depends_on") or {}).get("nodes", []) if x in every]}
        if rt == "source":
            d["label"] = f"{n.get('source_name')}.{n.get('name')}"
        if rt in PREFIX:
            d["label"] = n.get("label") or n.get("name")
        mat = (n.get("config") or {}).get("materialized")
        if rt == "model" and mat:
            d["materialized"] = mat
        if tests.get(uid):
            d["tests"] = tests[uid]
        out.append(d)
    spec = {"id": sid, "type": "dbt-lineage", "title": f"{manifest.get('metadata', {}).get('project_name') or 'dbt'} lineage",
            "key": ("Box = layer (folder or resource type) · colour = main resource type · counts per type below"
                    if view == "overview" else
                    "Pill colour = resource type (legend) · frame = folder layer · tag = type and materialization · "
                    "sub = data tests"),
            "notice": "", "nodes": sorted(out, key=lambda d: d["id"])}
    if layers:
        names = ["sources", "seeds", "snapshots"] + layers + ["semantic", "metrics", "saved_queries", "exposures"]
        spec["layers"] = [{"id": x, "label": x} for x in names if any(d["layer"] == x for d in out)]
    if select:
        spec["select"] = select
    if view:
        spec["view"] = view
    return spec


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("manifest")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--id", default="dbt-lineage")
    ap.add_argument("--select", help="dbt graph operators on node names, e.g. '+fct_orders' or 'stg_orders+'")
    ap.add_argument("--view", choices=("detail", "overview"))
    ap.add_argument("--layers", help="model folders in flow order, comma-separated")
    a = ap.parse_args(argv)
    m = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    spec = to_spec(m, a.id, a.select, a.view, a.layers.split(",") if a.layers else None)
    Path(a.out).write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK {len(spec['nodes'])} nodes -> {a.out} | write title, key and notice before building")
    return 0


if __name__ == "__main__":
    sys.exit(main())
