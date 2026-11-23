"""Regression tests for the design skill's scripts. Usage: python tests/run.py [--no-browser]
Builds fixtures in a temp folder, runs the scripts, checks their output. Playwright + Chrome/Edge for the canvas and screenshot tests."""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

SKILL = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
PY = [sys.executable, "-I"]
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
failed = []


def run(script, *args):
    r = subprocess.run(PY + [str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True, encoding="utf-8", env=ENV)
    return r.returncode, r.stdout + r.stderr


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else f"\n     {detail[:600]}"))
    if not cond:
        failed.append(name)


def page(direction="A", name="Alpha", screen="Runs", body="<main><h1>Runs</h1><a href='#'>x</a></main>", extra=""):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>t</title>
<link rel="stylesheet" href="../tokens.css"><style>body{{background:var(--bg);color:var(--ink)}} a:hover{{color:var(--accent)}} a:focus-visible{{outline:2px solid var(--focus)}}
@media (prefers-reduced-motion: reduce){{*{{transition:none}}}}{extra}</style></head>
<body data-direction="{direction}" data-name="{name}" data-screen="{screen}">{body}</body></html>"""


def fixture(tmp):
    proj = tmp / "proj"
    d = proj / "designs" / "x"
    (d / "round-1").mkdir(parents=True)
    (proj / ".gitignore").write_text("# designs are local\n/designs/\n", encoding="utf-8")
    (d / "brief.md").write_text("# Brief: x\n", encoding="utf-8")
    shutil.copy(SKILL / "references" / "templates" / "tokens.css", d / "tokens.css")
    return proj, d


def test_checker(tmp):
    proj, d = fixture(tmp)
    rnd = d / "round-1"
    (rnd / "a-one.html").write_text(page(), encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: clean fixture passes", code == 0 and "0 FAIL" in out, out)
    # M10 false positives
    (rnd / "a-one.html").write_text(page(body="<main><h1>Runs</h1><svg xmlns=\"http://www.w3.org/2000/svg\"></svg><p>one bar each, todo list, Password: required, Token: existing-file</p></main>"), encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: xmlns, 'bar', 'todo', 'Password: required' are not findings", "0 FAIL" in out, out)
    # M10 false negatives
    (rnd / "a-one.html").write_text(page(body="<main><h1>Runs</h1><p>C:/work/x and /Users/Bob and 10.0.0.5</p></main>"), encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: C:/work, /Users/Bob, private IP are FAIL", out.count("FAIL") >= 3 and "absolute path" in out and "private address" in out, out)
    (rnd / "a-one.html").write_text(page(body="<main><h1>Runs</h1><a href='http://localhost.evil.com/x'>x</a><script>var s='</script>';</script></main>"), encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: localhost.evil.com is an external URL", "external URL" in out, out)
    # M8 literals
    (rnd / "a-one.html").write_text(page(body="<main><h1>Runs</h1><svg><rect fill=\"#ff0000\"/></svg><i style='color:red'></i></main>",
                                         extra=" p{color:lab(50% 0 0)} h1{font-size:18px;border-radius:4px;transition:all 300ms}"), encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: named colour, lab(), SVG fill are FAIL; px and ms are WARN", "colour literals" in out and re.search(r"colour literals.*?e\.g\. .*(red|lab|fill)", out)
          and "size or duration literals" in out, out)
    # M10 structural twin with a changed heading
    (rnd / "a-one.html").write_text(page(), encoding="utf-8")
    (rnd / "b-two.html").write_text(page("B", "Beta", body="<main><h1>Other heading</h1><a href='#'>x</a></main>"), encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: duplicate direction with one changed heading is warned", "same element structure" in out, out)
    (rnd / "b-two.html").unlink()
    # M7 calc/none and a brace in a comment; H3 dark block, alpha, -text/-soft pairs
    tk = (d / "tokens.css").read_text(encoding="utf-8")
    (d / "tokens.css").write_text(tk.replace(":root {", ":root { /* a } b */") + "\n:root[data-theme=\"dark\"] { --ink: #333; --ok-text: calc(1px); --focus: none; }\n", encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: [data-theme=dark] block overrides dark values", "dark: --ink on --bg" in out, out)
    check("checker: calc() and none are reported, not a crash", "Traceback" not in out and "--ok-text not parsed" in out and "--focus not parsed" in out, out)
    (d / "tokens.css").write_text(tk.replace("--warn-text:   light-dark(oklch(40% 0.12 65)", "--warn-text:   light-dark(oklch(76% 0.12 65)")
                                  .replace("--accent-soft: light-dark(oklch(94% 0.05 var(--accent-h))", "--accent-soft: light-dark(oklch(40% 0.05 var(--accent-h) / 0.5)"), encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: -text on -soft pair is checked", "--warn-text on --warn-soft" in out, out)
    check("checker: alpha is composited (ink on accent-soft stays a pass)", "--accent-soft not parsed" not in out and "Traceback" not in out, out)
    shutil.copy(SKILL / "references" / "templates" / "tokens.css", d / "tokens.css")
    # M9 final: extra screen, tokens drift, Maps to under its own heading, one-line handoff, imports
    fin = d / "final"
    fin.mkdir()
    (fin / "index.html").write_text(page().replace("../tokens.css", "tokens.css"), encoding="utf-8")
    (fin / "run.html").write_text(page(screen="Run", body="<main><h1>Run</h1><i style='color:#123456'></i></main>").replace("../tokens.css", "tokens.css"), encoding="utf-8")
    (fin / "tokens.css").write_text((d / "tokens.css").read_text(encoding="utf-8") + "\n/* drift */\n", encoding="utf-8")
    (fin / "spec.md").write_text("# Spec\n## Layout\n## Components\n| a | b | Maps to existing |\n## Behaviour\n## States\n## Responsive\n## Accessibility\n## Copy\n## Acceptance checks\n## Maps to\n`src/nothere.tsx`\n", encoding="utf-8")
    (fin / "handoff-prompt.md").write_text("Refine the design.\n", encoding="utf-8")
    (d / "imports").mkdir()
    (d / "imports" / "ext.html").write_text("<script src='https://cdn.example.com/x.js'></script>", encoding="utf-8")
    code, out = run("check_design.py", d, "--final")
    check("checker: every final page is checked", "run.html | 1 colour literals" in out, out)
    check("checker: tokens drift root vs final is FAIL", "differs from designs/<name>/tokens.css" in out, out)
    check("checker: Maps to path under its own heading is reported", "nothere.tsx not found" in out, out)
    check("checker: one-line handoff is FAIL", "not self-contained" in out, out)
    check("checker: imports are listed as untrusted", "untrusted import: 1 external URL" in out, out)
    check("checker: states.html missing is WARN", "states.html missing" in out, out)
    # M10 gitignore: comment only, and running from inside the folder
    (proj / ".gitignore").write_text("# /designs/ would go here\n", encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: /designs/ inside a comment does not count", "add '/designs/'" in out, out)
    (proj / ".gitignore").write_text("/designs/\n", encoding="utf-8")
    r = subprocess.run(PY + [str(SCRIPTS / "check_design.py"), "."], cwd=d, capture_output=True, text=True, encoding="utf-8", env=ENV)
    check("checker: '.' resolves the project root", "add '/designs/'" not in r.stdout, r.stdout)
    # M6 apostrophe in attributes
    (rnd / "a-one.html").write_text(page(name="Dave's pick"), encoding="utf-8")
    code, out = run("check_design.py", d)
    check("checker: apostrophe in data-name is fine", "body needs data-direction" not in out, out)


def test_canvas(tmp, browser):
    proj, d = fixture(tmp)
    rnd = d / "round-1"
    (rnd / "a-runs.html").write_text(page(name="Dave's pick", body="<main><h1>Runs</h1><a href='#' id='lnk'>go</a><form><button>send</button></form><!-- </script> --></main>"), encoding="utf-8")
    (rnd / "b-runs.html").write_text(page("B", "Beta", body="<main><h1>B</h1><table><tr><td>1</td></tr></table></main>"), encoding="utf-8")
    (rnd / "b-run.html").write_text(page("B", "Beta", "Run", body="<main><h1>B run</h1></main>"), encoding="utf-8")
    tk = (d / "tokens.css").read_text(encoding="utf-8").replace("ui-monospace", '"C:\\\\Fonts\\\\x", ui-monospace')
    (d / "tokens.css").write_text(tk, encoding="utf-8")
    before = d / "before"
    before.mkdir()
    (before / "runs.png").write_bytes(bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d4944415478da63f8cfc0f01f0005000201 ".replace(" ", "") + "0e1e2b4d0000000049454e44ae426082"))
    code, out = run("build_canvas.py", rnd, "--before", before, "--screens", "Runs,Run")
    check("canvas: builds with backslash tokens and a </script> in a frame (H1, M5)", code == 0 and "frames" in out, out)
    html = (rnd / "canvas.html").read_text(encoding="utf-8")
    check("canvas: no raw </script> inside the frame JSON", html.count("</script>") == 1 and "\\u003c/script>" in html, "")
    check("canvas: apostrophe attributes parsed (M6)", "Dave's pick" in html, "")
    check("canvas: Before column and a placeholder for A's missing Run screen (L3)", '"key": "Before"' in html and '"missing": true' in html, "")
    if not browser:
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1280, "height": 800})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:100]))
        pg.goto((rnd / "canvas.html").as_uri())
        pg.wait_for_timeout(600)
        check("canvas: no page errors, 4 columns, System hidden by default (M2)", not errs and pg.locator(".col").count() == 4
              and pg.locator('.col[data-key="System"]').evaluate("e => e.hidden"), str(errs))
        f = [x for x in pg.frames if x.locator("#lnk").count()][0]
        f.locator("#lnk").click()
        f.locator("button").click()
        pg.wait_for_timeout(300)
        check("canvas: in-frame link and form do not navigate (M1)", f.url == "about:srcdoc" and f.locator("#lnk").count() == 1, f.url)
        s = pg.locator("#knobs input").first
        s.evaluate("e => { e.value = 20; e.dispatchEvent(new Event('input')); }")
        pg.locator("#reset").click()
        check("canvas: Reset restores the slider labels (M3)", pg.locator("#knobs output").first.inner_text() == "250", pg.locator("#knobs output").first.inner_text())
        pg.locator(".pick").first.click()
        pg.locator("#export").click()
        check("canvas: Pick lands in the export (L4)", "Picked: A" in pg.locator("#exportText").input_value(), "")
        pg.locator("#close").click()
        pg.locator('#columns input').nth(1).uncheck()
        pg.wait_for_timeout(100)
        check("canvas: hiding a column changes Fit (M2)", "%" in pg.locator("#status").inner_text() and pg.locator(".col[hidden]").count() == 2, pg.locator("#status").inner_text())
        pg.set_viewport_size({"width": 390, "height": 844})
        pg.wait_for_timeout(200)
        check("canvas: no page overflow at 390 (L4)", pg.evaluate("document.documentElement.scrollWidth") <= 390, "")
        check("canvas: no nested button in a link (L4)", pg.locator("a button").count() == 0, "")
        b.close()


def test_screenshot(tmp, browser):
    if not browser:
        return
    proj, d = fixture(tmp)
    rnd = d / "round-1"
    (rnd / "a-one.html").write_text(page(body="<main><h1>Runs</h1><input placeholder='type here' aria-label='q'><input type='checkbox' aria-label='c'></main>", extra=" ::placeholder{color:#a0a0a0}"), encoding="utf-8")
    (rnd / "canvas.html").write_text("<html><body>canvas</body></html>", encoding="utf-8")
    (rnd / "refresh.html").write_text("<meta http-equiv='refresh' content='0;url=https://example.com/'><body><h1>r</h1></body>", encoding="utf-8")
    out_dir = tmp / "shots"
    import http.server
    import threading
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=str(rnd), **k))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    code, out = run("screenshot.py", f"http://localhost:{port}/a-one.html?v=1", "http://localhost.evil.invalid/x", f"http://localhost:{port}@evil.invalid/",
                    "nothere.html", rnd, "--out", out_dir, "--viewports", "390x844", "--themes", "light", "--hover", "input")
    srv.shutdown()
    shots = [p for p in out_dir.glob("*.png") if p.stat().st_size > 0]
    check("screenshot: loopback stem sanitized, file written (H2)", any(p.name.startswith("a-one.html-v_1") for p in shots), out)
    check("screenshot: lookalike hosts refused, missing target reported, exit 2 (M4, L8)", out.count("SKIP") == 3 and code == 2, out)
    check("screenshot: folder skips canvas.html, meta refresh is a FAIL not a crash (L5, M4)", "canvas" not in "".join(p.name for p in shots) and "FAIL refresh" in out and "Traceback" not in out, out)
    check("screenshot: placeholder contrast and accent-color reported (L7)", "placeholder under 4.5:1" in out and "accent-color auto" in out, out)
    check("screenshot: distinct hover targets shot (L6)", any("hover2" in p.name for p in shots), out)


def main():
    browser = "--no-browser" not in sys.argv
    if browser:
        try:
            import playwright  # noqa: F401
        except ImportError:
            browser = False
            print("skip browser tests: Playwright not installed")
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        test_checker(tmp / "a")
        test_canvas(tmp / "b", browser)
        test_screenshot(tmp / "c", browser)
    print(f"{len(failed)} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
