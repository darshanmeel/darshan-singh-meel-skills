import { afterEach, describe, expect, it, vi } from "vitest";
import { onRender, setHeight, setValue } from "./bridge";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("bridge", () => {
  it("sends values and heights as Streamlit messages", () => {
    const post = vi.spyOn(window.parent, "postMessage").mockImplementation(() => {});
    setValue("Daily");
    setHeight(120);
    expect(post).toHaveBeenNthCalledWith(1, { isStreamlitMessage: true, type: "streamlit:setComponentValue", value: "Daily", dataType: "json" }, "*");
    expect(post).toHaveBeenNthCalledWith(2, { isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: 120 }, "*");
  });

  it("says it is ready and draws only render messages from the host page", () => {
    const post = vi.spyOn(window.parent, "postMessage").mockImplementation(() => {});
    const draw = vi.fn();
    onRender(draw);
    expect(post).toHaveBeenCalledWith({ isStreamlitMessage: true, type: "streamlit:componentReady", apiVersion: 1 }, "*");
    window.dispatchEvent(new MessageEvent("message", { data: { type: "streamlit:render", args: { a: 1 } }, source: null }));
    expect(draw).not.toHaveBeenCalled();
    window.dispatchEvent(new MessageEvent("message", { data: { type: "streamlit:render", args: { a: 1 }, disabled: false }, source: window.parent }));
    expect(draw).toHaveBeenCalledWith({ args: { a: 1 }, disabled: false, theme: undefined });
  });
});
