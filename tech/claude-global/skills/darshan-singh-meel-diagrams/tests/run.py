"""Tests for the diagram engine and checker. Usage: python tests/run.py [--write]  (--write refreshes the example SVGs;
prints PASS/FAIL per test, exit 1 on any)."""
import sys

sys.dont_write_bytecode = True
import copy, json, os, subprocess, tempfile  # noqa: E401,E402
from pathlib import Path  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))
import check  # noqa: E402
import diagram as d  # noqa: E402

EX = SKILL / "references" / "examples"
FAILS = []


def test(fn):
    try:
        fn()
        print("PASS", fn.__name__)
    except AssertionError as ex:
        FAILS.append(fn.__name__)
        print("FAIL", fn.__name__, "|", ex)
    return fn


def load(name):
    return json.loads((EX / f"{name}.json").read_text(encoding="utf-8"))


def spec(**kw):
    s = {"id": "t", "type": "boxes", "title": "T", "key": "k", "notice": "n",
         "nodes": [{"id": "a", "label": "Alpha"}, {"id": "b", "label": "Beta"}], "edges": [{"from": "a", "to": "b"}]}
    s.update(kw)
    return s


# ---------- core ----------
@test
def wrap_never_cuts_words():
    s = "Validate the incoming basket against stock levels and price lists"
    lines = d.wrap(s, 120)
    assert " ".join(lines) == s, lines
    assert all(d.text_width(x) <= 120 or " " not in x for x in lines), lines


@test
def wrap_breaks_identifiers_after_separators():
    lines = d.wrap("analytics.marts.fct_orders_daily_snapshot", 100, mono=True)
    assert "".join(lines) == "analytics.marts.fct_orders_daily_snapshot", lines
    assert all(x[-1] in "._" for x in lines[:-1]), lines


@test
def size_fits_text():
    n = {"label": "A long label that has to wrap inside the box", "sub": "and a sub line"}
    w, h = d.size(n, 160)
    assert w <= 160 and h > 40, (w, h)


@test
def every_shape_draws():
    for sh in d.SHAPES:
        assert d.shape_svg(sh, 0, 0, 100, 50).startswith("<"), sh


# ---------- examples ----------
@test
def examples_build_clean():
    for f in sorted(EX.glob("*.json")):
        r = d.build(json.loads(f.read_text(encoding="utf-8")))
        assert not r["errors"], (f.name, r["errors"])
        assert r["geometry"]["width"] <= d.MAX_W, f.name
        assert "prefers-color-scheme:dark" in r["svg"] and 'role="img"' in r["svg"], f.name
        assert 'class="dg-frame"' in r["html"] and "Notice:" in r["html"], f.name


@test
def mermaid_frontmatter_first():
    r = d.build(load("order-checkout"))
    assert r["mermaid"].startswith("---\ntitle:"), r["mermaid"][:40]
    assert "flowchart" in r["mermaid"] and "subgraph" in r["mermaid"]
    assert d.build(load("env-matrix"))["mermaid"] is None


@test
def marker_ids_are_scoped():
    svg = d.build(load("order-checkout"))["svg"]
    assert 'id="dg-order-checkout-filled-n"' in svg and "url(#dg-order-checkout-" in svg


# ---------- styles ----------
@test
def dbt_style_kinds_and_columns():
    r = d.build(load("shop-lineage"))
    geo = r["geometry"]
    assert not r["errors"], r["errors"]
    cs = sorted((c["x"], c["x"] + c["w"]) for c in geo["containers"])
    assert len(cs) == 4 and all(a[1] < b[0] for a, b in zip(cs, cs[1:])), cs
    assert "dg-solid" in r["svg"] and {"source", "seed", "model", "exposure"} <= {
        l["text"] for l in geo["labels"] if l["kind"] == "legend"}
    assert "classDef solid_blue" in r["mermaid"] and "6 tests" in r["mermaid"]


@test
def airflow_style_states_and_legend():
    st = d.style_graph(load("nightly-dag"))
    n = {x["id"]: x for x in st["nodes"]}
    assert n["payments"]["tone"] == "red" and n["payments"]["tag"] == "PythonOperator", n["payments"]
    assert n["payments"]["sub"] == "failed" and n["payments"]["strong"]
    assert [e["label"] for e in st["legend"]] == ["failed", "upstream failed", "success"], st["legend"]


@test
def overview_collapses_groups():
    st = d.style_graph(load("dag-overview"))
    n = {x["id"]: x for x in st["nodes"]}
    assert set(n) == {"ingest", "finance", "ml"}, set(n)
    assert n["ingest"]["state"] == "failed" and n["ingest"]["tone"] == "red", n["ingest"]
    assert "1 upstream failed" in n["ingest"]["sub"] and "4 tasks" in n["ingest"]["tag"], n["ingest"]
    es = {(e["from"], e["to"]): e for e in st["edges"]}
    assert set(es) == {("ingest", "finance"), ("ingest", "ml")}, es
    assert es[("ingest", "ml")]["style"] == "dashed" and es[("ingest", "ml")]["label"] == "marts.orders"


