/// <reference types="vitest/config" />
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

const HERE = import.meta.dirname;

// sha256 over every file git tracks in this folder (path, then bytes with CRLF read as LF, so a Windows
// checkout hashes the same), first 16 hex. tools/check_dist.py computes the same: a source change
// without a rebuild fails the check.
export function sourceHash(): string {
  const files = execFileSync("git", ["ls-files", "-z", "."], { cwd: HERE, encoding: "utf8" })
    .split("\0").filter(Boolean).sort();
  if (!files.length) throw new Error("git tracks no files here: commit (or git add) the frontend source, then build");
  const h = createHash("sha256");
  for (const f of files) {
    h.update(f + "\0", "utf8");
    // latin1 maps each byte to one char and back, so CRLF is replaced without decoding.
    h.update(Buffer.from(readFileSync(resolve(HERE, f)).toString("latin1").replace(/\r\n/g, "\n"), "latin1"));
    h.update("\0", "utf8");
  }
  return h.digest("hex").slice(0, 16);
}

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

// Moves the bundled JS and CSS into index.html, so dist/ is one self-contained file: it works through
// declare_component(path=...) and as a components.html string, with no static file serving and no CDN.
function inlineAll(): Plugin {
  return {
    name: "inline-all",
    apply: "build",
    enforce: "post",
    generateBundle(_options, bundle) {
      const page = bundle["index.html"];
      if (!page || page.type !== "asset") throw new Error("no index.html in the build");
      let html = String(page.source);
      for (const [name, file] of Object.entries(bundle)) {
        const tag = new RegExp(`<(?:script|link)[^>]*?(?:src|href)="[^"]*?${escapeRe(name)}"[^>]*>(?:</script>)?`);
        if (file.type === "chunk" && !file.isEntry) {
          // A lazy chunk would stay a separate file the inlined page can't load.
          throw new Error(`second JS chunk ${name}: remove dynamic import() from the widget`);
        }
        if (file.type === "chunk") {
          // A "</script" inside a string would end the inline tag early.
          html = html.replace(tag, () => `<script type="module">${file.code.replace(/<\/script/gi, "<\\/script")}</script>`);
        } else if (name.endsWith(".css")) {
          html = html.replace(tag, () => `<style>${String(file.source)}</style>`);
        } else {
          continue;
        }
        delete bundle[name];
      }
      page.source = html.replace("</head>", `  <meta name="source-hash" content="${sourceHash()}">\n</head>`);
    },
  };
}

export default defineConfig({
  plugins: [react(), inlineAll()],
  // Relative paths: Streamlit serves a component under its own sub-path, never at "/".
  base: "./",
  build: {
    outDir: "../dist",
    emptyOutDir: true,
    sourcemap: false,
    cssCodeSplit: false,
    // Fonts and images become data: URIs inside the CSS, so nothing is fetched at runtime.
    assetsInlineLimit: 100_000_000,
    modulePreload: { polyfill: false },
  },
  // threads: the default forks pool can time out starting its workers on Windows.
  test: { environment: "jsdom", pool: "threads" },
});
