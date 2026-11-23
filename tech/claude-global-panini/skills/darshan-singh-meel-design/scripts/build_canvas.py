"""Build one self-contained canvas.html from the direction files of a round.
Usage: python build_canvas.py designs/<name>/round-N [--tokens designs/<name>/tokens.css] [--images DIR[:Label]]... [--before DIR]
       [--screens runs,run-detail] [--out canvas.html]
Reads round-N/*.html (canvas*.html skipped); body attributes data-direction, data-name, data-screen, data-pitch; inlines tokens.css into
each frame; adds a guard so links and forms inside a frame never navigate; one image column per --images folder (--before = Before);
a System frame from the tokens; rows = screens in flow order (--screens, else first appearance). Writes round-N/canvas.html."""
import argparse
import base64
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LINK = re.compile(r"""<link[^>]+href=["'][^"']*tokens\.css["'][^>]*>""", re.I)
ATTR = re.compile(r"""data-(direction|name|screen|pitch)=(?:"([^"]*)"|'([^']*)')""")
TOKEN = re.compile(r"--([\w-]+)\s*:\s*([^;]+);")
GUARD = ("<script>/* canvas guard: a frame never navigates or opens windows */"
         "addEventListener('click',e=>{if(e.target.closest('a[href]'))e.preventDefault();},true);"
         "addEventListener('submit',e=>e.preventDefault(),true);window.open=()=>null;</script>")


def attrs_of(text):
    body = re.search(r"<body[^>]*>", text, re.I)
    return {m[1]: m[2] if m[2] is not None else m[3] for m in ATTR.finditer(body[0])} if body else {}


def read_frame(path, tokens):
    text = path.read_text(encoding="utf-8")
    a = attrs_of(text)
    if tokens:
        text = LINK.sub(lambda m: "<style>" + tokens + "</style>", text, count=1)
    text = re.sub(r"</body>", GUARD + "</body>", text, count=1, flags=re.I) if re.search(r"</body>", text, re.I) else text + GUARD
    return {"key": a.get("direction") or path.stem.split("-")[0].upper(), "name": a.get("name", path.stem), "screen": a.get("screen", ""),
            "pitch": a.get("pitch", ""), "file": path.name, "html": text}


