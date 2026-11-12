import { createRoot } from "react-dom/client";
import { onRender, setHeight, setValue, type Theme } from "./bridge";
import { Widget } from "./Widget";
import "./widget.css";

type Args = { label?: string; options?: string[]; value?: string | null; theme?: Partial<Theme> };

// Same names as the variables components v2 provides, so widget.css serves both mounts.
const VARS: Record<string, string> = {
  primaryColor: "--st-primary-color",
  backgroundColor: "--st-background-color",
  secondaryBackgroundColor: "--st-secondary-background-color",
  textColor: "--st-text-color",
  font: "--st-font",
};

// The app's theme as CSS variables, so the widget follows light and dark mode with the app.
function applyTheme(theme?: Partial<Theme>) {
  for (const [key, cssVar] of Object.entries(VARS)) {
    const value = theme?.[key as keyof Theme];
    if (value) document.documentElement.style.setProperty(cssVar, value);
  }
}

const root = createRoot(document.getElementById("root")!);

function draw(a: Args, disabled: boolean, interactive: boolean) {
  root.render(
    <Widget
      label={a.label ?? ""}
      options={a.options ?? []}
      value={a.value ?? null}
      disabled={disabled}
      onPick={interactive ? setValue : undefined}
    />,
  );
}

const inline: Args = JSON.parse(document.getElementById("args")?.textContent || "{}");
if (Object.keys(inline).length) {
  // components.html mount: the args are in the page and nothing goes back to Python.
  applyTheme(inline.theme);
  draw(inline, false, false);
} else {
  onRender((r) => {
    applyTheme(r.theme);
    draw(r.args as Args, r.disabled, true);
  });
  new ResizeObserver(() => setHeight(document.documentElement.scrollHeight)).observe(document.body);
}
