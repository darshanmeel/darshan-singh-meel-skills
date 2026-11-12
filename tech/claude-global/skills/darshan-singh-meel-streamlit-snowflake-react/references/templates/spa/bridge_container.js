// Container runtime: a v2 component. startApp(), concatenated above this file, wraps the React build.
export default function (component) {
  const { data, setTriggerValue } = component;
  // Called on every rerun: keep one bridge.
  const b = (globalThis.__spaBridge ||= makeBridge());
  b.send = setTriggerValue;
  b.receive(data?.out);
  b.schedule();
  if (b.started) return;
  b.started = true;
  window.APP_HOSTED = true;
  try { startApp(); } catch (e) { b.note(`the app did not start: ${e.message}`); }
}
