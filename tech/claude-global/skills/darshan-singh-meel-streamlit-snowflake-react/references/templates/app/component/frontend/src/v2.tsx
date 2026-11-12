// Container runtime: the same Widget as a components v2 entry (st.components.v2.component).
import { createRoot, type Root } from "react-dom/client";
import { Widget } from "./Widget";
import css from "./widget.css?inline";

type Data = { label?: string; options?: string[]; value?: string | null };
type Component = {
  data: Data;
  parentElement: HTMLElement;
  setStateValue: (key: string, value: unknown) => void;
};

// Streamlit calls the default export on every rerun with the same parentElement: render, don't remount.
const roots = new WeakMap<HTMLElement, Root>();

export default function (component: Component) {
  const { data, parentElement, setStateValue } = component;
  let root = roots.get(parentElement);
  if (!root) {
    const style = document.createElement("style");
    style.textContent = css;
    const mount = document.createElement("div");
    parentElement.append(style, mount);
    root = createRoot(mount);
    roots.set(parentElement, root);
  }
  root.render(
    <Widget
      label={data.label ?? ""}
      options={data.options ?? []}
      value={data.value ?? null}
      onPick={(o) => setStateValue("value", o)}
    />,
  );
}
