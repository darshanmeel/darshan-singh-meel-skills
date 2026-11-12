// Warehouse runtime: a v1 component in its own frame (frame/index.html), speaking Streamlit's messages.
const toStreamlit = (type, fields) => window.parent.postMessage({ isStreamlitMessage: true, type, ...fields }, "*");
const bridge = makeBridge();
bridge.send = (_name, value) => toStreamlit("streamlit:setComponentValue", { value, dataType: "json" });

function fitFrame() {
  let height = 900;
  try { height = window.parent.innerHeight || height; } catch (e) { /* another origin: keep the default */ }
  toStreamlit("streamlit:setFrameHeight", { height });
}

window.addEventListener("message", (event) => {
  if (event.source !== window.parent || event.data?.type !== "streamlit:render") return;
  bridge.receive((event.data.args || {}).out);
  bridge.schedule();
  if (bridge.started) return;
  // The app starts only now, so fetch is patched and a sender exists before its first request.
  bridge.started = true;
  window.APP_HOSTED = true;
  const script = document.createElement("script");
  script.type = "module";
  script.src = document.body.dataset.bundle;
  script.onerror = () => bridge.note("the app bundle did not load");
  document.body.appendChild(script);
  fitFrame();
});
window.addEventListener("resize", fitFrame);
toStreamlit("streamlit:componentReady", { apiVersion: 1 });
