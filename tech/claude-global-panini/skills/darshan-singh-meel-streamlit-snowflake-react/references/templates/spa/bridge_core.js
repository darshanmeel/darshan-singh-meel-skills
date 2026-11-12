// Routes the React build's fetch("/api/...") to Python through a Streamlit component: the browser can't
// reach a port on Snowflake's side. bridge_frame.js (v1) or bridge_container.js (v2) connects it.
const BATCH_DELAY_MS = 15; // collect the requests one render fires into one rerun
const MAX_BATCH = 8; // Python also caps a batch by bytes and sends back what didn't fit as retry
const NO_ANSWER_MS = 300000;
const NO_BODY = new Set([101, 204, 205, 304]);

function makeBridge() {
  const b = { queue: [], pending: new Map(), sent: [], inflight: null, nextId: 1, nextBatch: 1,
              timer: null, send: null, started: false, problems: [] };

  b.note = (text) => {
    b.problems.push(text);
    const box = document.getElementById("bridge-checks");
    if (box) box.textContent = b.problems.slice(-30).join("\n");
  };

  b.settle = (id, response) => {
    const p = b.pending.get(id);
    b.pending.delete(id);
    if (p) response ? p.resolve(response) : p.reject(new Error("The app did not answer. Reload the page."));
  };

  // One batch in flight: every send reruns the Python script.
  b.flush = () => {
    b.timer = null;
    if (b.inflight !== null || !b.queue.length || !b.send) return;
    const id = b.nextBatch++;
    const requests = (b.sent = b.queue.splice(0, MAX_BATCH));
    b.inflight = id;
    b.send("batch", { id, requests });
    setTimeout(() => {
      if (b.inflight !== id) return;
      b.note(`batch ${id}: no answer in ${NO_ANSWER_MS / 1000} s`);
      requests.forEach((r) => b.settle(r.id, null));
      b.inflight = null;
      b.schedule();
    }, NO_ANSWER_MS);
  };
  b.schedule = () => { if (!b.timer) b.timer = setTimeout(b.flush, BATCH_DELAY_MS); };

  b.receive = (out) => {
    if (!out || out.batch_id !== b.inflight) return; // a rerender with an old answer
    b.inflight = null;
    for (const r of out.responses) {
      if (r.status >= 500 || r.status === 413) b.note(`HTTP ${r.status} on ${r.path}`);
      b.settle(r.id, new Response(NO_BODY.has(r.status) ? null : r.body, { status: r.status, headers: r.headers }));
    }
    const retry = new Set(out.retry || []);
    b.queue.unshift(...b.sent.filter((r) => retry.has(r.id)));
    b.schedule();
  };

  const realFetch = window.fetch.bind(window);
  // String URLs, string bodies and plain-object headers only: the request travels as JSON.
  window.fetch = (input, init = {}) => {
    if (typeof input !== "string" || !input.startsWith("/api/")) return realFetch(input, init);
    return new Promise((resolve, reject) => {
      const id = b.nextId++;
      b.pending.set(id, { resolve, reject });
      b.queue.push({ id, method: (init.method || "GET").toUpperCase(), path: input,
                     body: init.body ?? null, headers: init.headers ?? null });
      b.schedule();
    });
  };

  document.addEventListener("securitypolicyviolation", (e) => b.note(`blocked by the security policy: ${e.violatedDirective} ${e.blockedURI}`));
  window.addEventListener("error", (e) => b.note(`script error: ${e.message}`));
  return b;
}
