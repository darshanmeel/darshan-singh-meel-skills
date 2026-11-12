// Streamlit components v1 messages (the same ones streamlit-component-lib sends), without the lib and
// its Arrow dependency. Args are JSON only; use the lib if DataFrames must cross as Arrow tables.
export type Theme = {
  base: string;
  primaryColor: string;
  backgroundColor: string;
  secondaryBackgroundColor: string;
  textColor: string;
  font: string;
};
export type Render = { args: Record<string, unknown>; disabled: boolean; theme?: Theme };

function send(type: string, data: Record<string, unknown> = {}) {
  window.parent.postMessage({ isStreamlitMessage: true, type, ...data }, "*");
}

export function onRender(draw: (r: Render) => void) {
  window.addEventListener("message", (e: MessageEvent) => {
    // Only the Streamlit page that hosts this iframe may drive it.
    if (e.source !== window.parent || e.data?.type !== "streamlit:render") return;
    draw({ args: e.data.args ?? {}, disabled: Boolean(e.data.disabled), theme: e.data.theme });
  });
  send("streamlit:componentReady", { apiVersion: 1 });
}

// Every call reruns the Python script: send on commit (click, Enter, blur), never per keystroke.
export const setValue = (value: unknown) => send("streamlit:setComponentValue", { value, dataType: "json" });

export const setHeight = (height: number) => send("streamlit:setFrameHeight", { height });
