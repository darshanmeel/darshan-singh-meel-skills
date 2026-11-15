"""Offline dbt project facts from manifest.json / run_results.json - structure only, never compiled SQL or data.

Usage:
  dbt_inventory.py <manifest.json> health [--pk-tests unique,unique_combination_of_columns,<own>]
                   | impact <model> | upstream <model> | joins <model> | column-users <model> <column>
                   | relations [--select-prefix <path>] | macros | macro-users <macro>
  dbt_inventory.py <run_results.json> timing [--type model|test] [--top N] [--order duration|started]
"""
import json
import re
import sys
from collections import deque

INTROSPECTIVE = re.compile(r"\b(run_query|get_column_values|get_columns_in_relation|dbt_utils\.star|get_relations_by_pattern)\s*\(")
HARDCODED = re.compile(r"\b(?:from|join)\s+(?!\{)([A-Za-z_][\w$]*\.[A-Za-z_][\w$]*\.[A-Za-z_][\w$]*)", re.I)
PK_TESTS = {"unique", "unique_combination_of_columns"}
COMMENTS = re.compile(r"\{#.*?#\}|/\*.*?\*/|--[^\n]*", re.S)
REF = re.compile(r"\b(from|join)\s+\{\{\s*ref\(\s*(?:['\"]\w+['\"]\s*,\s*)?['\"](\w+)['\"][^}]*\}\}\s*(?:as\s+)?(?!(?:on|using|left|right|inner|full|cross|natural|outer|join|where|group|qualify|order|union|having|limit|window)\b)(\w+)?", re.I)
STOP = re.compile(r"(left|right|inner|full|cross|natural|outer|join|where|group|qualify|order|union|having|limit|window)\b", re.I)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def models(m):
    return {k: n for k, n in m["nodes"].items() if n["resource_type"] == "model"}


def find(m, name):
    """unique_id for a model name, 'name.v1' or a full unique_id."""
    for k, n in models(m).items():
        if name in (k, n["name"], f'{n["name"]}.v{n.get("version")}') or k.endswith("." + name):
            return k
    sys.exit(f"model not found: {name}")


def tests_by_model(m):
    out = {}
    for n in m["nodes"].values():
        if n["resource_type"] != "test":
            continue
        for parent in n["depends_on"]["nodes"]:
            out.setdefault(parent, []).append(n)
    return out


def test_kind(t):
    return (t.get("test_metadata") or {}).get("name", "singular")