def system_frame(tokens):
    found = {m[1]: m[2].strip() for m in TOKEN.finditer(re.sub(r"/\*.*?\*/", "", tokens, flags=re.S).split("}", 1)[0]) if m[2].strip()}
    colors = [n for n in found if re.search(r"\b(bg|surface|ink|border|accent|ok|warn|danger|info|focus)\b", n) and not n.endswith("-h")]
    sw = "".join(f'<div class="sw"><i style="background:var(--{n})"></i><code>--{n}</code><small>{html.escape(found[n])}</small></div>' for n in colors)
    ty = "".join(f'<p style="font-size:var(--{n});margin:0 0 8px"><code>--{n}</code> The quick brown fox jumps over 13 lazy dogs</p>'
                 for n in found if n.startswith("text-"))
    sp = "".join(f'<div class="sp"><code>--{n}</code><b style="width:var(--{n})"></b></div>' for n in found if n.startswith("space-"))
    rd = "".join(f'<div class="rd" style="border-radius:var(--{n})"><code>--{n}</code></div>' for n in found if n.startswith("radius"))
    sh = "".join(f'<div class="rd" style="box-shadow:var(--{n});border:0"><code>--{n}</code></div>' for n in found if n.startswith("shadow"))
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>System</title><style>{tokens}
body{{margin:0;padding:24px;background:var(--bg);color:var(--ink);font:var(--font-size-base,15px)/1.5 var(--font-sans,system-ui)}}
h2{{font-size:var(--text-sm,13px);text-transform:uppercase;letter-spacing:.04em;color:var(--ink-2);margin:24px 0 8px}}
.sw{{display:flex;align-items:center;gap:10px;margin:4px 0}}.sw i{{width:28px;height:28px;border-radius:6px;border:1px solid var(--border)}}
.sw small{{color:var(--ink-2)}}.sp{{display:flex;gap:10px;align-items:center;margin:4px 0}}.sp b{{height:12px;background:var(--accent)}}
.rd{{display:inline-block;width:110px;height:56px;border:1px solid var(--border);background:var(--surface);margin:4px;padding:6px}}
code{{font:12px var(--font-mono,monospace)}}</style></head><body><h1 style="margin:0;font-size:var(--text-xl,22px)">Tokens</h1>
<h2>Colour</h2>{sw}<h2>Type</h2>{ty}<h2>Spacing</h2>{sp}<h2>Radius</h2>{rd}<h2>Elevation</h2>{sh}</body></html>"""
    return {"key": "System", "name": "Tokens", "screen": "", "pitch": "generated from tokens.css", "file": "tokens.css", "html": page}


def image_frames(folder, label):
    out, seen = [], set()
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        screen = p.stem if p.stem not in seen else f"{p.stem} ({p.suffix[1:]})"
        seen.add(p.stem)
        mime = "image/jpeg" if p.suffix.lower() in (".jpg", ".jpeg") else f"image/{p.suffix[1:].lower()}"
        page = (f'<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;background:#888">'
                f'<img src="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}" alt="{html.escape(label)}: {html.escape(p.stem)}" style="width:100%;display:block"></body></html>')
        out.append({"key": label, "name": label, "screen": screen, "pitch": "", "file": p.name, "html": page})
    return out


def order_screens(frames, wanted):
    """Flow order: --screens first, then first appearance; every column gets a slot per screen (a placeholder when missing)."""
    seen = {s.lower(): s for s in wanted if s}
    for f in frames:
        if f["screen"] and f["file"].endswith(".html"):
            seen.setdefault(f["screen"].lower(), f["screen"])  # the direction's spelling wins over an image's file stem
    for f in frames:
        if f["screen"]:
            seen.setdefault(f["screen"].lower(), f["screen"])
    if not seen:
        return frames
    out = []
    for key in dict.fromkeys(f["key"] for f in frames):
        col = [f for f in frames if f["key"] == key]
        if key == "System" or not any(f["screen"] for f in col):
            out += col
            continue
        for low, name in seen.items():
            hit = [dict(f, screen=name) for f in col if f["screen"].lower() == low]
            out += hit or [{"key": key, "name": col[0]["name"], "screen": name, "pitch": col[0]["pitch"], "file": "", "html": "", "missing": True}]
    return out


def embed(obj):
    """JSON safe inside <script>: no '<' (so no '</script>'), no U+2028/2029."""
    return json.dumps(obj).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round")
    ap.add_argument("--tokens")
    ap.add_argument("--images", action="append", default=[], help="DIR[:Label], repeatable; one image column each")
    ap.add_argument("--before", help="shorthand for --images DIR:Before")
    ap.add_argument("--screens", default="", help="comma-separated screen names in flow order")
    ap.add_argument("--out", default="canvas.html")
    a = ap.parse_args()
    rnd = pathlib.Path(a.round)
    if not rnd.is_dir():
        sys.exit(f"ERROR not a folder: {rnd}")
    tokens_path = pathlib.Path(a.tokens) if a.tokens else rnd.parent / "tokens.css"
    tokens = tokens_path.read_text(encoding="utf-8") if tokens_path.is_file() else ""
    frames = [read_frame(p, tokens) for p in sorted(rnd.glob("*.html")) if not p.name.startswith("canvas") and p.name != a.out]
    if not frames:
        sys.exit(f"ERROR no direction files (<key>-<slug>.html) in {rnd}")
    images = [f"{a.before}:Before"] if a.before else []
    for spec in images + a.images:
        folder, _, label = spec.rpartition(":") if re.search(r":[^\\/:]+$", spec) else (spec, "", "")
        folder = pathlib.Path(folder or spec)
        if not folder.is_dir():
            sys.exit(f"ERROR image folder not found: {folder}")
        frames = image_frames(folder, label or folder.name) + frames
    frames = order_screens(frames, a.screens.split(","))
    if tokens:
        frames.append(system_frame(tokens))
    tpl = (HERE / "canvas_template.html").read_text(encoding="utf-8")
    page = tpl.replace("/*TITLE*/", html.escape(f"{rnd.parent.name} · {rnd.name}")).replace("/*FRAMES*/", embed(frames))
    (rnd / a.out).write_text(page, encoding="utf-8")
    cols = len(dict.fromkeys(f["key"] for f in frames))
    print(f"canvas: {(rnd / a.out).as_posix()} · {len(frames)} frames in {cols} columns · tokens: {'yes' if tokens else 'none'}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