@test
def collapse_merges_edge_labels():
    s = spec(groups=[{"id": "g", "label": "G"}], collapse=["g"],
             nodes=[{"id": "a", "label": "A", "group": "g"}, {"id": "b", "label": "B", "group": "g"},
                    {"id": "c", "label": "C"}],
             edges=[{"from": "a", "to": "c", "label": "x"}, {"from": "b", "to": "c", "label": "y"}, {"from": "a", "to": "b"}])
    st = d.style_graph(s)
    assert [(e["from"], e["to"], e.get("label")) for e in st["edges"]] == [("g", "c", "2 links")], st["edges"]
    assert not d.build(s)["errors"]


@test
def auto_group_layout():
    s = load("shop-lineage")
    s["style"] = "plain"
    geo = d.build(s)["geometry"]
    xs = sorted((c["x"], c["x"] + c["w"]) for c in geo["containers"])
    assert all(a[1] < b[0] for a, b in zip(xs, xs[1:])), "sequential groups should become columns"
    par = spec(groups=[{"id": "g1", "label": "one"}, {"id": "g2", "label": "two"}],
               nodes=[{"id": "s", "label": "Start"}, {"id": "a", "label": "A", "group": "g1"},
                      {"id": "b", "label": "B", "group": "g2"}],
               edges=[{"from": "s", "to": "a"}, {"from": "s", "to": "b"}])
    geo = d.build(par)["geometry"]
    ys = sorted((c["y"], c["y"] + c["h"]) for c in geo["containers"])
    assert ys[0][1] < ys[1][0], "parallel groups should stack as bands"


@test
def style_validation():
    errs = d.build(spec(style="fancy", view="all", collapse=["nope"], kinds={"x": "pink"}))["errors"]
    joined = " ".join(errs)
    for frag in ("style 'fancy'", "view 'all'", "collapse: 'nope'", "kinds.x"):
        assert frag in joined, (frag, errs)


@test
def dim_nodes_and_edges():
    s = spec()
    s["nodes"][0]["dim"] = True
    s["edges"][0]["dim"] = True
    svg = d.build(s)["svg"]
    assert svg.count("dg-dim") >= 3, "class on node, edge and in css"


# ---------- build errors ----------
@test
def build_reports_spec_errors():
    r = d.build({"id": "Bad Id", "type": "nope"})
    joined = " ".join(r["errors"])
    for frag in ("id:", "title:", "key:", "notice:"):
        assert frag in joined, (frag, r["errors"])
    assert "unknown" in " ".join(d.build(spec(type="nope"))["errors"])


@test
def too_wide_names_the_fix():
    nodes = [{"id": f"n{i}", "label": f"Step number {i} of the long chain"} for i in range(12)]
    edges = [{"from": f"n{i}", "to": f"n{i + 1}"} for i in range(11)]
    r = d.build(spec(nodes=nodes, edges=edges, direction="LR"))
    assert r["errors"] and "max 1000" in r["errors"][0] and "split" in r["errors"][0], r["errors"]


# ---------- checker ----------
def geo(**kw):
    g = {"id": "g", "width": 400, "height": 300, "connected": True, "nodes": [], "containers": [], "edges": [], "labels": []}
    g.update(kw)
    return g


def nd(i, x, y, w=80, h=40, **kw):
    n = {"id": i, "x": x, "y": y, "w": w, "h": h, "text": i, "shape": "box", "inner": [x + 4, y + 4, w - 8, h - 8],
         "lines": [], "decision": False, "free": False}
    n.update(kw)
    return n


def problems(g):
    return [p for p, _ in check.check(g)[0]]


@test
def checker_finds_overlap_and_width():
    p = problems(geo(width=1200, nodes=[nd("a", 10, 10), nd("b", 50, 20)], edges=[{"from": "a", "to": "b", "points": [[0, 0], [1, 1]]}]))
    assert "boxes overlap" in p and "canvas too wide" in p, p


@test
def checker_finds_arrow_through_box():
    g = geo(nodes=[nd("a", 10, 100), nd("b", 300, 100), nd("c", 150, 100)],
            edges=[{"from": "a", "to": "b", "points": [[90, 120], [300, 120]], "label": None}])
    assert "arrow through box" in problems(g)