def health(m, pk=PK_TESTS):
    ms, tbm, child = models(m), tests_by_model(m), m.get("child_map", {})
    exposed = {p for e in m.get("exposures", {}).values() for p in e["depends_on"]["nodes"]}
    r = {k: [] for k in ["untested_models", "no_pk_test", "sources_without_freshness", "source_outside_staging",
                         "orphan_models", "many_parents", "incremental_no_unique_key", "incremental_no_on_schema_change",
                         "public_no_contract", "no_description", "no_group", "warn_tests", "hardcoded_relations",
                         "introspective_macros", "deprecated_configs", "seeds_without_column_types"]}
    for k, n in ms.items():
        if n["package_name"] != m["metadata"].get("project_name", n["package_name"]):
            continue
        c, name, path = n["config"], n["name"], n["original_file_path"]
        tests = tbm.get(k, [])
        if not tests and c.get("materialized") != "ephemeral":
            r["untested_models"].append(name)
        if not any(test_kind(t) in pk for t in tests):
            r["no_pk_test"].append(name)
        parents = n["depends_on"]["nodes"]
        if any(p.startswith("source.") for p in parents) and "staging" not in path:
            r["source_outside_staging"].append(name)
        kids = [x for x in child.get(k, []) if not x.startswith(("test.", "unit_test."))]
        if not kids and k not in exposed:
            r["orphan_models"].append(name)
        if len(parents) > 8:
            r["many_parents"].append(f"{name} ({len(parents)})")
        if c.get("materialized") == "incremental":
            strategy = c.get("incremental_strategy") or "default"
            if not c.get("unique_key") and strategy not in ("append", "microbatch", "insert_overwrite"):
                r["incremental_no_unique_key"].append(name)
            if c.get("on_schema_change", "ignore") == "ignore":
                r["incremental_no_on_schema_change"].append(name)
        if n.get("access") == "public" and not (c.get("contract") or {}).get("enforced"):
            r["public_no_contract"].append(name)
        if not n.get("description"):
            r["no_description"].append(name)
        if "marts" in path and not n.get("group"):
            r["no_group"].append(name)
        code = COMMENTS.sub(" ", n.get("raw_code", ""))
        if HARDCODED.search(code):
            r["hardcoded_relations"].append(name)
        if INTROSPECTIVE.search(code):
            r["introspective_macros"].append(name)
    for n in m["nodes"].values():
        if n["resource_type"] == "test" and n["config"].get("severity", "error").lower() == "warn":
            r["warn_tests"].append(n["name"])
        if n["resource_type"] == "snapshot" and "invalidate_hard_deletes" in n["config"]:
            r["deprecated_configs"].append(f'{n["name"]}: invalidate_hard_deletes -> hard_deletes')
        if n["resource_type"] == "seed" and not n["config"].get("column_types"):
            r["seeds_without_column_types"].append(n["name"])
    for s in m.get("sources", {}).values():
        f = s.get("freshness") or (s.get("config") or {}).get("freshness") or {}
        if not (f.get("warn_after") or {}).get("count") and not (f.get("error_after") or {}).get("count"):
            r["sources_without_freshness"].append(f'{s["source_name"]}.{s["name"]}')
    fan = sorted(((len([x for x in child.get(k, []) if x.startswith("model.")]), n["name"]) for k, n in ms.items()), reverse=True)
    r["fan_out"] = [f"{name} ({c})" for c, name in fan[:10] if c]
    print(f"models: {len(ms)}  tests: {sum(1 for n in m['nodes'].values() if n['resource_type'] == 'test')}  "
          f"sources: {len(m.get('sources', {}))}  exposures: {len(m.get('exposures', {}))}")
    for k, v in r.items():
        print(f"{k}: {len(v)}" + ("" if not v else "\n  " + "\n  ".join(sorted(v)[:50])))
    return r


def walk(start, graph):
    seen, q, out = {start}, deque([(start, 0)]), []
    while q:
        node, d = q.popleft()
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                out.append((d + 1, nxt))
                q.append((nxt, d + 1))
    return out


def impact(m, name):
    out = walk(find(m, name), m["child_map"])
    for d, node in out:
        print(f"{d}  {node}")
    return out


def upstream(m, name):
    out = walk(find(m, name), m["parent_map"])
    for d, node in out:
        print(f"{d}  {node}")
    return out


