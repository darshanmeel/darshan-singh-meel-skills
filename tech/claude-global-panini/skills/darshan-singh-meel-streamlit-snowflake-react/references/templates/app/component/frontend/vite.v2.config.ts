// Container runtime only: src/v2.tsx as one ES module, CSS inside it, for st.components.v2.component.
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import { sourceHash } from "./vite.config";

// The same stamp as dist/index.html, as a first-line banner; tools/check_dist.py compares it.
function hashBanner(): Plugin {
  return {
    name: "source-hash-banner",
    apply: "build",
    enforce: "post",
    generateBundle(_options, bundle) {
      const chunks = Object.values(bundle).filter((f) => f.type === "chunk");
      if (chunks.length !== 1) throw new Error(`want one JS file, got ${chunks.length}: remove dynamic import()`);
      for (const c of chunks) c.code = `/*! source-hash: ${sourceHash()} */
${c.code}`;
    },
  };
}

export default defineConfig({
  plugins: [react(), hashBanner()],
  // Library mode leaves process.env in React's code; the browser has no process.
  define: { "process.env.NODE_ENV": JSON.stringify("production") },
  build: {
    outDir: "../dist-v2",
    emptyOutDir: true,
    sourcemap: false,
    assetsInlineLimit: 100_000_000,
    lib: { entry: "src/v2.tsx", formats: ["es"], fileName: () => "widget.js" },
  },
});