@test
def checker_finds_label_problems():
    g = geo(nodes=[nd("a", 10, 10), nd("b", 300, 10), nd("c", 10, 200), nd("e", 300, 200)],
            containers=[{"id": "grp", "x": 0, "y": 150, "w": 200, "h": 120, "kind": "group", "text": "grp", "members": ["c"]}],
            edges=[{"from": "a", "to": "b", "points": [[90, 30], [300, 30]], "label": 0},
                   {"from": "c", "to": "e", "points": [[90, 220], [300, 220]], "label": None}],
            labels=[{"text": "on c-e", "x": 150, "y": 212, "w": 40, "h": 16, "edge": 0, "kind": "edge"}])
    p = problems(g)
    assert "label on foreign line" in p and "label across group border" not in p, p
    g["labels"][0].update(x=180, y=160)
    assert "label across group border" in problems(g), problems(g)


@test
def checker_finds_text_overflow_and_decision():
    n = nd("q", 10, 10, shape="diamond", decision=True,
           lines=[{"text": "too long", "x": 0, "y": 15, "w": 200, "h": 16}])
    p = problems(geo(nodes=[n, nd("b", 200, 10)], edges=[{"from": "q", "to": "b", "points": [[90, 30], [200, 30]]}]))
    assert "text overflows box" in p and "decision with fewer than 2 exits" in p, p


@test
def checker_warns_unconnected():
    _, w = check.check(geo(nodes=[nd("a", 10, 10)]))
    assert w and w[0][0] == "unconnected node", w
    _, w = check.check(geo(connected=False, nodes=[nd("a", 10, 10)]))
    assert not w


@test
def straddles_rule():
    assert check.straddles((95, 10, 20, 10), (0, 0, 100, 100))
    assert not check.straddles((10, 10, 20, 10), (0, 0, 100, 100))
    assert not check.straddles((200, 10, 20, 10), (0, 0, 100, 100))


# ---------- registry / discovery ----------
FAMILY = '''
import diagram as engine


def mm(spec):
    return engine.mermaid_head(spec, "flowchart LR")[0]


def svg(spec, core):
    c = core.canvas(spec)
    for i, it in enumerate(spec["items"]):
        core.node(c, {"id": it, "label": it}, 16 + i * 140, 16, 120, 40)
    return core.finish(c)


def check_items(spec):
    return [] if spec.get("items") else ["items: at least one"]


def layout_error(spec, core):
    raise core.LayoutError("too many items: split it")


TYPES = {"stripe-test": {"svg": svg, "validate": check_items, "doc": "test type"},
         "mm-test": {"svg": svg, "mermaid": mm},
         "boom-test": {"svg": layout_error},
         "boxes": {"svg": svg}}
'''


@test
def registry_discovers_family_modules():
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "types_test.py").write_text(FAMILY, encoding="utf-8")
        (Path(td) / "types_broken.py").write_text("TYPES = {", encoding="utf-8")
        old = os.environ.get("DIAGRAM_TYPES")
        os.environ["DIAGRAM_TYPES"] = td
        try:
            reg = d.registry(refresh=True)
            assert "stripe-test" in reg and reg["stripe-test"]["mermaid"]({}) is None
            assert reg["boxes"]["family"] == "base", "a family must not replace a built-in"
            errs = " ".join(d.REG_ERRORS)
            assert "types_broken.py" in errs and "already defined" in errs, d.REG_ERRORS
            r = d.build({"id": "s", "type": "stripe-test", "title": "T", "key": "k", "notice": "n", "items": ["a", "b"]})
            assert not r["errors"] and r["mermaid"] is None, r["errors"]
            r = d.build({"id": "s", "type": "stripe-test", "title": "T", "key": "k", "notice": "n"})
            assert r["errors"] == ["items: at least one"], r["errors"]
            r = d.build({"id": "s", "type": "mm-test", "title": "T", "key": "k", "notice": "n", "items": ["a"]})
            assert r["mermaid"] == "---" and sys.modules["diagram"] is d, r
            r = d.build({"id": "s", "type": "boom-test", "title": "T", "key": "k", "notice": "n"})
            assert r["errors"] == ["layout: too many items: split it"], r["errors"]
        finally:
            if old is None:
                os.environ.pop("DIAGRAM_TYPES", None)
            else:
                os.environ["DIAGRAM_TYPES"] = old
            d.registry(refresh=True)


@test
def sibling_glob_points_at_family_folders():
    pattern = d.HERE.parent.parent / "darshan-singh-meel-diagrams-x" / "scripts" / "types_x.py"
    assert pattern.match("*/darshan-singh-meel-diagrams-*/scripts/types_*.py")


# ---------- routing options ----------
def ports_into(geo_, nid):
    return {tuple(round(v) for v in e["points"][-1]) for e in geo_["edges"] if e["to"] == nid}