def on_clause(code, pos):
    """Text of an ON condition from pos: up to a keyword or an unbalanced ')' at depth 0."""
    depth, i = 0, pos
    while i < len(code):
        ch = code[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth == 0:
                break
            depth -= 1
        elif depth == 0 and STOP.match(code, i) and (i == 0 or not (code[i - 1].isalnum() or code[i - 1] in "_.")):
            break
        i += 1
    return " ".join(code[pos:i].split())


def ref_joins(code):
    """(keyword, ref name, alias, condition) per ref after from/join in raw_code."""
    out = []
    for r in REF.finditer(code):
        kw, ref, alias = r.group(1).lower(), r.group(2), r.group(3)
        rest = code[r.end():]
        cond = ""
        m = re.match(r"\s*on\b", rest, re.I)
        if m:
            cond = on_clause(rest, m.end())
        else:
            m = re.match(r"\s*using\s*\(([^)]*)\)", rest, re.I)
            if m:
                cond = "using (" + " ".join(m.group(1).split()) + ")"
        out.append((kw, ref, alias or ref, cond))
    return out


def joins(m, name):
    """Models joining <name>, with alias and ON / USING text; children with no parsed join are listed too."""
    uid = find(m, name)
    target = m["nodes"][uid]["name"]
    out = []
    for k, n in models(m).items():
        refs = ref_joins(COMMENTS.sub(" ", n.get("raw_code", "")))
        mine = [r for r in refs if r[1] == target]
        rows = [(n["name"], r[2], r[3]) for r in mine if r[0] == "join" and r[3]]
        for _, _, alias, _ in (r for r in mine if r[0] == "from"):
            rows += [(n["name"], alias, c) for kw, ref, _, c in refs
                     if kw == "join" and ref != target and c and (c.startswith("using") or re.search(rf"\b{re.escape(alias)}\.", c))]
        out += rows
    found = {r[0] for r in out}
    for c in m.get("child_map", {}).get(uid, []):
        if c.startswith("model.") and m["nodes"][c]["name"] not in found:
            out.append((m["nodes"][c]["name"], "", f"depends on {target} but no join parsed"))
    for row in out:
        print(" | ".join(row))
    return out


def column_users(m, name, column):
    """Models reading <column> of <name> (word match in raw_code), select * pass-throughs, and tests on it."""
    word = re.compile(rf"\b{re.escape(column)}\b", re.I)
    star = re.compile(r"select\s+(?:distinct\s+)?(?:\w+\.)?\*|\.\*\s*(?:,|from)|\bstar\s*\(", re.I)
    start, out, seen, q = find(m, name), [], set(), deque()
    q.append(start)
    while q:
        node = q.popleft()
        for c in m.get("child_map", {}).get(node, []):
            n = m["nodes"].get(c)
            if not n or c in seen:
                continue
            seen.add(c)
            if n["resource_type"] == "test":
                if (n.get("column_name") or "").lower() == column.lower():
                    out.append((n["name"], "test on the column"))
                continue
            code = COMMENTS.sub(" ", n.get("raw_code", ""))
            if word.search(code):
                out.append((n["name"], "uses the column"))
            elif star.search(code):
                out.append((n["name"], "select * (passes it on)"))
                q.append(c)
    for row in out:
        print(" | ".join(row))
    return out


def relations(m, prefix=None):
    out = [n["relation_name"].replace('"', "").replace("`", "").lower() for n in models(m).values()
           if n.get("relation_name") and n["config"].get("materialized") != "ephemeral"
           and (not prefix or n["original_file_path"].startswith(prefix))]
    print("\n".join(sorted(out)))
    return out


def unused_macros(m):
    used = {x for n in list(m["nodes"].values()) + list(m.get("macros", {}).values())
            for x in (n.get("depends_on") or {}).get("macros", [])}
    project = m["metadata"].get("project_name")
    out = sorted(k for k, mc in m.get("macros", {}).items()
                 if mc["package_name"] == project and k not in used and not mc["name"].startswith(("test_", "generate_")))
    print("\n".join(out))
    return out


def macro_users(m, macro):
    out = sorted(k for k, n in m["nodes"].items()
                 if any(x == macro or x.endswith("." + macro) for x in n["depends_on"].get("macros", [])))
    print("\n".join(out))
    return out


def timing(rr, kind=None, top=20, order="duration"):
    rows = []
    for r in rr["results"]:
        if kind and not r["unique_id"].startswith(kind + "."):
            continue
        started = min((t.get("started_at") or "" for t in r.get("timing") or []), default="")
        rows.append((r.get("execution_time") or 0, r["unique_id"], r["status"], r.get("failures"), started))
    if order == "started":
        rows.sort(key=lambda x: (x[4] or "~", x[1]))   # no timing → last
    else:
        rows.sort(reverse=True)
    print(f"elapsed_time: {rr.get('elapsed_time')}  nodes: {len(rows)}  "
          f"errors: {sum(1 for r in rows if r[2] in ('error', 'fail'))}")
    for secs, uid, status, failures, started in rows[:top]:
        print(f"{started[:19]:19}  {secs:8.1f}s  {status:8}  {uid}" + (f"  failures={failures}" if failures else ""))
    return rows


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    data, cmd, rest = load(argv[1]), argv[2], argv[3:]
    opt = lambda k, d=None: rest[rest.index(k) + 1] if k in rest else d
    if cmd == "health":
        health(data, set(opt("--pk-tests").split(",")) if opt("--pk-tests") else PK_TESTS)
    elif cmd in ("impact", "upstream", "joins", "macro-users"):
        {"impact": impact, "upstream": upstream, "joins": joins, "macro-users": macro_users}[cmd](data, rest[0])
    elif cmd == "relations":
        relations(data, opt("--select-prefix"))
    elif cmd == "macros":
        unused_macros(data)
    elif cmd == "column-users":
        column_users(data, rest[0], rest[1])
    elif cmd == "timing":
        timing(data, opt("--type"), int(opt("--top", 20)), opt("--order", "duration"))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