@test
def trunk_by_default_spread_on_request():
    s = spec(nodes=[{"id": i, "label": i} for i in ("a", "b", "c")], edges=[{"from": "a", "to": "c"}, {"from": "b", "to": "c"}])
    g = d.build(s)["geometry"]
    assert len(ports_into(g, "c")) == 1, "arrows into one side share a port"
    body, g2 = d.graph(s, spread=True)
    assert len(ports_into(g2, "c")) == 2, "spread=True: one port per arrow"
    s["edges"][0]["own_port"] = True
    assert len(ports_into(d.build(s)["geometry"], "c")) == 2, "own_port on one edge splits that side"


@test
def pill_and_hexagon_ports_spread_onto_outline():
    for shape in ("pill", "hexagon"):
        s = spec(nodes=[{"id": "a", "label": "A"}, {"id": "b", "label": "B"},
                        {"id": "c", "label": "Target", "shape": shape, "sub": "two lines of text"}],
                 edges=[{"from": "a", "to": "c", "label": "x"}, {"from": "b", "to": "c", "label": "y"}])
        body, g = d.graph(s, spread=True)
        assert len(ports_into(g, "c")) == 2, shape
        assert not problems(g), (shape, problems(g))


@test
def obstacle_and_clear_are_public():
    c = d.canvas(spec())
    d.obstacle(c, 0, 0, 10, 10)
    d.node(c, {"id": "n", "label": "N"}, 50, 50, 80, 30, clear=3)
    assert c["obst"][0][4] == d.CLEAR and c["obst"][-1][4] == 3, c["obst"]


@test
def column_frames_leave_room_for_labels():
    s = spec(group_layout="columns", groups=[{"id": "g1", "label": "one"}, {"id": "g2", "label": "two"}],
             nodes=[{"id": "a", "label": "A", "group": "g1"}, {"id": "b", "label": "B", "group": "g2"}],
             edges=[{"from": "a", "to": "b", "label": "a fairly long arrow label"}])
    r = d.build(s)
    assert not r["errors"], r["errors"]


@test
def arrows_avoid_frame_borders():
    for name in ("order-checkout",):
        g = d.build(load(name))["geometry"]
        for e in g["edges"]:
            for p, q in zip(e["points"], e["points"][1:]):
                for f in g["containers"]:
                    if abs(p[1] - q[1]) < .5 and abs(p[0] - q[0]) > 8:
                        assert all(abs(p[1] - y) >= 4 for y in (f["y"], f["y"] + f["h"])), (name, e["from"], e["to"])


@test
def example_svgs_are_current():
    for f in sorted(EX.glob("*.json")):
        r = d.build(json.loads(f.read_text(encoding="utf-8")))
        if "--write" in sys.argv:
            f.with_suffix(".svg").write_text(r["svg"], encoding="utf-8")
        assert f.with_suffix(".svg").read_text(encoding="utf-8").strip() == r["svg"].strip(),             f"{f.stem}.svg is stale: python tests/run.py --write"


@test
def skill_table_matches_registry():
    import re
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    rows = text[text.index("## Pick the type"):text.index("## Graph style")]
    listed = {m for line in rows.splitlines() if line.startswith("| ") and ("`" in line.split("|")[2] or "this skill" in line) for m in re.findall(r"`([a-z0-9-]+)`\*?", line.split("|")[3])}
    reg = set(d.registry())
    assert listed == reg, f"in SKILL.md only: {sorted(listed - reg)} · registered only: {sorted(reg - listed)}"


# ---------- CLI ----------
@test
def cli_writes_outputs():
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        r = subprocess.run([sys.executable, str(SKILL / "scripts" / "diagram.py"), str(EX / "shop-lineage.json"),
                            "-o", str(t / "a.svg"), "--mermaid", str(t / "a.mmd"), "--page", str(t / "a.html"),
                            "--geometry", str(t / "a.json")], capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0 and r.stdout.strip().startswith("OK shop-lineage"), r.stdout + r.stderr
        assert (t / "a.svg").read_text(encoding="utf-8").startswith("<svg")
        assert (t / "a.html").read_text(encoding="utf-8").startswith("<!doctype html>")
        r = subprocess.run([sys.executable, str(SKILL / "scripts" / "check.py"), str(t / "a.json")],
                           capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stdout
        bad = copy.deepcopy(load("order-checkout"))
        bad.pop("notice")
        (t / "bad.json").write_text(json.dumps(bad), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SKILL / "scripts" / "diagram.py"), str(t / "bad.json"), "-o", str(t / "b.svg")],
                           capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 1 and "notice: required" in r.stdout, r.stdout
        r = subprocess.run([sys.executable, str(SKILL / "scripts" / "diagram.py"), "--list"],
                           capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0 and "boxes" in r.stdout and "layers" in r.stdout, r.stdout


if __name__ == "__main__":
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    sys.exit(1 if FAILS else 0)
